"""
Multimodal Vision & OCR Laboratory for Cloudflare Workers AI.
Powered by Llama 3.2 11B Vision and LLaVA 1.5.
"""

import sys
import time
from pathlib import Path
from typing import Optional

from .banner import (
    RESET, BOLD, DIM, CYAN, AMBER, CF_ORANGE, GOLD, GREEN, GRAY, WHITE, DARK_GRAY, CRIMSON,
    print_header, print_divider
)
from .client import CloudflareClient

DEFAULT_VISION_MODEL = "@cf/meta/llama-3.2-11b-vision-instruct"

class VisionLab:
    def __init__(self, client: CloudflareClient):
        self.client = client

    def run(self, preset_image: Optional[str] = None, preset_prompt: Optional[str] = None) -> None:
        """Run interactive vision analysis session."""
        print_header("WORKERS AI VISION & MULTIMODAL LAB", "Powered by Llama 3.2 11B Vision & LLaVA")
        print(f"{DARK_GRAY}Analyze local images, extract text/OCR, detect objects, and evaluate visual scenes.{RESET}\n")

        image_path_str = preset_image
        if not image_path_str:
            print(f"{GOLD}{BOLD}Enter Image Path:{RESET}")
            print(f"{GRAY}Supports PNG, JPEG, WebP, GIF (e.g. C:\\path\\to\\image.png){RESET}")
            image_path_str = input(f"{AMBER}Image Path: {RESET}").strip().strip('"').strip("'")

        if not image_path_str:
            return

        img_path = Path(image_path_str)
        if not img_path.exists():
            print(f"{CRIMSON}File not found: {img_path}{RESET}\n")
            input(f"{AMBER}Press Enter to return...{RESET}")
            return

        try:
            img_bytes = img_path.read_bytes()
        except Exception as e:
            print(f"{CRIMSON}Failed reading image file: {e}{RESET}\n")
            input(f"{AMBER}Press Enter to return...{RESET}")
            return

        file_size_kb = len(img_bytes) / 1024
        print(f"\n{GREEN}✓ Loaded image:{RESET} {WHITE}{img_path.name}{RESET} ({file_size_kb:.1f} KB)")

        # Prompt selection
        prompt = preset_prompt
        if not prompt:
            print(f"\n{GOLD}{BOLD}Select Vision Query:{RESET}")
            print(f"  {CYAN}[1]{RESET} Describe this image in comprehensive detail.")
            print(f"  {CYAN}[2]{RESET} Optical Character Recognition (OCR): Extract all visible text.")
            print(f"  {CYAN}[3]{RESET} Identify all key objects, colors, and spatial composition.")
            print(f"  {CYAN}[4]{RESET} Enter Custom Question / Instruction")

            p_choice = input(f"\n{AMBER}Select [1-4] (default: 1): {RESET}").strip() or "1"
            if p_choice == "1":
                prompt = "Describe this image in comprehensive, meticulous detail. Mention subjects, lighting, background, colors, and mood."
            elif p_choice == "2":
                prompt = "Transcribe and extract all written, printed, or rendered text visible in this image accurately."
            elif p_choice == "3":
                prompt = "List all identifiable objects, key color palettes, artistic style, and layout structure in this image."
            else:
                prompt = input(f"\n{AMBER}Enter custom question about the image: {RESET}").strip()

        if not prompt:
            prompt = "Describe this image in detail."

        print(f"\n{CF_ORANGE}Analyzing image on Cloudflare Edge GPUs ({DEFAULT_VISION_MODEL})...{RESET}\n")

        start_time = time.time()
        desc, elapsed, err = self.client.analyze_image(
            image_bytes=img_bytes,
            prompt=prompt,
            model=DEFAULT_VISION_MODEL
        )

        if err or not desc:
            print(f"{CRIMSON}✗ Vision analysis failed: {err}{RESET}\n")
        else:
            print(f"{DARK_GRAY}───────────────────────────────────────────────────────────────────{RESET}")
            print(f"{CYAN}{BOLD}VISION ANALYSIS RESULT:{RESET}")
            print(f"{DARK_GRAY}───────────────────────────────────────────────────────────────────{RESET}\n")
            print(desc.strip())
            print(f"\n{DARK_GRAY}[⏱️  Analysis Latency: {elapsed:.2f}s]{RESET}\n")

        input(f"{AMBER}Press Enter to return to menu...{RESET}")
