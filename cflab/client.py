"""
Cloudflare API Client for Workers AI & Edge Cloud Platform.
Zero mandatory external dependencies; pure Python standard library.
"""

import json
import time
import base64
import urllib.request
import urllib.error
from typing import Generator, List, Dict, Any, Optional, Tuple, Union

from .models import ModelInfo, FALLBACK_CF_MODELS, parse_model_from_cf_api

CF_API_BASE = "https://api.cloudflare.com/client/v4"

class CloudflareClient:
    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id.strip()
        self.api_token = api_token.strip()
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "Cloudflare-API-Lab/1.0"
        }

    # -------------------------------------------------------------------------
    # Authentication & Account Verification
    # -------------------------------------------------------------------------

    def check_auth(self) -> Dict[str, Any]:
        """Verify API token and retrieve account info."""
        url = f"{CF_API_BASE}/accounts/{self.account_id}"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("success"):
                    res = data.get("result", {})
                    return {
                        "valid": True,
                        "account_id": self.account_id,
                        "account_name": res.get("name", "Cloudflare Account"),
                        "type": res.get("type", "standard"),
                        "created_on": res.get("created_on", ""),
                        "error": None
                    }
                else:
                    err_msg = ", ".join(e.get("message", "") for e in data.get("errors", []))
                    return {"valid": False, "error": err_msg or "Failed to verify account"}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                j = json.loads(err_body)
                msg = ", ".join(er.get("message", "") for er in j.get("errors", [])) or err_body
            except Exception:
                msg = err_body
            return {"valid": False, "error": f"HTTP {e.code}: {msg}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    # -------------------------------------------------------------------------
    # Workers AI: Model Discovery
    # -------------------------------------------------------------------------

    def get_models(self, task: Optional[str] = None) -> List[ModelInfo]:
        """
        Dynamically query Cloudflare for all available Workers AI models.
        Falls back to curated offline catalog if network fails.
        """
        url = f"{CF_API_BASE}/accounts/{self.account_id}/ai/models/search"
        if task:
            url += f"?task={urllib.parse.quote(task)}"

        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("success"):
                    raw_models = data.get("result", [])
                    models = [parse_model_from_cf_api(m) for m in raw_models]
                    if task:
                        models = [m for m in models if m.task.lower() == task.lower()]
                    return sorted(models, key=lambda m: (m.task, m.name))
        except Exception:
            pass

        # Fallback to local catalog
        models = [
            ModelInfo(
                id=m["id"],
                name=m["name"],
                task=m["task"],
                description=m["description"],
                context_length=m.get("context_length", 4096),
                input_modalities=m.get("input_modalities", ["text"]),
                output_modalities=m.get("output_modalities", ["text"])
            )
            for m in FALLBACK_CF_MODELS
        ]
        if task:
            models = [m for m in models if m.task.lower() == task.lower()]
        return models

    # -------------------------------------------------------------------------
    # Workers AI: Text Generation & Streaming Chat
    # -------------------------------------------------------------------------

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Generator[str, None, Dict[str, Any]]:
        """
        Stream chat response token by token via Server-Sent Events (SSE).
        Yields chunk text deltas. Returns summary metadata upon completion.
        """
        url = f"{CF_API_BASE}/accounts/{self.account_id}/ai/run/{model}"
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        req = urllib.request.Request(
            url,
            headers=self.headers,
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )

        start_time = time.time()
        total_content = ""
        total_chunks = 0

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if not line_str or line_str == "data: [DONE]":
                        continue
                    if line_str.startswith("data: "):
                        try:
                            chunk = json.loads(line_str[6:])
                            delta = chunk.get("response", "")
                            if delta:
                                total_content += delta
                                total_chunks += 1
                                yield delta
                        except Exception:
                            continue
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                j = json.loads(err_body)
                msg = ", ".join(er.get("message", "") for er in j.get("errors", [])) or err_body
            except Exception:
                msg = err_body
            yield f"\n[Workers AI Error {e.code}: {msg}]"
        except Exception as e:
            yield f"\n[Connection Error: {str(e)}]"

        duration = time.time() - start_time
        return {
            "content": total_content,
            "duration": duration,
            "chunks": total_chunks
        }

    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Non-streaming text completion.
        Returns: (response_text, elapsed_seconds, error_message)
        """
        url = f"{CF_API_BASE}/accounts/{self.account_id}/ai/run/{model}"
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        req = urllib.request.Request(
            url,
            headers=self.headers,
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elapsed = time.time() - start_time
                if data.get("success"):
                    res = data.get("result", {})
                    content = res.get("response", "")
                    return content, elapsed, None
                err_msg = ", ".join(e.get("message", "") for e in data.get("errors", []))
                return None, elapsed, err_msg
        except urllib.error.HTTPError as e:
            elapsed = time.time() - start_time
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                j = json.loads(err_body)
                msg = ", ".join(er.get("message", "") for er in j.get("errors", [])) or err_body
            except Exception:
                msg = err_body
            return None, elapsed, f"HTTP {e.code}: {msg}"
        except Exception as e:
            elapsed = time.time() - start_time
            return None, elapsed, str(e)

    # -------------------------------------------------------------------------
    # Workers AI: Text-to-Image Studio
    # -------------------------------------------------------------------------

    def generate_image(
        self,
        prompt: str,
        model: str = "@cf/black-forest-labs/flux-1-schnell",
        steps: int = 4,
        guidance: float = 7.5,
        width: Optional[int] = None,
        height: Optional[int] = None,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> Tuple[Optional[bytes], float, Optional[str]]:
        """
        Generate image from prompt using Cloudflare Workers AI.
        Supports FLUX.1-schnell, SDXL Lightning, DreamShaper, etc.
        Returns: (raw_image_bytes, elapsed_seconds, error_message)
        """
        url = f"{CF_API_BASE}/accounts/{self.account_id}/ai/run/{model}"
        payload: Dict[str, Any] = {"prompt": prompt}

        # Model specific parameters
        if "flux" in model.lower():
            payload["steps"] = min(8, max(1, steps))
        else:
            payload["num_steps"] = steps
            payload["guidance"] = guidance
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt

        if width:
            payload["width"] = width
        if height:
            payload["height"] = height
        if seed is not None:
            payload["seed"] = seed

        req = urllib.request.Request(
            url,
            headers=self.headers,
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                elapsed = time.time() - start_time
                ct = resp.headers.get("Content-Type", "").lower()
                data = resp.read()

                # If binary image payload
                if "image" in ct:
                    return data, elapsed, None

                # If JSON payload containing base64 string
                try:
                    j = json.loads(data.decode("utf-8"))
                    if j.get("success") or "result" in j:
                        res = j.get("result", {})
                        b64 = res.get("image") or j.get("image")
                        if b64:
                            img_bytes = base64.b64decode(b64)
                            return img_bytes, elapsed, None
                    errs = j.get("errors", [])
                    err_msg = ", ".join(e.get("message", "") for e in errs) if errs else str(j)
                    return None, elapsed, err_msg
                except Exception as ex:
                    return None, elapsed, f"Failed parsing image response: {ex}"
        except urllib.error.HTTPError as e:
            elapsed = time.time() - start_time
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                j = json.loads(err_body)
                msg = ", ".join(er.get("message", "") for er in j.get("errors", [])) or err_body
            except Exception:
                msg = err_body
            return None, elapsed, f"HTTP {e.code}: {msg}"
        except Exception as e:
            elapsed = time.time() - start_time
            return None, elapsed, str(e)

    # -------------------------------------------------------------------------
    # Workers AI: Vision / Image-to-Text
    # -------------------------------------------------------------------------

    def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str = "Describe this image in detail.",
        model: str = "@cf/meta/llama-3.2-11b-vision-instruct"
    ) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Analyze an image and return description or answers.
        """
        url = f"{CF_API_BASE}/accounts/{self.account_id}/ai/run/{model}"
        payload = {
            "prompt": prompt,
            "image": list(image_bytes)
        }

        req = urllib.request.Request(
            url,
            headers=self.headers,
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                elapsed = time.time() - start_time
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("success"):
                    desc = data.get("result", {}).get("description") or data.get("result", {}).get("response", "")
                    return desc, elapsed, None
                errs = data.get("errors", [])
                return None, elapsed, ", ".join(e.get("message", "") for e in errs)
        except Exception as e:
            elapsed = time.time() - start_time
            return None, elapsed, str(e)

    # -------------------------------------------------------------------------
    # Edge Infrastructure: Zones, Workers, D1, KV, R2
    # -------------------------------------------------------------------------

    def get_zones(self) -> List[Dict[str, Any]]:
        """List all DNS zones under this account."""
        url = f"{CF_API_BASE}/zones"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", [])
        except Exception:
            return []

    def get_dns_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """List DNS records for a given zone."""
        url = f"{CF_API_BASE}/zones/{zone_id}/dns_records"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", [])
        except Exception:
            return []

    def get_workers(self) -> List[Dict[str, Any]]:
        """List active Cloudflare Workers scripts."""
        url = f"{CF_API_BASE}/accounts/{self.account_id}/workers/scripts"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", [])
        except Exception:
            return []

    def get_d1_databases(self) -> List[Dict[str, Any]]:
        """List serverless D1 SQLite databases."""
        url = f"{CF_API_BASE}/accounts/{self.account_id}/d1/database"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", [])
        except Exception:
            return []

    def get_kv_namespaces(self) -> List[Dict[str, Any]]:
        """List KV namespaces."""
        url = f"{CF_API_BASE}/accounts/{self.account_id}/storage/kv/namespaces"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", [])
        except Exception:
            return []

    def get_r2_buckets(self) -> List[Dict[str, Any]]:
        """List R2 object storage buckets."""
        url = f"{CF_API_BASE}/accounts/{self.account_id}/r2/buckets"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", {}).get("buckets", [])
        except Exception:
            return []

    def get_ai_gateways(self) -> List[Dict[str, Any]]:
        """List AI Gateway instances."""
        url = f"{CF_API_BASE}/accounts/{self.account_id}/ai-gateway/gateways"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", [])
        except Exception:
            return []
