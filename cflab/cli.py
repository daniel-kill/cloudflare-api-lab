"""
Command-line interface argument parsing for Cloudflare API Lab.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .banner import print_banner, clear_screen, GREEN, CRIMSON, CF_ORANGE, GOLD, WHITE, DARK_GRAY, RESET, BOLD
from .config import get_credentials, load_settings, save_settings
from .client import CloudflareClient
from .menu import run_main_menu, inspect_account_status
from .chat import ChatSession
from .image_studio import ImageStudio, open_image, sanitize_filename
from .vision import VisionLab
from .catalog import CatalogViewer
from .edge import EdgeExplorer
from .quick import run_quick_prompt
from .__init__ import __version__

def main() -> None:
    """Entry point for CLI commands and interactive laboratory menu."""
    parser = argparse.ArgumentParser(
        prog="cflab",
        description="Cloudflare API Lab — Terminal Laboratory & Developer Tool for Workers AI & Edge Cloud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cflab                                         Launch the interactive terminal menu
  cflab -p "What is Cloudflare Workers AI?"     Quick streaming text generation (Llama 3.3 70B)
  cflab --image "Gothic castle in misty rain"   Render image with FLUX.1-schnell in 3 seconds
  cflab --image "Cyberpunk dragon" --steps 4 -m "@cf/black-forest-labs/flux-1-schnell"
  cflab --vision photo.png -p "Describe this"   Multimodal image analysis (Llama 3.2 11B Vision)
  cflab --chat                                  Interactive streaming chat REPL
  cflab --studio                                Jump directly into Image Studio
  cflab --models                                List available Workers AI models
  cflab --account                               Inspect Cloudflare account and token status
  cflab --edge                                  Inspect DNS Zones, Workers, D1, KV, R2
        """
    )

    parser.add_argument("-p", "--prompt", type=str, help="Execute a single text prompt and exit")
    parser.add_argument("--image", type=str, help="Generate an image from prompt and save to disk")
    parser.add_argument("--vision", type=str, help="Analyze an image file path with multimodal vision")
    parser.add_argument("-m", "--model", type=str, default=None, help="Specify model ID (text or image)")
    parser.add_argument("--chat", action="store_true", help="Launch interactive multi-turn chat session directly")
    parser.add_argument("--studio", action="store_true", help="Launch interactive Image Studio directly")
    parser.add_argument("--models", action="store_true", help="Display all available Workers AI models")
    parser.add_argument("--account", action="store_true", help="Display account details and token status")
    parser.add_argument("--edge", action="store_true", help="Inspect edge services (Zones, Workers, D1, KV, R2)")
    parser.add_argument("--steps", type=int, default=4, help="Inference steps for image generation (1-30, default: 4)")
    parser.add_argument("--output", type=str, default=None, help="Output filepath for generated image")
    parser.add_argument("-t", "--temperature", type=float, default=None, help="Sampling temperature (0.0 to 1.5)")
    parser.add_argument("-s", "--system", type=str, default=None, help="Custom system prompt")
    parser.add_argument("-v", "--version", action="version", version=f"Cloudflare API Lab v{__version__}")

    args = parser.parse_args()

    account_id, api_token = get_credentials()
    if not account_id or not api_token:
        from .menu import prompt_credentials_setup
        creds = prompt_credentials_setup()
        if not creds:
            print(f"{CRIMSON}Exiting: Cloudflare Account ID and API Token required.{RESET}")
            sys.exit(1)
        account_id, api_token = creds["account_id"], creds["api_token"]

    client = CloudflareClient(account_id=account_id, api_token=api_token)
    settings = load_settings()

    target_text_model = args.model or settings.get("default_text_model", "@cf/meta/llama-3.3-70b-instruct-fp8-fast")
    target_img_model = args.model or settings.get("default_image_model", "@cf/black-forest-labs/flux-1-schnell")
    temp = args.temperature if args.temperature is not None else settings.get("temperature", 0.7)

    # 1. Image Generation Flag
    if args.image:
        print(f"\n{CF_ORANGE}🎨 Rendering on Cloudflare Workers AI ({target_img_model})...{RESET}")
        img_bytes, elapsed, err = client.generate_image(args.image, model=target_img_model, steps=args.steps)
        if err or not img_bytes:
            print(f"{CRIMSON}Error: {err}{RESET}")
            sys.exit(1)

        out_path = Path(args.output) if args.output else (Path(settings.get("image_dir", ".")) / f"cf_{sanitize_filename(args.image, 30)}.png")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(img_bytes)

        size_kb = len(img_bytes) / 1024
        print(f"{GREEN}✓ Image generated in {elapsed:.2f}s!{RESET}")
        print(f"  Saved to: {WHITE}{out_path.resolve()}{RESET} ({size_kb:.1f} KB)\n")
        if settings.get("auto_open_images", True):
            open_image(out_path)
        return

    # 2. Vision Analysis Flag
    if args.vision:
        v_path = Path(args.vision)
        if not v_path.exists():
            print(f"{CRIMSON}File not found: {args.vision}{RESET}")
            sys.exit(1)
        prompt = args.prompt or "Describe this image in detail."
        print(f"\n{CF_ORANGE}Analyzing image with Llama 3.2 11B Vision...{RESET}")
        desc, elapsed, err = client.analyze_image(v_path.read_bytes(), prompt=prompt)
        if err or not desc:
            print(f"{CRIMSON}Vision Error: {err}{RESET}")
            sys.exit(1)
        print(f"\n{WHITE}{desc.strip()}{RESET}\n")
        print(f"{DARK_GRAY}[⏱️  Latency: {elapsed:.2f}s]{RESET}\n")
        return

    # 3. Single Text Prompt Flag
    if args.prompt:
        run_quick_prompt(
            client=client,
            prompt=args.prompt,
            model=target_text_model,
            system_prompt=args.system or settings.get("system_prompt"),
            temperature=temp
        )
        return

    # 4. Account Verification Flag
    if args.account:
        inspect_account_status(client, wait_enter=False)
        return

    # 5. Models Catalog Flag
    if args.models:
        viewer = CatalogViewer(client)
        viewer.run()
        return

    # 6. Edge Explorer Flag
    if args.edge:
        explorer = EdgeExplorer(client)
        explorer.run()
        return

    # 7. Image Studio Flag
    if args.studio:
        studio = ImageStudio(client)
        studio.run()
        return

    # 8. Interactive Chat REPL Flag
    if args.chat:
        session = ChatSession(
            client=client,
            model=target_text_model,
            temperature=temp
        )
        session.start()
        return

    # Default: launch full interactive TUI menu
    run_main_menu()

if __name__ == "__main__":
    main()
