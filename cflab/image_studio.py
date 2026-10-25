"""
Interactive AI Image Studio for Cloudflare Workers AI.
Supports FLUX.1-schnell, FLUX.2-klein, SDXL Lightning, DreamShaper LCM, and SDXL Base.
"""

import os
import re
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from .banner import (
    RESET, BOLD, DIM, CYAN, AMBER, CF_ORANGE, GOLD, GREEN, PURPLE, GRAY, WHITE, DARK_GRAY, CRIMSON,
    print_header, print_divider
)
from .client import CloudflareClient
from .config import load_settings, save_settings

STYLE_PRESETS: Dict[str, Dict[str, str]] = {
    "1": {
        "name": "Cinematic Dark Fantasy / Gothic",
        "suffix": ", cinematic lighting, dark atmosphere, photorealistic, 8k resolution, volumetric fog, dramatic chiaroscuro, masterpiece",
        "negative": "blurry, low quality, cartoon, watermark, distorted, oversaturated"
    },
    "2": {
        "name": "Photorealistic Studio Portrait",
        "suffix": ", 85mm portrait photography, f/1.4 aperture, natural skin texture, soft bokeh, studio lighting, hyper-realistic, award winning",
        "negative": "plastic skin, airbrushed, cartoon, deformed hands, extra limbs, bad eyes"
    },
    "3": {
        "name": "Cyberpunk Neon Metropolis",
        "suffix": ", cyberpunk aesthetic, neon glow, rain-slicked streets, volumetric smoke, futuristic technology, octane render, Unreal Engine 5",
        "negative": "lowres, sketch, blurry, daylight, countryside"
    },
    "4": {
        "name": "Anime & Manga Concept Art",
        "suffix": ", Makoto Shinkai aesthetic, vibrant palette, detailed sky and clouds, expressive lighting, masterpiece digital illustration",
        "negative": "photograph, 3d render, deformed anatomy, low quality"
    },
    "5": {
        "name": "Classic Baroque Oil Painting",
        "suffix": ", Rembrandt chiaroscuro style, rich impasto brushwork, warm golden tones, atmospheric shadows, museum oil on canvas masterpiece",
        "negative": "digital, modern, photograph, neon, sharp plastic"
    },
    "6": {
        "name": "Raw (No Preset Added)",
        "suffix": "",
        "negative": ""
    }
}

AVAILABLE_IMAGE_MODELS = [
    {
        "id": "@cf/black-forest-labs/flux-1-schnell",
        "name": "FLUX.1-schnell (Recommended)",
        "steps": 4,
        "desc": "12B state-of-the-art flow transformer by Black Forest Labs (fastest & highest quality)"
    },
    {
        "id": "@cf/black-forest-labs/flux-2-klein-9b",
        "name": "FLUX.2-klein-9B",
        "steps": 4,
        "desc": "Next-gen 9B efficient FLUX model for photorealism"
    },
    {
        "id": "@cf/bytedance/stable-diffusion-xl-lightning",
        "name": "SDXL Lightning",
        "steps": 8,
        "desc": "Distilled high-speed 1024x1024 generation in 4-8 steps"
    },
    {
        "id": "@cf/lykon/dreamshaper-8-lcm",
        "name": "DreamShaper 8 LCM",
        "steps": 6,
        "desc": "Latent Consistency Model tuned for portraits and anime"
    },
    {
        "id": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
        "name": "Stable Diffusion XL 1.0",
        "steps": 20,
        "desc": "Full foundation 3.5B model for complex compositions"
    }
]

def sanitize_filename(text: str, max_len: int = 40) -> str:
    """Create a filesystem-safe filename slug."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '_', text).strip('-_')
    return text[:max_len] or "image"

def open_image(filepath: Path) -> None:
    """Open image file using system viewer."""
    try:
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(filepath)], check=False)
        else:
            subprocess.run(["xdg-open", str(filepath)], check=False)
    except Exception:
        pass

class ImageStudio:
    def __init__(self, client: CloudflareClient):
        self.client = client
        self.settings = load_settings()
        self.output_dir = Path(self.settings.get("image_dir", Path.home() / ".cflab" / "generated_images"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_model = self.settings.get("default_image_model", "@cf/black-forest-labs/flux-1-schnell")
        self.steps = self.settings.get("image_steps", 4)

    def run(self) -> None:
        """Launch interactive image creation loop."""
        while True:
            m_short = self.current_model.split("/")[-1]
            print_header("WORKERS AI IMAGE STUDIO", f"Model: {m_short} | Steps: {self.steps} | Output: {self.output_dir}")
            print(f"  {CYAN}[1]{RESET} 🎨 Generate Image from Prompt")
            print(f"  {CYAN}[2]{RESET} 🧙 Generate with Guided Style Presets (Gothic, Portrait, Cyberpunk)")
            print(f"  {CYAN}[3]{RESET} ⚙️  Select Image Generation Model ({m_short})")
            print(f"  {CYAN}[4]{RESET} 🎛️  Configure Steps & Output Settings")
            print(f"  {CYAN}[5]{RESET} 📁 Browse Generated Images Gallery ({self.output_dir})")
            print(f"  {CYAN}[0]{RESET} Back to Main Menu")

            choice = input(f"\n{AMBER}Select Studio Option [0-5]: {RESET}").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._generate_direct()
            elif choice == "2":
                self._generate_with_presets()
            elif choice == "3":
                self._select_model()
            elif choice == "4":
                self._configure_parameters()
            elif choice == "5":
                self._browse_gallery()
            else:
                print(f"{CRIMSON}Invalid choice.{RESET}")

    def _generate_direct(self, initial_prompt: str = "") -> None:
        """Quick direct prompt image generation."""
        prompt = initial_prompt
        if not prompt:
            print(f"\n{GOLD}{BOLD}Enter Image Generation Prompt:{RESET}")
            prompt = input(f"{AMBER}Prompt: {RESET}").strip()

        if not prompt:
            print(f"{CRIMSON}Prompt cannot be empty.{RESET}")
            return

        self._execute_generation(prompt)

    def _generate_with_presets(self) -> None:
        """Generate image with style preset wrapping."""
        print(f"\n{GOLD}{BOLD}Choose Aesthetic Style Preset:{RESET}")
        for key, preset in STYLE_PRESETS.items():
            print(f"  {CYAN}[{key}]{RESET} {WHITE}{preset['name']}{RESET}")

        p_choice = input(f"\n{AMBER}Select preset [1-6] (default: 1): {RESET}").strip() or "1"
        preset = STYLE_PRESETS.get(p_choice, STYLE_PRESETS["1"])

        print(f"\n{GOLD}{BOLD}Enter Core Subject / Scene Description:{RESET}")
        print(f"{GRAY}Example: A gothic vampire lord in velvet overlooking Castle Dracula{RESET}")
        subject = input(f"{AMBER}Subject: {RESET}").strip()
        if not subject:
            return

        full_prompt = subject + preset["suffix"]
        neg_prompt = preset["negative"]

        print(f"\n{DARK_GRAY}Synthesized Prompt:{RESET} {WHITE}{full_prompt}{RESET}")
        self._execute_generation(full_prompt, negative_prompt=neg_prompt)

    def _execute_generation(self, prompt: str, negative_prompt: Optional[str] = None) -> None:
        """Perform API call and save generated image."""
        m_short = self.current_model.split("/")[-1]
        print(f"\n{CF_ORANGE}Rendering on Cloudflare Serverless GPUs via {m_short}...{RESET}")
        print(f"{DARK_GRAY}Steps: {self.steps} | Prompt: {prompt[:65]}...{RESET}\n")

        start_time = time.time()
        img_bytes, elapsed, err = self.client.generate_image(
            prompt=prompt,
            model=self.current_model,
            steps=self.steps,
            negative_prompt=negative_prompt
        )

        if err or not img_bytes:
            print(f"{CRIMSON}✗ Generation failed: {err}{RESET}\n")
            input(f"{AMBER}Press Enter to return...{RESET}")
            return

        # Save to disk
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = sanitize_filename(prompt, 30)
        filename = f"{m_short}_{timestamp}_{slug}.png"
        filepath = self.output_dir / filename

        filepath.write_bytes(img_bytes)
        file_size_kb = len(img_bytes) / 1024

        print(f"{GREEN}{BOLD}✓ Image successfully generated!{RESET}")
        print(f"  {BOLD}Saved File:{RESET}   {WHITE}{filepath}{RESET}")
        print(f"  {BOLD}File Size:{RESET}    {CYAN}{file_size_kb:.1f} KB{RESET}")
        print(f"  {BOLD}Render Time:{RESET}  {GOLD}{elapsed:.2f} seconds{RESET}\n")

        # Auto-open
        if self.settings.get("auto_open_images", True):
            open_image(filepath)

        input(f"{AMBER}Press Enter to continue...{RESET}")

    def _select_model(self) -> None:
        """Switch active image model."""
        print(f"\n{GOLD}{BOLD}Available Cloudflare Image Models:{RESET}")
        for idx, m in enumerate(AVAILABLE_IMAGE_MODELS, 1):
            is_active = " (Active)" if m["id"] == self.current_model else ""
            print(f"  {CYAN}[{idx}]{RESET} {WHITE}{m['name']}{is_active}{RESET}")
            print(f"      {DARK_GRAY}{m['desc']}{RESET}")

        choice = input(f"\n{AMBER}Select model number: {RESET}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(AVAILABLE_IMAGE_MODELS):
            selected = AVAILABLE_IMAGE_MODELS[int(choice) - 1]
            self.current_model = selected["id"]
            self.steps = selected["steps"]
            self.settings["default_image_model"] = self.current_model
            self.settings["image_steps"] = self.steps
            save_settings(self.settings)
            print(f"{GREEN}✓ Switched to {selected['name']} (Default steps: {self.steps}){RESET}\n")

    def _configure_parameters(self) -> None:
        """Adjust steps, output directory, and auto-open."""
        print(f"\n{GOLD}{BOLD}Studio Configuration:{RESET}")
        print(f"  1. Steps:           {WHITE}{self.steps}{RESET}")
        print(f"  2. Output Directory: {WHITE}{self.output_dir}{RESET}")
        print(f"  3. Auto-Open Image: {WHITE}{self.settings.get('auto_open_images', True)}{RESET}")

        c = input(f"\n{AMBER}Select setting to change [1-3, or Enter to return]: {RESET}").strip()
        if c == "1":
            val = input(f"{AMBER}Enter steps [1-30]: {RESET}").strip()
            if val.isdigit():
                self.steps = int(val)
                self.settings["image_steps"] = self.steps
                save_settings(self.settings)
                print(f"{GREEN}✓ Steps updated.{RESET}\n")
        elif c == "2":
            new_dir = input(f"{AMBER}New output directory path: {RESET}").strip()
            if new_dir:
                self.output_dir = Path(new_dir)
                self.output_dir.mkdir(parents=True, exist_ok=True)
                self.settings["image_dir"] = str(self.output_dir)
                save_settings(self.settings)
                print(f"{GREEN}✓ Output directory updated.{RESET}\n")
        elif c == "3":
            cur = self.settings.get("auto_open_images", True)
            self.settings["auto_open_images"] = not cur
            save_settings(self.settings)
            print(f"{GREEN}✓ Auto-open set to {not cur}{RESET}\n")

    def _browse_gallery(self) -> None:
        """Browse recent images in output directory."""
        images = sorted(list(self.output_dir.glob("*.png")) + list(self.output_dir.glob("*.jpg")), key=lambda p: p.stat().st_mtime, reverse=True)
        if not images:
            print(f"\n{AMBER}No images found in {self.output_dir}{RESET}\n")
            input(f"{AMBER}Press Enter to return...{RESET}")
            return

        print_header("GENERATED IMAGES GALLERY", f"{len(images)} Images Found")
        for idx, img in enumerate(images[:15], 1):
            mtime = datetime.fromtimestamp(img.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            size_kb = img.stat().st_size / 1024
            print(f"  {CYAN}[{idx:2d}]{RESET} {WHITE}{img.name[:45]:<48}{RESET} {DARK_GRAY}{size_kb:6.1f} KB | {mtime}{RESET}")

        sel = input(f"\n{AMBER}Enter number to view image (or Enter to return): {RESET}").strip()
        if sel.isdigit() and 1 <= int(sel) <= min(15, len(images)):
            target_img = images[int(sel) - 1]
            print(f"{GREEN}Opening {target_img.name}...{RESET}")
            open_image(target_img)
