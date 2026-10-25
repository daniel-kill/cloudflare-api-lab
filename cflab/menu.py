"""
Main Interactive Terminal Menu Loop for Cloudflare API Lab.
"""

import os
import sys
import time
from typing import Dict, Any, Optional

from .banner import (
    RESET, BOLD, DIM, CYAN, AMBER, CF_ORANGE, GOLD, GREEN, PURPLE, GRAY, WHITE, DARK_GRAY, CRIMSON,
    print_banner, print_header, print_box, print_divider, clear_screen
)
from .client import CloudflareClient
from .config import (
    get_credentials,
    save_credentials_to_env,
    load_settings,
    save_settings
)
from .chat import ChatSession
from .image_studio import ImageStudio
from .vision import VisionLab
from .edge import EdgeExplorer
from .catalog import CatalogViewer
from .quick import run_quick_prompt

def prompt_credentials_setup() -> Optional[Dict[str, str]]:
    """Interactively guide user to provide Cloudflare credentials."""
    print_header("CLOUDFLARE CREDENTIALS SETUP", "Account ID and API Token required")
    print(f"{DARK_GRAY}Could not automatically discover CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN.{RESET}\n")
    print(f"You can create an API Token with full access at: {CYAN}https://dash.cloudflare.com/profile/api-tokens{RESET}\n")

    account_id = input(f"{AMBER}Enter Cloudflare Account ID: {RESET}").strip()
    api_token = input(f"{AMBER}Enter Cloudflare API Token: {RESET}").strip()

    if not account_id or not api_token:
        print(f"{CRIMSON}Both Account ID and API Token are required.{RESET}\n")
        return None

    save = input(f"{AMBER}Save credentials to ~/.cflab/.env for future sessions? [Y/n]: {RESET}").strip().lower()
    if save != "n":
        save_credentials_to_env(account_id, api_token)
        print(f"{GREEN}✓ Credentials saved to ~/.cflab/.env{RESET}\n")

    return {"account_id": account_id, "api_token": api_token}

def inspect_account_status(client: CloudflareClient, wait_enter: bool = True) -> None:
    """Display live account and API token details."""
    print_header("CLOUDFLARE ACCOUNT STATUS", "Live data from Cloudflare REST API")
    info = client.check_auth()

    if not info.get("valid"):
        print(f"  {CRIMSON}✗ Authentication Failed:{RESET} {info.get('error')}\n")
        if wait_enter:
            input(f"{AMBER}Press Enter to return...{RESET}")
        return

    masked_id = client.account_id[:6] + "..." + client.account_id[-4:]
    masked_tok = client.api_token[:6] + "..." + client.api_token[-4:]

    print()
    print(f"  {BOLD}Account Name:{RESET}      {WHITE}{info.get('account_name')}{RESET}")
    print(f"  {BOLD}Account ID:{RESET}        {CYAN}{masked_id}{RESET} ({client.account_id})")
    print(f"  {BOLD}Account Type:{RESET}      {PURPLE}{info.get('type', 'standard').title()}{RESET}")
    print(f"  {BOLD}API Token:{RESET}         {GRAY}{masked_tok}{RESET} (Account Scoped)")
    print(f"  {BOLD}Workers AI:{RESET}        {GREEN}Operational (Global Serverless GPU Edge){RESET}")
    print(f"  {BOLD}Created On:{RESET}        {DARK_GRAY}{info.get('created_on')}{RESET}\n")

    # Quick test of Workers AI
    models = client.get_models()
    print(f"  {BOLD}Workers AI Catalog:{RESET} {GOLD}{len(models)} Total Models Available{RESET}")
    t_models = len([m for m in models if m.task == 'Text Generation'])
    i_models = len([m for m in models if m.task == 'Text-to-Image'])
    v_models = len([m for m in models if m.task == 'Image-to-Text'])
    print(f"      • Text Generation:  {t_models} models")
    print(f"      • Text-to-Image:    {i_models} models (FLUX.1, SDXL)")
    print(f"      • Vision & OCR:     {v_models} models (Llama 3.2 Vision)\n")

    if wait_enter:
        input(f"{AMBER}Press Enter to return to menu...{RESET}")

def manage_settings(settings: Dict[str, Any], client: CloudflareClient) -> None:
    """Adjust settings interactively."""
    while True:
        print_header("LAB SETTINGS & DEFAULTS", "Configure default models and parameters")
        print(f"  {CYAN}[1]{RESET} Default Text Model:   {WHITE}{settings.get('default_text_model')}{RESET}")
        print(f"  {CYAN}[2]{RESET} Default Image Model:  {WHITE}{settings.get('default_image_model')}{RESET}")
        print(f"  {CYAN}[3]{RESET} Image Steps:          {WHITE}{settings.get('image_steps', 4)}{RESET}")
        print(f"  {CYAN}[4]{RESET} Temperature:          {WHITE}{settings.get('temperature')}{RESET}")
        print(f"  {CYAN}[5]{RESET} Auto-Open Images:     {WHITE}{settings.get('auto_open_images', True)}{RESET}")
        print(f"  {CYAN}[6]{RESET} System Prompt:        {GRAY}{settings.get('system_prompt')[:45]}...{RESET}")
        print(f"  {CYAN}[0]{RESET} Back to Main Menu")

        choice = input(f"\n{AMBER}Select option to edit [0-6]: {RESET}").strip()
        if choice == "0":
            break
        elif choice == "1":
            models = client.get_models(task="Text Generation")
            print(f"\n{GOLD}Choose Default Text Model:{RESET}")
            for i, m in enumerate(models[:10], 1):
                print(f"  [{i:2d}] {m.name} ({m.id})")
            c = input(f"\n{AMBER}Select number: {RESET}").strip()
            if c.isdigit() and 1 <= int(c) <= min(10, len(models)):
                settings["default_text_model"] = models[int(c) - 1].id
                save_settings(settings)
                print(f"{GREEN}✓ Default text model saved.{RESET}\n")
        elif choice == "2":
            models = client.get_models(task="Text-to-Image")
            print(f"\n{GOLD}Choose Default Image Model:{RESET}")
            for i, m in enumerate(models, 1):
                print(f"  [{i:2d}] {m.name} ({m.id})")
            c = input(f"\n{AMBER}Select number: {RESET}").strip()
            if c.isdigit() and 1 <= int(c) <= len(models):
                settings["default_image_model"] = models[int(c) - 1].id
                save_settings(settings)
                print(f"{GREEN}✓ Default image model saved.{RESET}\n")
        elif choice == "3":
            val = input(f"{AMBER}New Steps [1-30]: {RESET}").strip()
            if val.isdigit():
                settings["image_steps"] = int(val)
                save_settings(settings)
                print(f"{GREEN}✓ Steps saved.{RESET}\n")
        elif choice == "4":
            val = input(f"{AMBER}New Temperature [0.0 - 1.5]: {RESET}").strip()
            try:
                settings["temperature"] = max(0.0, min(1.5, float(val)))
                save_settings(settings)
                print(f"{GREEN}✓ Temperature saved.{RESET}\n")
            except ValueError:
                print(f"{CRIMSON}Invalid float.{RESET}\n")
        elif choice == "5":
            settings["auto_open_images"] = not settings.get("auto_open_images", True)
            save_settings(settings)
            print(f"{GREEN}✓ Auto-open set to {settings['auto_open_images']}{RESET}\n")
        elif choice == "6":
            val = input(f"{AMBER}New System Prompt: {RESET}").strip()
            if val:
                settings["system_prompt"] = val
                save_settings(settings)
                print(f"{GREEN}✓ System prompt saved.{RESET}\n")

def run_main_menu() -> None:
    """Launch the main terminal menu system."""
    account_id, api_token = get_credentials()
    if not account_id or not api_token:
        creds = prompt_credentials_setup()
        if not creds:
            print(f"{CRIMSON}Exiting: Cloudflare Account ID and API Token are required.{RESET}")
            sys.exit(1)
        account_id, api_token = creds["account_id"], creds["api_token"]

    client = CloudflareClient(account_id=account_id, api_token=api_token)
    settings = load_settings()

    # Initial auth query
    account_info = client.check_auth()

    while True:
        clear_screen()
        current_model = settings.get("default_text_model", "@cf/meta/llama-3.3-70b-instruct-fp8-fast")
        print_banner(account_info, current_model=current_model)

        print(f"{GOLD}{BOLD}LABORATORY OPERATIONS:{RESET}")
        print(f"  {CYAN}[1]{RESET} 💬  {WHITE}{BOLD}Workers AI Chat Session{RESET}         {GRAY}(Multi-turn conversation with Llama 3.3 70B & personas){RESET}")
        print(f"  {CYAN}[2]{RESET} 🎨  {WHITE}{BOLD}AI Image Studio{RESET}                 {GRAY}(Text-to-Image with FLUX.1-schnell, FLUX.2 & SDXL){RESET}")
        print(f"  {CYAN}[3]{RESET} 👁️   {WHITE}{BOLD}Vision Lab & OCR{RESET}                {GRAY}(Multimodal image analysis with Llama 3.2 11B Vision){RESET}")
        print(f"  {CYAN}[4]{RESET} ⚡  {WHITE}{BOLD}Quick Single Prompt{RESET}             {GRAY}(One-off streaming response with active model){RESET}")
        print(f"  {CYAN}[5]{RESET} 📜  {WHITE}{BOLD}Workers AI Models Catalog{RESET}       {GRAY}(Explore & search 73+ edge models across all tasks){RESET}")
        print(f"  {CYAN}[6]{RESET} 🌐  {WHITE}{BOLD}Edge Platform Explorer{RESET}          {GRAY}(Inspect DNS Zones, Workers, D1, KV, R2, AI Gateways){RESET}")
        print(f"  {CYAN}[7]{RESET} 🔑  {WHITE}{BOLD}Account & API Verification{RESET}      {GRAY}(Check account details, token validity, and edge status){RESET}")
        print(f"  {CYAN}[8]{RESET} ⚙️   {WHITE}{BOLD}Settings & Default Models{RESET}       {GRAY}(Configure default LLM, image model, steps, paths){RESET}")
        print(f"  {CYAN}[0]{RESET} 🚪  {GRAY}Exit Cloudflare API Lab{RESET}")
        print_divider()

        try:
            choice = input(f"{AMBER}{BOLD}Select Operation [0-8]: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{GRAY}Exiting Cloudflare API Lab. Goodbye!{RESET}")
            break

        if choice == "0":
            print(f"\n{GOLD}Thank you for using Cloudflare API Lab. Happy hacking! ☁️{RESET}\n")
            break
        elif choice == "1":
            session = ChatSession(
                client=client,
                model=current_model,
                temperature=settings.get("temperature", 0.7)
            )
            session.start(account_info)
        elif choice == "2":
            studio = ImageStudio(client=client)
            studio.run()
        elif choice == "3":
            lab = VisionLab(client=client)
            lab.run()
        elif choice == "4":
            run_quick_prompt(
                client=client,
                model=current_model,
                system_prompt=settings.get("system_prompt"),
                temperature=settings.get("temperature", 0.7)
            )
            input(f"{AMBER}Press Enter to return to menu...{RESET}")
        elif choice == "5":
            viewer = CatalogViewer(client=client)
            viewer.run()
        elif choice == "6":
            explorer = EdgeExplorer(client=client)
            explorer.run()
        elif choice == "7":
            inspect_account_status(client=client)
        elif choice == "8":
            manage_settings(settings, client)
        else:
            print(f"{CRIMSON}Invalid choice. Select 0 through 8.{RESET}")
            time.sleep(1)
