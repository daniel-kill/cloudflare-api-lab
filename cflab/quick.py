"""
Quick single prompt runner with streaming for Cloudflare Workers AI.
"""

import sys
import time
from typing import Optional

from .banner import (
    RESET, BOLD, CYAN, AMBER, CF_ORANGE, GOLD, GREEN, GRAY, WHITE, DARK_GRAY,
    print_header
)
from .client import CloudflareClient

def run_quick_prompt(
    client: CloudflareClient,
    prompt: Optional[str] = None,
    model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    system_prompt: Optional[str] = None,
    temperature: float = 0.7
) -> None:
    """Execute a single prompt and stream response to stdout."""
    if not prompt:
        m_short = model.split("/")[-1]
        print_header("QUICK SINGLE PROMPT", f"Target: {m_short}")
        try:
            prompt = input(f"{AMBER}Enter your prompt: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            return

    if not prompt:
        return

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    m_short = model.split("/")[-1]
    print(f"\n{DARK_GRAY}───────────────────────────────────────────────────────────{RESET}")
    print(f"{CF_ORANGE}{BOLD}Model:{RESET} {WHITE}{m_short}{RESET} ({model}) | {CYAN}Temp:{RESET} {temperature}")
    print(f"{DARK_GRAY}───────────────────────────────────────────────────────────{RESET}\n")

    start_time = time.time()
    total_text = ""

    try:
        for chunk in client.stream_chat(messages, model=model, temperature=temperature):
            total_text += chunk
            sys.stdout.write(chunk)
            sys.stdout.flush()
    except KeyboardInterrupt:
        print(f"\n{AMBER}[Stream interrupted by user]{RESET}")

    elapsed = time.time() - start_time
    approx_tokens = int(len(total_text.split()) * 1.3)
    speed = (approx_tokens / elapsed) if elapsed > 0 else 0

    spd_color = GREEN if speed > 60 else (CYAN if speed > 30 else DARK_GRAY)
    print(f"\n\n{DARK_GRAY}[⏱️  {elapsed:.2f}s | ~{approx_tokens} tokens | {spd_color}{speed:.1f} tok/s{DARK_GRAY}]{RESET}\n")
