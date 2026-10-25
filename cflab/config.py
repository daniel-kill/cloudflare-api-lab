"""
Configuration, credential discovery, and user settings for Cloudflare API Lab.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

DEFAULT_TEXT_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
DEFAULT_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
DEFAULT_VISION_MODEL = "@cf/meta/llama-3.2-11b-vision-instruct"

CONFIG_DIR = Path.home() / ".cflab"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = CONFIG_DIR / ".env"
IMAGE_DIR = CONFIG_DIR / "generated_images"

DEFAULT_SETTINGS = {
    "default_text_model": DEFAULT_TEXT_MODEL,
    "default_image_model": DEFAULT_IMAGE_MODEL,
    "default_vision_model": DEFAULT_VISION_MODEL,
    "temperature": 0.7,
    "max_tokens": 4096,
    "image_steps": 4,
    "image_dir": str(IMAGE_DIR),
    "auto_open_images": True,
    "save_transcripts": True,
    "system_prompt": "You are a helpful, expert AI assistant powered by Cloudflare Workers AI."
}

def _lookup_env_file(path: Path, target_var: str) -> Optional[str]:
    """Search a .env file for the given variable."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{target_var}="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    except Exception:
        pass
    return None

def _get_windows_registry_env(var_name: str) -> Optional[str]:
    """Read environment variable from Windows User Registry (HKCU\\Environment)."""
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                val, _ = winreg.QueryValueEx(key, var_name)
                if val:
                    return str(val).strip()
        except Exception:
            pass
    return None

def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve Cloudflare Account ID and API Token.
    Searches:
    1. Active os.environ
    2. Windows User Registry (HKCU\\Environment)
    3. User config ~/.cflab/.env
    4. Local .env in current working directory
    5. WSL -> Windows Host fallback
    """
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()

    # Registry lookup if missing
    if not account_id:
        account_id = _get_windows_registry_env("CLOUDFLARE_ACCOUNT_ID") or ""
    if not api_token:
        api_token = _get_windows_registry_env("CLOUDFLARE_API_TOKEN") or ""

    # Local ~/.cflab/.env
    if not account_id:
        account_id = _lookup_env_file(ENV_FILE, "CLOUDFLARE_ACCOUNT_ID") or ""
    if not api_token:
        api_token = _lookup_env_file(ENV_FILE, "CLOUDFLARE_API_TOKEN") or ""

    # Current directory .env
    if not account_id:
        account_id = _lookup_env_file(Path(".env"), "CLOUDFLARE_ACCOUNT_ID") or ""
    if not api_token:
        api_token = _lookup_env_file(Path(".env"), "CLOUDFLARE_API_TOKEN") or ""

    # WSL cross-platform fallback
    if (not account_id or not api_token) and os.name != "nt" and Path("/proc/version").exists():
        try:
            # Check mounted Windows User .cflab/.env
            for win_user_dir in Path("/mnt/c/Users").glob("*/.cflab/.env"):
                if not account_id:
                    account_id = _lookup_env_file(win_user_dir, "CLOUDFLARE_ACCOUNT_ID") or ""
                if not api_token:
                    api_token = _lookup_env_file(win_user_dir, "CLOUDFLARE_API_TOKEN") or ""

            # Check powershell.exe on Windows host
            if not account_id or not api_token:
                cmd = ["powershell.exe", "-NoProfile", "-Command",
                       "[System.Environment]::GetEnvironmentVariable('CLOUDFLARE_ACCOUNT_ID', 'User') + '|||' + [System.Environment]::GetEnvironmentVariable('CLOUDFLARE_API_TOKEN', 'User')"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
                if proc.returncode == 0 and "|||" in proc.stdout:
                    parts = proc.stdout.strip().split("|||")
                    if not account_id and parts[0].strip():
                        account_id = parts[0].strip()
                    if not api_token and len(parts) > 1 and parts[1].strip():
                        api_token = parts[1].strip()
        except Exception:
            pass

    return (account_id or None, api_token or None)

def save_credentials_to_env(account_id: str, api_token: str) -> None:
    """Save credentials to ~/.cflab/.env for future sessions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(f"CLOUDFLARE_ACCOUNT_ID={account_id}\n")
        f.write(f"CLOUDFLARE_API_TOKEN={api_token}\n")

    os.environ["CLOUDFLARE_ACCOUNT_ID"] = account_id
    os.environ["CLOUDFLARE_API_TOKEN"] = api_token

def load_settings() -> Dict[str, Any]:
    """Load settings from config file, creating defaults if missing."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                merged = {**DEFAULT_SETTINGS, **saved}
                return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: Dict[str, Any]) -> None:
    """Save updated settings to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass
