"""
Job Pilot – Naukri.com Automation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CLI entry-point that orchestrates login → search using
the modular-monolith architecture (Playwright + Firefox).

Usage
-----
    python main.py                  # uses config.yaml in project root
    python main.py --config my.yaml # custom config path
"""

from __future__ import annotations

import argparse
import sys

from config.settings import load_config
from browser.driver import create_browser
from auth.login import login
from search.job_search import search_jobs


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Job Pilot – automate Naukri.com login & job search",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a YAML config file (default: config.yaml in project root)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # ── 1. Load configuration ─────────────────────────────
    config = load_config(args.config)
    print(f"[main] Config loaded  (keywords={config.keywords}, "
          f"experience={config.experience}, location={config.location})")

    if not config.email or not config.password:
        print("[main] ❌ Email / password not set in config.yaml – aborting.")
        sys.exit(1)

    # ── 2. Create browser ─────────────────────────────────
    session = create_browser(config)

    try:
        # ── 3. Login ──────────────────────────────────────
        login(session.page, config)

        # ── 4. Search ─────────────────────────────────────
        all_jobs, ai_jobs = search_jobs(session.page, config)

        if all_jobs:
            print("\n[main] All jobs (in memory only):")
            for idx, job in enumerate(all_jobs, start=1):
                print(f"[main]   {idx}. {job.get('title', '')}")
                print(f"[main]       Company: {job.get('company', '')}")
                print(f"[main]       Location: {job.get('location', '')}")
                print(f"[main]       Experience: {job.get('experience', '')}")
                print(f"[main]       Tags: {job.get('tags', '')}")
                print(f"[main]       Link: {job.get('link', '')}")

        if ai_jobs:
            print("\n[main] AI-related jobs (in memory only):")
            for idx, job in enumerate(ai_jobs, start=1):
                print(f"[main]   {idx}. {job.get('title', '')}")
                print(f"[main]       Company: {job.get('company', '')}")
                print(f"[main]       Location: {job.get('location', '')}")
                print(f"[main]       Experience: {job.get('experience', '')}")
                print(f"[main]       Tags: {job.get('tags', '')}")
                print(f"[main]       Link: {job.get('link', '')}")
                if config.auto_apply:
                    print(f"[main]       Apply status: {job.get('apply_status', '')}")
        else:
            print("\n[main] No AI-related jobs found.")

        # Keep the browser open so the user can inspect results
        print("\n[main] ✅ Done!  The browser will stay open.")
        print("[main] Press Enter to close the browser …")
        input()

    except KeyboardInterrupt:
        print("\n[main] Interrupted by user.")
    except Exception as exc:
        print(f"\n[main] ❌ Error: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
