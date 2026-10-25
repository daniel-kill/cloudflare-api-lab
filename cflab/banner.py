"""
Terminal styling, ANSI colors, Cloudflare branding, ASCII logo, and layout helpers.
"""

import os
import sys

# Color Palette (Cloudflare Orange / Amber / Cyan / Gray)
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
ITALIC = '\033[3m'
UNDERLINE = '\033[4m'

# Colors
CF_ORANGE = '\033[38;5;208m'
AMBER = '\033[38;5;214m'
GOLD = '\033[38;5;220m'
CYAN = '\033[38;5;51m'
BLUE = '\033[38;5;39m'
TEAL = '\033[38;5;44m'
GREEN = '\033[38;5;82m'
PURPLE = '\033[38;5;141m'
CRIMSON = '\033[38;5;196m'
ROSE = '\033[38;5;204m'
GRAY = '\033[38;5;244m'
DARK_GRAY = '\033[38;5;238m'
WHITE = '\033[38;5;255m'

ASCII_LOGO = f"""{CF_ORANGE}{BOLD}
   ____ _                 _  __ _                 
  / ___| | ___  _   _  __| |/ _| | __ _ _ __ ___  
 | |   | |/ _ \\| | | |/ _` | |_| |/ _` | '__/ _ \\ 
 | |___| | (_) | |_| | (_| |  _| | (_| | | |  __/ 
  \\____|_|\\___/ \\__,_|\\__,_|_| |_|\\__,_|_|  \\___| 
     _    ____ ___   _          _     
    / \\  |  _ \\_ _| | |    __ _| |__  
   / _ \\ | |_) | |  | |   / _` | '_ \\ 
  / ___ \\|  __/| |  | |__| (_| | |_) |
 /_/   \\_\\_|  |___| |_____\\__,_|_.__/ {RESET}
{AMBER}{BOLD}  ☁️  Workers AI & Edge Cloud Platform Laboratory  ☁️{RESET}
{GRAY}  Maintained by Daniel Kill <daniel@danielkill.online>{RESET}
"""

def clear_screen() -> None:
    """Clear terminal screen cross-platform."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def print_banner(
    account_info: dict | None = None,
    current_model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
) -> None:
    """Print the application banner with status bar."""
    print(ASCII_LOGO)

    status_parts = []
    status_parts.append(f"{CF_ORANGE}{BOLD}[☁️ Cloudflare]{RESET}")

    if account_info and account_info.get("valid"):
        acc_name = account_info.get("account_name", "Account")
        if len(acc_name) > 28:
            acc_name = acc_name[:25] + "..."
        status_parts.append(f"{WHITE}{acc_name}{RESET}")
        status_parts.append(f"{GREEN}● Workers AI Operational{RESET}")
    else:
        status_parts.append(f"{AMBER}Edge API Ready{RESET}")

    # Model name
    m_short = current_model.split("/")[-1]
    status_parts.append(f"{CYAN}Model:{RESET} {WHITE}{m_short}{RESET}")

    bar = f"{DARK_GRAY}───┤ {RESET}" + f" {DARK_GRAY}|{RESET} ".join(status_parts) + f" {DARK_GRAY}├───{RESET}"
    print(bar)
    print()

def print_header(title: str, subtitle: str = "") -> None:
    """Print section header with accented box."""
    print()
    print(f"{CF_ORANGE}{BOLD}┌──[ {AMBER}{title}{CF_ORANGE} ]{RESET}")
    if subtitle:
        print(f"{CF_ORANGE}│  {GRAY}{subtitle}{RESET}")
    print(f"{CF_ORANGE}└───{RESET}")

def print_box(text: str, title: str = "", border_color: str = CF_ORANGE) -> None:
    """Print text inside terminal box."""
    lines = text.split('\n')
    max_len = max(len(line) for line in lines) if lines else 40
    if title:
        max_len = max(max_len, len(title) + 6)
    width = max_len + 4

    top = f"{border_color}┌"
    if title:
        top += f"─[ {BOLD}{WHITE}{title}{RESET}{border_color} ]"
        top += "─" * (width - len(title) - 6) + "┐"
    else:
        top += "─" * (width - 1) + "┐"

    print(top + RESET)
    for line in lines:
        padding = " " * (width - len(line) - 3)
        print(f"{border_color}│{RESET}  {line}{padding}{border_color}│{RESET}")
    print(f"{border_color}└" + "─" * (width - 1) + f"┘{RESET}")

def print_divider(label: str = "") -> None:
    """Print horizontal divider line."""
    if label:
        print(f"\n{DARK_GRAY}──────[ {AMBER}{label}{DARK_GRAY} ]" + "─" * 40 + f"{RESET}\n")
    else:
        print(f"{DARK_GRAY}" + "─" * 60 + f"{RESET}")
