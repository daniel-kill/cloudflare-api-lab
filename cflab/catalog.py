"""
Interactive Workers AI Models Catalog & Inspector.
Browse, search, and ping all 73+ serverless AI models on Cloudflare.
"""

import sys
import time
from typing import List, Optional

from .banner import (
    RESET, BOLD, DIM, CYAN, AMBER, CF_ORANGE, GOLD, GREEN, PURPLE, GRAY, WHITE, DARK_GRAY, CRIMSON,
    print_header, print_divider
)
from .client import CloudflareClient
from .models import ModelInfo

class CatalogViewer:
    def __init__(self, client: CloudflareClient):
        self.client = client

    def run(self) -> None:
        """Browse and filter models interactively."""
        models = self.client.get_models()
        if not models:
            print(f"{CRIMSON}Could not retrieve models from Cloudflare.{RESET}")
            return

        while True:
            print_header("WORKERS AI MODELS CATALOG", f"{len(models)} Total Edge Models Available")
            print(f"{DARK_GRAY}Filter by task category:{RESET}")
            print(f"  {CYAN}[1]{RESET} All Models ({len(models)})")
            print(f"  {CYAN}[2]{RESET} 💬 Text Generation & LLMs (Llama 3.3 70B, GPT-OSS 120B, DeepSeek R1)")
            print(f"  {CYAN}[3]{RESET} 🎨 Text-to-Image (FLUX.1-schnell, FLUX.2-klein, SDXL Lightning)")
            print(f"  {CYAN}[4]{RESET} 👁️  Vision & OCR (Llama 3.2 11B Vision, LLaVA)")
            print(f"  {CYAN}[5]{RESET} 🎙️  Automatic Speech Recognition (Whisper, Whisper Tiny)")
            print(f"  {CYAN}[6]{RESET} 🔢 Text Embeddings (BGE Large & Small)")
            print(f"  {CYAN}[7]{RESET} 🌐 Translation (Meta M2M-100)")
            print(f"  {CYAN}[8]{RESET} 🔍 Search by keyword / model name")
            print(f"  {CYAN}[9]{RESET} ⚡ Ping / Test a Model")
            print(f"  {CYAN}[0]{RESET} Back to Main Menu")

            choice = input(f"\n{AMBER}Select view [0-9]: {RESET}").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._display_table(models, "ALL CLOUDFLARE WORKERS AI MODELS")
            elif choice == "2":
                filtered = [m for m in models if m.task == "Text Generation"]
                self._display_table(filtered, "TEXT GENERATION & LLM MODELS")
            elif choice == "3":
                filtered = [m for m in models if m.task == "Text-to-Image"]
                self._display_table(filtered, "TEXT-TO-IMAGE MODELS")
            elif choice == "4":
                filtered = [m for m in models if m.task == "Image-to-Text"]
                self._display_table(filtered, "VISION & OCR MODELS")
            elif choice == "5":
                filtered = [m for m in models if m.task == "Automatic Speech Recognition"]
                self._display_table(filtered, "AUTOMATIC SPEECH RECOGNITION MODELS")
            elif choice == "6":
                filtered = [m for m in models if m.task == "Text Embeddings"]
                self._display_table(filtered, "TEXT EMBEDDINGS MODELS")
            elif choice == "7":
                filtered = [m for m in models if m.task == "Translation"]
                self._display_table(filtered, "TRANSLATION MODELS")
            elif choice == "8":
                kw = input(f"{AMBER}Search keyword (e.g. flux, llama, whisper, r1, sdxl): {RESET}").strip().lower()
                filtered = [
                    m for m in models 
                    if kw in m.id.lower() or kw in m.name.lower() or kw in m.description.lower()
                ]
                self._display_table(filtered, f"SEARCH RESULTS: '{kw}'")
            elif choice == "9":
                self._ping_model(models)
            else:
                print(f"{CRIMSON}Invalid choice.{RESET}")

    def _display_table(self, models: List[ModelInfo], title: str) -> None:
        """Render clean terminal table."""
        print_header(title, f"{len(models)} Models")
        print(f" {BOLD}{'#':<3} {'Task':<18} {'Model Name':<28} {'Model ID':<45} {'Context':<8}{RESET}")
        print(f" {DARK_GRAY}{'─'*3} {'─'*18} {'─'*28} {'─'*45} {'─'*8}{RESET}")

        for idx, m in enumerate(models, 1):
            task_col = m.task_badge
            name_col = m.name[:26]
            id_col = m.id[:43]
            ctx_col = m.formatted_ctx

            color = WHITE
            if "flux" in m.id:
                color = GOLD
            elif "70b" in m.id or "deepseek" in m.id:
                color = CF_ORANGE
            elif "vision" in m.id:
                color = CYAN
            elif "whisper" in m.id:
                color = GREEN

            print(f" {DARK_GRAY}{idx:2d}{RESET}  {task_col:<28} {color}{name_col:<28}{RESET} {DARK_GRAY}{id_col:<45}{RESET} {PURPLE}{ctx_col:<8}{RESET}")

        print(f"\n{DARK_GRAY}Tip: Use Option 9 to ping any model, or use in chat/image studio.{RESET}")
        input(f"\n{AMBER}Press Enter to return...{RESET}")

    def _ping_model(self, models: List[ModelInfo]) -> None:
        """Ping a model with a quick test."""
        print(f"\n{GOLD}{BOLD}Test / Ping a Model:{RESET}")
        target = input(f"{AMBER}Model number or ID (e.g. @cf/meta/llama-3.1-8b-instruct): {RESET}").strip()
        if not target:
            return

        target_model = None
        if target.isdigit() and 1 <= int(target) <= len(models):
            target_model = models[int(target) - 1]
        else:
            target_model = next((m for m in models if m.id == target), None)
            if not target_model:
                target_model = ModelInfo(id=target, name=target, task="Text Generation")

        print(f"\n{CF_ORANGE}Pinging {target_model.name} ({target_model.id})...{RESET}\n")
        start_t = time.time()

        if target_model.task == "Text-to-Image":
            img, elapsed, err = self.client.generate_image("A futuristic serverless node in glowing orange light", model=target_model.id, steps=2)
            if err or not img:
                print(f"{CRIMSON}Ping failed: {err}{RESET}")
            else:
                print(f"{GREEN}✓ Ping successful! Generated {len(img)} bytes image in {elapsed:.2f}s.{RESET}")
        else:
            try:
                for chunk in self.client.stream_chat(
                    [{"role": "user", "content": "In 1 sentence: Introduce yourself."}],
                    model=target_model.id
                ):
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                print()
            except Exception as e:
                print(f"{CRIMSON}Ping failed: {e}{RESET}")

        elapsed = time.time() - start_t
        print(f"\n{DARK_GRAY}[⏱️  Latency: {elapsed:.2f}s]{RESET}\n")
        input(f"{AMBER}Press Enter to return...{RESET}")
