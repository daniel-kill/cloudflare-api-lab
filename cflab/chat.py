"""
Interactive Multi-Turn Streaming Chat REPL for Cloudflare Workers AI.
Supports Llama 3.3 70B, DeepSeek R1, GPT-OSS 120B, expert personas, and in-chat image rendering.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .banner import (
    RESET, BOLD, DIM, CYAN, AMBER, CF_ORANGE, GOLD, GREEN, PURPLE, GRAY, WHITE, DARK_GRAY, CRIMSON,
    print_header, print_divider
)
from .client import CloudflareClient
from .personas import PERSONAS
from .config import load_settings

class ChatSession:
    def __init__(
        self,
        client: CloudflareClient,
        model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        persona_key: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        self.client = client
        self.model = model
        self.persona_key = persona_key
        self.system_prompt = PERSONAS.get(persona_key, PERSONAS["default"])["prompt"]
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, str]] = []
        self.session_start = datetime.now()
        self.total_tokens_generated = 0
        self.total_turns = 0
        self.settings = load_settings()

    def start(self, account_info: Optional[Dict[str, Any]] = None) -> None:
        """Start the interactive chat loop."""
        p_info = PERSONAS.get(self.persona_key, PERSONAS["default"])
        m_short = self.model.split("/")[-1]

        print_header("WORKERS AI CHAT SESSION", f"Model: {m_short} | Persona: {p_info['icon']} {p_info['name']}")
        print(f"{DARK_GRAY}Type your message and press Enter. Available commands:{RESET}")
        print(f"  {CYAN}/m{RESET} or {CYAN}/model{RESET}     - Switch LLM model           {CYAN}/image{RESET} [prompt]  - Generate an image right in chat")
        print(f"  {CYAN}/p{RESET} or {CYAN}/persona{RESET}   - Change persona             {CYAN}/c{RESET} or {CYAN}/clear{RESET}     - Clear chat history")
        print(f"  {CYAN}/s{RESET} or {CYAN}/system{RESET}    - Edit system prompt         {CYAN}/save{RESET}            - Save transcript to disk")
        print(f"  {CYAN}/params{RESET} [temp]  - Adjust sampling temp       {CYAN}/stats{RESET}           - View generation metrics")
        print(f"  {CYAN}/help{RESET}             - Detailed command manual    {CYAN}/q{RESET} or {CYAN}/exit{RESET}     - Return to main menu")
        print_divider()

        while True:
            try:
                prompt_label = f"{CF_ORANGE}{BOLD}You [{m_short}]{RESET}{CYAN} ❯ {RESET}"
                user_input = input(prompt_label).strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{GRAY}Session ended by user.{RESET}")
                break

            if not user_input:
                continue

            # Command handling
            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

                if cmd in ("/exit", "/quit", "/q"):
                    print(f"{GRAY}Returning to Lab Menu...{RESET}")
                    break
                elif cmd in ("/help", "/h"):
                    self._show_help()
                    continue
                elif cmd in ("/clear", "/c"):
                    self.messages = []
                    self.total_turns = 0
                    print(f"{GREEN}✓ Chat history cleared.{RESET}\n")
                    continue
                elif cmd in ("/model", "/m"):
                    self._switch_model(arg)
                    m_short = self.model.split("/")[-1]
                    continue
                elif cmd in ("/persona", "/p"):
                    self._switch_persona(arg)
                    continue
                elif cmd in ("/system", "/s"):
                    self._edit_system_prompt(arg)
                    continue
                elif cmd == "/image":
                    self._generate_image_in_chat(arg)
                    continue
                elif cmd == "/save":
                    self._save_transcript(arg)
                    continue
                elif cmd == "/stats":
                    self._show_stats()
                    continue
                elif cmd == "/params":
                    self._adjust_parameters(arg)
                    continue
                else:
                    print(f"{CRIMSON}Unknown command: {cmd}. Type /help for options.{RESET}\n")
                    continue

            # Execute user prompt
            self._send_message(user_input)

    def _send_message(self, text: str) -> None:
        """Send message to model and stream response."""
        self.messages.append({"role": "user", "content": text})
        self.total_turns += 1

        full_payload = [{"role": "system", "content": self.system_prompt}] + self.messages
        m_short = self.model.split("/")[-1]

        print(f"\n{CF_ORANGE}{BOLD}Assistant ({m_short}){RESET}:")
        full_response = ""
        start_time = time.time()

        try:
            for chunk in self.client.stream_chat(
                messages=full_payload,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            ):
                full_response += chunk
                sys.stdout.write(chunk)
                sys.stdout.flush()
        except KeyboardInterrupt:
            print(f"\n{AMBER}[Generation interrupted by user]{RESET}")

        elapsed = time.time() - start_time
        print("\n")

        approx_tokens = len(full_response.split()) * 1.3
        self.total_tokens_generated += approx_tokens
        speed = (approx_tokens / elapsed) if elapsed > 0 else 0

        spd_color = GREEN if speed > 60 else (CYAN if speed > 30 else DARK_GRAY)
        print(f"{DARK_GRAY}[⏱️ {elapsed:.2f}s | ~{int(approx_tokens)} tokens | {spd_color}{speed:.1f} tok/s{DARK_GRAY}]{RESET}\n")
        self.messages.append({"role": "assistant", "content": full_response})

    def _generate_image_in_chat(self, prompt: str) -> None:
        """Trigger instant image generation without leaving chat."""
        if not prompt:
            prompt = input(f"{AMBER}Enter image prompt: {RESET}").strip()
            if not prompt:
                return

        img_model = self.settings.get("default_image_model", "@cf/black-forest-labs/flux-1-schnell")
        m_short = img_model.split("/")[-1]

        print(f"\n{CF_ORANGE}🎨 Rendering image via {m_short}...{RESET}")
        img_bytes, elapsed, err = self.client.generate_image(prompt, model=img_model, steps=4)

        if err or not img_bytes:
            print(f"{CRIMSON}Image generation failed: {err}{RESET}\n")
            return

        out_dir = Path(self.settings.get("image_dir", Path.home() / ".cflab" / "generated_images"))
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = out_dir / f"chat_render_{stamp}.png"
        filepath.write_bytes(img_bytes)

        print(f"{GREEN}✓ Image rendered in {elapsed:.2f}s! Saved to: {filepath}{RESET}\n")
        if self.settings.get("auto_open_images", True):
            try:
                import os
                if sys.platform == "win32":
                    os.startfile(filepath)
            except Exception:
                pass

    def _switch_model(self, model_id: str) -> None:
        """Switch active LLM model."""
        if not model_id:
            models = self.client.get_models(task="Text Generation")
            print(f"\n{GOLD}{BOLD}Available Cloudflare Text Generation Models:{RESET}")
            for idx, m in enumerate(models[:12], 1):
                print(f"  [{idx:2d}] {m.name} ({m.id}) - {m.formatted_ctx}")
            sel = input(f"\n{AMBER}Select number or type model ID: {RESET}").strip()
            if sel.isdigit() and 1 <= int(sel) <= min(12, len(models)):
                self.model = models[int(sel) - 1].id
                print(f"{GREEN}✓ Model set to: {self.model}{RESET}\n")
            elif sel:
                self.model = sel
                print(f"{GREEN}✓ Model set to: {self.model}{RESET}\n")
            return

        self.model = model_id
        print(f"{GREEN}✓ Switched model to: {self.model}{RESET}\n")

    def _switch_persona(self, persona_name: str) -> None:
        """Switch persona."""
        if not persona_name:
            print(f"\n{GOLD}{BOLD}Available Personas:{RESET}")
            for key, p in PERSONAS.items():
                print(f"  {CYAN}{key:<12}{RESET} {p['icon']} {WHITE}{p['name']:<24}{RESET} {GRAY}{p['desc']}{RESET}")
            sel = input(f"\n{AMBER}Select persona key (default: default): {RESET}").strip().lower()
            persona_name = sel or "default"

        if persona_name in PERSONAS:
            self.persona_key = persona_name
            self.system_prompt = PERSONAS[persona_name]["prompt"]
            p = PERSONAS[persona_name]
            print(f"{GREEN}✓ Activated persona: {p['icon']} {p['name']}{RESET}\n")
        else:
            print(f"{CRIMSON}Persona '{persona_name}' not found.{RESET}\n")

    def _edit_system_prompt(self, new_prompt: str) -> None:
        """Update system prompt."""
        if not new_prompt:
            print(f"\n{GOLD}Current System Prompt:{RESET}\n{DARK_GRAY}{self.system_prompt}{RESET}\n")
            new_prompt = input(f"{AMBER}Enter new system prompt: {RESET}").strip()
            if not new_prompt:
                return

        self.system_prompt = new_prompt
        print(f"{GREEN}✓ Custom system prompt set.{RESET}\n")

    def _adjust_parameters(self, arg: str) -> None:
        """Adjust temperature."""
        if not arg:
            print(f"\nCurrent Temperature: {self.temperature}")
            val = input(f"{AMBER}New Temperature [0.0 - 1.5]: {RESET}").strip()
            if val:
                try:
                    self.temperature = max(0.0, min(1.5, float(val)))
                    print(f"{GREEN}✓ Temperature set to {self.temperature}{RESET}\n")
                except ValueError:
                    print(f"{CRIMSON}Invalid float.{RESET}\n")
            return

        try:
            self.temperature = max(0.0, min(1.5, float(arg)))
            print(f"{GREEN}✓ Temperature set to {self.temperature}{RESET}\n")
        except ValueError:
            print(f"{CRIMSON}Invalid float.{RESET}\n")

    def _show_stats(self) -> None:
        """Show conversation statistics."""
        elapsed = (datetime.now() - self.session_start).total_seconds()
        print(f"\n{BOLD}{GOLD}Session Analytics:{RESET}")
        print(f"  Active Model:      {WHITE}{self.model}{RESET}")
        print(f"  Persona:           {WHITE}{self.persona_key}{RESET}")
        print(f"  Duration:          {WHITE}{int(elapsed // 60)}m {int(elapsed % 60)}s{RESET}")
        print(f"  Dialogue Turns:    {WHITE}{self.total_turns}{RESET}")
        print(f"  Generated Tokens:  {WHITE}~{int(self.total_tokens_generated)}{RESET}")
        print(f"  Context Messages:  {WHITE}{len(self.messages)}{RESET}\n")

    def _save_transcript(self, custom_filename: str) -> None:
        """Export session dialogue to Markdown."""
        save_dir = Path.home() / ".cflab" / "transcripts"
        save_dir.mkdir(parents=True, exist_ok=True)

        if custom_filename:
            if not custom_filename.endswith(".md"):
                custom_filename += ".md"
            filepath = save_dir / custom_filename
        else:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            m_slug = self.model.replace("@cf/", "").replace("/", "_")
            filepath = save_dir / f"cf_chat_{m_slug}_{stamp}.md"

        content = [
            f"# Cloudflare Workers AI Chat Transcript",
            f"- **Model:** `{self.model}`",
            f"- **Persona:** {self.persona_key}",
            f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "---",
            "## System Prompt",
            f"```text\n{self.system_prompt}\n```\n",
            "## Dialogue\n"
        ]

        for msg in self.messages:
            role_header = "### 👤 User" if msg["role"] == "user" else f"### 🤖 Assistant ({self.model})"
            content.append(f"{role_header}\n\n{msg['content']}\n")

        filepath.write_text("\n".join(content), encoding="utf-8")
        print(f"{GREEN}✓ Transcript saved to: {filepath}{RESET}\n")

    def _show_help(self) -> None:
        """Display slash commands manual."""
        print(f"\n{BOLD}{GOLD}Workers AI Chat Command Guide:{RESET}")
        print(f"  {CYAN}/model [id]{RESET}      - Switch to another model (e.g. @cf/meta/llama-3.1-8b-instruct)")
        print(f"  {CYAN}/image [prompt]{RESET}  - Generate an image instantly with FLUX.1 or SDXL")
        print(f"  {CYAN}/persona [name]{RESET}  - Switch persona (default, architect, visionary, secops, dracula, oracle)")
        print(f"  {CYAN}/system [text]{RESET}   - Set a custom system instruction")
        print(f"  {CYAN}/params [temp]{RESET}   - Adjust temperature (0.0 to 1.5, e.g. /params 0.2)")
        print(f"  {CYAN}/clear{RESET}           - Erase conversation memory")
        print(f"  {CYAN}/save [filename]{RESET} - Export dialogue to a Markdown file")
        print(f"  {CYAN}/stats{RESET}          - Display tokens and timing statistics")
        print(f"  {CYAN}/exit{RESET} or {CYAN}/q{RESET}     - Return to the main menu\n")
