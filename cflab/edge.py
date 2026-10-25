"""
Cloudflare Edge Platform Explorer:
Inspect DNS Zones, Workers scripts, D1 databases, KV namespaces, R2 buckets, and AI Gateways.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from .banner import (
    RESET, BOLD, DIM, CYAN, AMBER, CF_ORANGE, GOLD, GREEN, PURPLE, GRAY, WHITE, DARK_GRAY, CRIMSON,
    print_header, print_divider
)
from .client import CloudflareClient

class EdgeExplorer:
    def __init__(self, client: CloudflareClient):
        self.client = client

    def run(self) -> None:
        """Interactive Edge Platform Explorer loop."""
        while True:
            print_header("CLOUDFLARE EDGE CLOUD EXPLORER", "Inspect & manage serverless edge architecture")
            print(f"  {CYAN}[1]{RESET} 🌐 DNS Zones & Domain Management")
            print(f"  {CYAN}[2]{RESET} ⚡ Cloudflare Workers Scripts")
            print(f"  {CYAN}[3]{RESET} 🗄️  D1 Serverless SQLite Databases")
            print(f"  {CYAN}[4]{RESET} 🗝️  KV Key-Value Storage Namespaces")
            print(f"  {CYAN}[5]{RESET} 🪣  R2 Zero-Egress Object Storage Buckets")
            print(f"  {CYAN}[6]{RESET} 🌉 AI Gateways (Observability & Caching)")
            print(f"  {CYAN}[7]{RESET} 📜 Generate Workers AI Edge Script Template")
            print(f"  {CYAN}[0]{RESET} Back to Main Menu")

            choice = input(f"\n{AMBER}Select Edge Service [0-7]: {RESET}").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._inspect_zones()
            elif choice == "2":
                self._inspect_workers()
            elif choice == "3":
                self._inspect_d1()
            elif choice == "4":
                self._inspect_kv()
            elif choice == "5":
                self._inspect_r2()
            elif choice == "6":
                self._inspect_ai_gateways()
            elif choice == "7":
                self._generate_worker_template()
            else:
                print(f"{CRIMSON}Invalid choice.{RESET}")

    def _inspect_zones(self) -> None:
        """Inspect DNS Zones."""
        print_header("DNS ZONES & DOMAINS", "Live from Cloudflare /zones")
        zones = self.client.get_zones()
        if not zones:
            print(f"  {GRAY}No DNS zones configured under this account yet.{RESET}")
            print(f"  {DARK_GRAY}Tip: You can add danielkill.online to Cloudflare to enable global CDN & edge rules.{RESET}\n")
            input(f"{AMBER}Press Enter to return...{RESET}")
            return

        for idx, z in enumerate(zones, 1):
            name = z.get("name", "Unknown")
            status = z.get("status", "unknown")
            zid = z.get("id", "")
            plan = z.get("plan", {}).get("name", "Free")
            ns = ", ".join(z.get("name_servers", []))
            s_color = GREEN if status == "active" else AMBER
            print(f"  {CYAN}[{idx}]{RESET} {BOLD}{WHITE}{name}{RESET} (Plan: {plan})")
            print(f"      Status: {s_color}{status}{RESET} | Zone ID: {DARK_GRAY}{zid}{RESET}")
            print(f"      Nameservers: {GRAY}{ns}{RESET}\n")

        input(f"{AMBER}Press Enter to return...{RESET}")

    def _inspect_workers(self) -> None:
        """Inspect Workers scripts."""
        print_header("CLOUDFLARE WORKERS", "Serverless V8 compute at the edge")
        workers = self.client.get_workers()
        if not workers:
            print(f"  {GRAY}No Worker scripts deployed under this account yet.{RESET}")
            print(f"  {DARK_GRAY}Workers allow executing JavaScript/TypeScript or Python across 300+ data centers.{RESET}\n")
        else:
            for idx, w in enumerate(workers, 1):
                wid = w.get("id", "")
                mod = w.get("modified_on", "")
                created = w.get("created_on", "")
                print(f"  {CYAN}[{idx}]{RESET} {BOLD}{WHITE}{wid}{RESET}")
                print(f"      Modified: {DARK_GRAY}{mod}{RESET} | Created: {DARK_GRAY}{created}{RESET}\n")

        input(f"{AMBER}Press Enter to return...{RESET}")

    def _inspect_d1(self) -> None:
        """Inspect D1 databases."""
        print_header("D1 SERVERLESS SQLITE", "Edge databases with zero cold-starts")
        dbs = self.client.get_d1_databases()
        if not dbs:
            print(f"  {GRAY}No D1 databases created under this account yet.{RESET}")
            print(f"  {DARK_GRAY}D1 provides serverless SQLite distributed across Cloudflare's network.{RESET}\n")
        else:
            for idx, db in enumerate(dbs, 1):
                name = db.get("name", "")
                uuid = db.get("uuid", "")
                version = db.get("version", "")
                print(f"  {CYAN}[{idx}]{RESET} {BOLD}{WHITE}{name}{RESET} (UUID: {DARK_GRAY}{uuid}{RESET}, Version: {version})")

        input(f"{AMBER}Press Enter to return...{RESET}")

    def _inspect_kv(self) -> None:
        """Inspect KV namespaces."""
        print_header("WORKERS KV", "Ultra-low latency global key-value data storage")
        kvs = self.client.get_kv_namespaces()
        if not kvs:
            print(f"  {GRAY}No KV namespaces created under this account yet.{RESET}\n")
        else:
            for idx, kv in enumerate(kvs, 1):
                title = kv.get("title", "")
                kvid = kv.get("id", "")
                print(f"  {CYAN}[{idx}]{RESET} {BOLD}{WHITE}{title}{RESET} (ID: {DARK_GRAY}{kvid}{RESET})")

        input(f"{AMBER}Press Enter to return...{RESET}")

    def _inspect_r2(self) -> None:
        """Inspect R2 storage buckets."""
        print_header("R2 OBJECT STORAGE", "S3-compatible storage with zero egress fees")
        buckets = self.client.get_r2_buckets()
        if not buckets:
            print(f"  {GRAY}No R2 storage buckets created under this account yet.{RESET}\n")
        else:
            for idx, b in enumerate(buckets, 1):
                name = b.get("name", "")
                created = b.get("creation_date", "")
                print(f"  {CYAN}[{idx}]{RESET} {BOLD}{WHITE}{name}{RESET} (Created: {DARK_GRAY}{created}{RESET})")

        input(f"{AMBER}Press Enter to return...{RESET}")

    def _inspect_ai_gateways(self) -> None:
        """Inspect AI Gateways."""
        print_header("AI GATEWAYS", "Analytics, caching, and rate limiting for AI models")
        gateways = self.client.get_ai_gateways()
        if not gateways:
            print(f"  {GRAY}No AI Gateways created under this account yet.{RESET}\n")
        else:
            for idx, gw in enumerate(gateways, 1):
                gid = gw.get("id", "")
                print(f"  {CYAN}[{idx}]{RESET} {BOLD}{WHITE}{gid}{RESET}")

        input(f"{AMBER}Press Enter to return...{RESET}")

    def _generate_worker_template(self) -> None:
        """Generate and save an example Workers AI edge script."""
        template = """/**
 * Cloudflare Worker: Serverless AI Endpoint
 * Deployed to Cloudflare's edge network with access to Workers AI.
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. Text Generation Endpoint
    if (url.pathname === "/api/chat") {
      const { prompt } = await request.json();
      const response = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", {
        messages: [{ role: "user", content: prompt || "Hello from Workers AI!" }]
      });
      return Response.json(response);
    }

    // 2. Image Generation Endpoint (FLUX.1-schnell)
    if (url.pathname === "/api/image") {
      const { prompt } = await request.json();
      const imageBytes = await env.AI.run("@cf/black-forest-labs/flux-1-schnell", {
        prompt: prompt || "A cybernetic falcon soaring over neon clouds",
        steps: 4
      });
      return new Response(imageBytes, {
        headers: { "Content-Type": "image/png" }
      });
    }

    return new Response("Cloudflare Workers AI Endpoint Active. Query /api/chat or /api/image.", {
      headers: { "Content-Type": "text/plain" }
    });
  }
};
"""
        out_path = Path("worker_ai_template.js")
        out_path.write_text(template, encoding="utf-8")
        print(f"\n{GREEN}✓ Generated Workers AI edge script: {out_path.resolve()}{RESET}\n")
        input(f"{AMBER}Press Enter to return...{RESET}")
