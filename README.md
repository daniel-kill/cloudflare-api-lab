# Cloudflare API Lab (cflab) ☁️

[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Cloudflare Workers AI](https://img.shields.io/badge/Cloudflare-Workers%20AI-orange.svg)](https://developers.cloudflare.com/workers-ai/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20Mandatory-success.svg)](#installation)

> **Interactive Terminal Laboratory & Developer Tool for Cloudflare Workers AI & Edge Cloud Platform.**  
> Render photorealistic imagery with FLUX.1 in seconds, stream reasoning from 70B+ LLMs, analyze images with multimodal vision, and inspect edge infrastructure (Workers, D1, KV, R2, DNS) directly from your terminal.

Created and maintained by [Daniel Kill](https://github.com/daniel-kill) (<daniel@danielkill.online>).

---

```
   ____ _                 _  __ _                 
  / ___| | ___  _   _  __| |/ _| | __ _ _ __ ___  
 | |   | |/ _ \| | | |/ _` | |_| |/ _` | '__/ _ \ 
 | |___| | (_) | |_| | (_| |  _| | (_| | | |  __/ 
  \____|_|\___/ \__,_|\__,_|_| |_|\__,_|_|  \___| 
     _    ____ ___   _          _     
    / \  |  _ \_ _| | |    __ _| |__  
   / _ \ | |_) | |  | |   / _` | '_ \ 
  / ___ \|  __/| |  | |__| (_| | |_) |
 /_/   \_\_|  |___| |_____\__,_|_.__/ 

  ☁️  Workers AI & Edge Cloud Platform Laboratory  ☁️
```

---

## ⚡ Highlights

- **Zero Mandatory External Dependencies:** Runs natively out-of-the-box with standard Python 3.8+ (`urllib`, `json`, `base64`, `os`, `sys`).
- **High-Speed Image Studio:** Generate 1024x1024 images using **FLUX.1-schnell**, **FLUX.2-klein**, **SDXL Lightning**, and **DreamShaper LCM** in **2 to 4 seconds** on Cloudflare's serverless GPU edge network.
- **Frontier LLM Streaming:** Real-time token streaming from Meta's **Llama 3.3 70B Instruct**, **Llama 3.1 8B**, **OpenAI GPT-OSS 120B**, and **DeepSeek R1 Distill Qwen 32B**.
- **In-Chat Image Generation:** Seamlessly generate images directly from your chat conversation using the `/image <prompt>` slash command without switching modes.
- **Multimodal Vision Lab:** Pass any local image path or photo for instant scene deconstruction, object detection, and optical character recognition (OCR) using **Llama 3.2 11B Vision**.
- **Edge Platform Explorer:** Inspect DNS Zones, Worker scripts, serverless D1 SQLite databases, KV namespaces, R2 storage buckets, and AI Gateways.
- **73+ Models Catalog:** Search and filter Cloudflare's complete catalog by task (Text Generation, Text-to-Image, Vision, Speech Recognition, Embeddings, Translation).
- **Cross-Platform Compatibility:** Fully supported on Windows (PowerShell 7 / pwsh, CMD) and Linux / WSL with automated credential discovery.

---

## 🌟 Featured Workers AI Models

Cloudflare API Lab surfaces all 73+ models deployed on Cloudflare's global GPU network:

### 🎨 Text-to-Image
| Model ID | Provider | Steps | Description |
| :--- | :--- | :--- | :--- |
| `@cf/black-forest-labs/flux-1-schnell` | Black Forest Labs | 4 | 12B flow transformer: state-of-the-art photorealism & prompt adherence |
| `@cf/black-forest-labs/flux-2-klein-9b` | Black Forest Labs | 4 | Next-generation 9B parameter FLUX architecture |
| `@cf/bytedance/stable-diffusion-xl-lightning` | ByteDance | 8 | High-speed distilled 1024x1024 generation in 4-8 steps |
| `@cf/lykon/dreamshaper-8-lcm` | Lykon | 6 | Latent Consistency Model tuned for portraits, digital art, and anime |
| `@cf/stabilityai/stable-diffusion-xl-base-1.0` | Stability AI | 20 | Full 3.5B foundation model for complex compositions |

### 💬 Text Generation & Reasoning
| Model ID | Context Window | Architecture | Description |
| :--- | :--- | :--- | :--- |
| `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | 131,072 tokens | 70B FP8-Fast | Flagship frontier intelligence running at 35+ tok/s |
| `@cf/meta/llama-3.1-8b-instruct` | 131,072 tokens | 8B Dense | Versatile, fast instruction model with 128K context |
| `@cf/openai/gpt-oss-120b` | 131,072 tokens | 120B Dense | Massive open-weights model hosted directly on Cloudflare GPUs |
| `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` | 131,072 tokens | 32B Distill | Deep mathematical and code reasoning with chain-of-thought |
| `@cf/mistral/mistral-7b-instruct-v0.2-lora` | 32,768 tokens | 7B Dense | High-efficiency instruction model by Mistral AI |

### 👁️ Vision, Audio & Utilities
| Model ID | Task | Description |
| :--- | :--- | :--- |
| `@cf/meta/llama-3.2-11b-vision-instruct` | Image-to-Text | Vision-language model understanding images, charts, and OCR |
| `@cf/openai/whisper` | Speech Recognition | Multilingual automatic speech-to-text audio transcription |
| `@cf/baai/bge-large-en-v1.5` | Text Embeddings | 1024-dimension semantic vector embeddings for vector search & RAG |
| `@cf/meta/m2m100-1.2b` | Translation | Direct 100-language translation without intermediate English pivot |

---

## 🚀 Quickstart & Installation

### 1. Prerequisites & API Credentials
Ensure you have Python 3.8+ installed. Set your Cloudflare Account ID and API Token:

**Windows PowerShell:**
```powershell
$env:CLOUDFLARE_ACCOUNT_ID = "0e058d11ca44..."
$env:CLOUDFLARE_API_TOKEN = "cfat_..."

# Or persist permanently in your User profile:
[System.Environment]::SetEnvironmentVariable('CLOUDFLARE_ACCOUNT_ID', '0e058d11ca44...', 'User')
[System.Environment]::SetEnvironmentVariable('CLOUDFLARE_API_TOKEN', 'cfat_...', 'User')
```

**Linux / macOS / WSL:**
```bash
export CLOUDFLARE_ACCOUNT_ID="0e058d11ca44..."
export CLOUDFLARE_API_TOKEN="cfat_..."
```

*(Note: If not set in the environment, Cloudflare API Lab automatically checks Windows User Registry, `~/.cflab/.env`, or prompts you on first run.)*

### 2. Clone & Run
```bash
git clone https://github.com/daniel-kill/cloudflare-api-lab.git
cd cloudflare-api-lab

# Launch the interactive terminal laboratory
python cflab.py
```

---

## 🕹️ CLI Usage & Flags

Cloudflare API Lab functions both as a full interactive TUI menu and an instant CLI utility:

```bash
# 1. Quick single prompt (streams response to stdout via Llama 3.3 70B)
python cflab.py -p "Explain how Cloudflare Workers route requests at the edge"

# 2. Render an image from prompt using FLUX.1-schnell (~3s render)
python cflab.py --image "Gothic vampire lord in crimson velvet overlooking Castle Dracula"

# 3. Specify custom model and steps for image generation
python cflab.py --image "Cyberpunk metropolis in neon rain" --model "@cf/bytedance/stable-diffusion-xl-lightning" --steps 8

# 4. Multimodal image analysis / OCR with Llama 3.2 Vision
python cflab.py --vision ./photo.png -p "What text and objects are visible in this image?"

# 5. Jump straight into interactive streaming chat REPL
python cflab.py --chat

# 6. Jump straight into the interactive Image Studio
python cflab.py --studio

# 7. Inspect Cloudflare account details & token validity
python cflab.py --account

# 8. Inspect edge infrastructure (DNS Zones, Workers, D1, KV, R2)
python cflab.py --edge

# 9. Browse all 73+ Workers AI models
python cflab.py --models
```

---

## 💬 Chat Session Slash Commands

While in an interactive chat session, control the laboratory on the fly using slash commands:

| Command | Shortcut | Description |
| :--- | :--- | :--- |
| `/image [prompt]` | — | **Generate an image instantly** inside chat and save to disk |
| `/model [id]` | `/m` | Switch active LLM model (Llama 3.3 70B, GPT-OSS 120B, DeepSeek R1) |
| `/persona [name]` | `/p` | Switch persona (architect, visionary, secops, dracula, oracle) |
| `/system [text]` | `/s` | View or customize the system instruction |
| `/params [temp]` | — | Adjust sampling temperature (0.0 to 1.5) |
| `/clear` | `/c` | Clear conversation memory context |
| `/save [filename]` | — | Export chat transcript to formatted Markdown |
| `/stats` | — | Display token counts, duration, and generation speed (tok/s) |
| `/help` | `/h` | View command guide |
| `/exit` | `/q` | Return to main menu |

---

## 🌐 Edge Infrastructure Explorer

The Edge Explorer gives you live visibility into Cloudflare's serverless building blocks:
- **DNS Zones:** Inspect domain status, nameservers, and DNS routing records.
- **Workers Scripts:** Inspect active serverless scripts running on Cloudflare's V8 runtime.
- **D1 Databases:** View serverless edge SQLite databases.
- **KV Namespaces:** Inspect low-latency key-value data stores.
- **R2 Storage:** Check S3-compatible object storage buckets.
- **AI Gateways:** Inspect gateway metrics, logging, and caching rules.
- **Worker Code Generator:** Automatically export a production-ready JavaScript/TypeScript Worker template utilizing `@cloudflare/ai`.

---

## 📜 License

MIT License. Copyright (c) 2026 Daniel Kill <daniel@danielkill.online>.
