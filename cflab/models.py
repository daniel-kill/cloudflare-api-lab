"""
Model registry, metadata structures, and categorization for Cloudflare Workers AI.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ModelInfo:
    id: str
    name: str
    task: str  # 'Text Generation', 'Text-to-Image', 'Image-to-Text', etc.
    description: str = ""
    context_length: int = 4096
    input_modalities: List[str] = field(default_factory=list)
    output_modalities: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    @property
    def formatted_ctx(self) -> str:
        """Return human-readable context window format (e.g. 128K, 8K)."""
        if self.context_length >= 1_000_000:
            return f"{self.context_length // 1_000_000}M"
        elif self.context_length >= 1000:
            return f"{self.context_length // 1000}K"
        return f"{self.context_length}"

    @property
    def task_badge(self) -> str:
        """Return task icon & short label."""
        task_map = {
            "Text Generation": "💬 Text Gen",
            "Text-to-Image": "🎨 Text-to-Image",
            "Image-to-Text": "👁️ Vision / OCR",
            "Automatic Speech Recognition": "🎙️ Speech-to-Text",
            "Text-to-Speech": "🔊 Text-to-Speech",
            "Text Embeddings": "🔢 Embeddings",
            "Translation": "🌐 Translation",
            "Text Classification": "🛡️ Classification",
            "Image Classification": "🖼️ Img Classify"
        }
        return task_map.get(self.task, f"⚙️ {self.task}")


# Curated offline catalog of Cloudflare Workers AI Models
FALLBACK_CF_MODELS: List[Dict[str, Any]] = [
    # --- TEXT-TO-IMAGE ---
    {
        "id": "@cf/black-forest-labs/flux-1-schnell",
        "name": "FLUX.1-schnell",
        "task": "Text-to-Image",
        "description": "12B parameter state-of-the-art rectified flow transformer by Black Forest Labs (4-8 steps).",
        "context_length": 512,
        "input_modalities": ["text"],
        "output_modalities": ["image"]
    },
    {
        "id": "@cf/black-forest-labs/flux-2-klein-9b",
        "name": "FLUX.2-klein-9B",
        "task": "Text-to-Image",
        "description": "High-efficiency 9B parameter next-generation FLUX architecture for photorealistic imagery.",
        "context_length": 512,
        "input_modalities": ["text"],
        "output_modalities": ["image"]
    },
    {
        "id": "@cf/bytedance/stable-diffusion-xl-lightning",
        "name": "SDXL Lightning",
        "task": "Text-to-Image",
        "description": "Ultra-fast distilled SDXL generating high-res 1024x1024 images in 2-8 steps.",
        "context_length": 512,
        "input_modalities": ["text"],
        "output_modalities": ["image"]
    },
    {
        "id": "@cf/lykon/dreamshaper-8-lcm",
        "name": "DreamShaper 8 LCM",
        "task": "Text-to-Image",
        "description": "Latent Consistency Model tuned for photorealistic portraits, digital art, and anime.",
        "context_length": 512,
        "input_modalities": ["text"],
        "output_modalities": ["image"]
    },
    {
        "id": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
        "name": "Stable Diffusion XL 1.0",
        "task": "Text-to-Image",
        "description": "Flagship 3.5B open foundation model for complex compositions and photorealism.",
        "context_length": 512,
        "input_modalities": ["text"],
        "output_modalities": ["image"]
    },
    {
        "id": "@cf/runwayml/stable-diffusion-v1-5-inpainting",
        "name": "SD 1.5 Inpainting",
        "task": "Text-to-Image",
        "description": "Classic Stable Diffusion tuned for mask inpainting and targeted modifications.",
        "context_length": 512,
        "input_modalities": ["text", "image"],
        "output_modalities": ["image"]
    },

    # --- TEXT GENERATION / LLMS ---
    {
        "id": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        "name": "Llama 3.3 70B Instruct Fast",
        "task": "Text Generation",
        "description": "Meta's flagship 70B open-weights model running FP8-fast at 35+ tok/s on Cloudflare Workers AI.",
        "context_length": 131072,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/meta/llama-3.1-8b-instruct-fp8",
        "name": "Llama 3.1 8B Instruct FP8",
        "task": "Text Generation",
        "description": "Meta's versatile 8B parameter model supporting 128K context window.",
        "context_length": 131072,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/meta/llama-3.2-3b-instruct",
        "name": "Llama 3.2 3B Instruct",
        "task": "Text Generation",
        "description": "Ultra-lightweight edge model optimized for low latency and prompt workflows.",
        "context_length": 131072,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/meta/llama-3.2-1b-instruct",
        "name": "Llama 3.2 1B Instruct",
        "task": "Text Generation",
        "description": "Sub-billion lightweight model built for instantaneous response and classification.",
        "context_length": 131072,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/openai/gpt-oss-120b",
        "name": "OpenAI GPT-OSS 120B",
        "task": "Text Generation",
        "description": "Massive 120B parameter reasoning model running on Cloudflare GPUs with 128K context.",
        "context_length": 131072,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
        "name": "DeepSeek R1 Distill Qwen 32B",
        "task": "Text Generation",
        "description": "Deep reasoning model with chain-of-thought distillation for mathematics and code.",
        "context_length": 131072,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/google/gemma-7b-it",
        "name": "Google Gemma 7B IT",
        "task": "Text Generation",
        "description": "Google's lightweight instruction-tuned model trained on Gemini research.",
        "context_length": 8192,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/mistral/mistral-7b-instruct-v0.2-lora",
        "name": "Mistral 7B Instruct v0.2",
        "task": "Text Generation",
        "description": "High performance 7B model by Mistral AI with 32K context support.",
        "context_length": 32768,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/qwen/qwen1.5-14b-chat-awq",
        "name": "Qwen 1.5 14B Chat",
        "task": "Text Generation",
        "description": "Alibaba's 14B multilingual model optimized with AWQ 4-bit quantization.",
        "context_length": 32768,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },

    # --- VISION & MULTIMODAL ---
    {
        "id": "@cf/meta/llama-3.2-11b-vision-instruct",
        "name": "Llama 3.2 11B Vision",
        "task": "Image-to-Text",
        "description": "Multimodal vision-language model understanding images, charts, diagrams, and text.",
        "context_length": 131072,
        "input_modalities": ["text", "image"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/llava-hf/llava-1.5-7b-hf",
        "name": "LLaVA 1.5 7B",
        "task": "Image-to-Text",
        "description": "Visual instruction tuning connecting vision encoder to Vicuna language model.",
        "context_length": 4096,
        "input_modalities": ["text", "image"],
        "output_modalities": ["text"]
    },

    # --- SPEECH RECOGNITION (AUDIO-TO-TEXT) ---
    {
        "id": "@cf/openai/whisper",
        "name": "OpenAI Whisper",
        "task": "Automatic Speech Recognition",
        "description": "Multilingual automatic speech recognition and audio transcription model.",
        "context_length": 448,
        "input_modalities": ["audio"],
        "output_modalities": ["text"]
    },
    {
        "id": "@cf/openai/whisper-tiny-en",
        "name": "Whisper Tiny English",
        "task": "Automatic Speech Recognition",
        "description": "Ultra-fast low-latency English speech transcription engine.",
        "context_length": 448,
        "input_modalities": ["audio"],
        "output_modalities": ["text"]
    },

    # --- TEXT EMBEDDINGS ---
    {
        "id": "@cf/baai/bge-large-en-v1.5",
        "name": "BGE Large English v1.5",
        "task": "Text Embeddings",
        "description": "1024-dimension high-accuracy semantic embeddings for vector search & RAG.",
        "context_length": 512,
        "input_modalities": ["text"],
        "output_modalities": ["vector"]
    },
    {
        "id": "@cf/baai/bge-small-en-v1.5",
        "name": "BGE Small English v1.5",
        "task": "Text Embeddings",
        "description": "384-dimension compact embeddings optimized for low latency and vector database storage.",
        "context_length": 512,
        "input_modalities": ["text"],
        "output_modalities": ["vector"]
    },

    # --- TRANSLATION ---
    {
        "id": "@cf/meta/m2m100-1.2b",
        "name": "Meta M2M-100 1.2B",
        "task": "Translation",
        "description": "Direct translation between 100 languages without relying on English as intermediate pivot.",
        "context_length": 1024,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    },

    # --- MODERATION & CLASSIFICATION ---
    {
        "id": "@cf/meta/llama-guard-3-8b",
        "name": "Llama Guard 3 8B",
        "task": "Text Classification",
        "description": "Llama 3-based safety classifier detecting toxic, hazardous, or policy-violating prompts.",
        "context_length": 8192,
        "input_modalities": ["text"],
        "output_modalities": ["text"]
    }
]

def parse_model_from_cf_api(raw: Dict[str, Any]) -> ModelInfo:
    """Parse a raw model item from Cloudflare's /ai/models/search API."""
    mid = raw.get("name", "") or raw.get("id", "")
    task_info = raw.get("task", {})
    task_name = task_info.get("name", "Text Generation") if isinstance(task_info, dict) else str(task_info)
    desc = raw.get("description", "")
    
    # Try finding friendly name in fallback catalog
    matched = next((m for m in FALLBACK_CF_MODELS if m["id"] == mid), None)
    friendly_name = matched["name"] if matched else mid.split("/")[-1].replace("-", " ").title()
    ctx = matched["context_length"] if matched else 4096

    in_mods = ["text"]
    out_mods = ["text"]
    if task_name == "Text-to-Image":
        in_mods = ["text"]
        out_mods = ["image"]
    elif task_name == "Image-to-Text":
        in_mods = ["text", "image"]
        out_mods = ["text"]
    elif task_name == "Automatic Speech Recognition":
        in_mods = ["audio"]
        out_mods = ["text"]
    elif task_name == "Text-to-Speech":
        in_mods = ["text"]
        out_mods = ["audio"]
    elif task_name == "Text Embeddings":
        in_mods = ["text"]
        out_mods = ["vector"]

    return ModelInfo(
        id=mid,
        name=friendly_name,
        task=task_name,
        description=desc or (matched["description"] if matched else ""),
        context_length=ctx,
        input_modalities=in_mods,
        output_modalities=out_mods,
        properties=raw.get("properties", {})
    )
