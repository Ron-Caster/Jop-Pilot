"""
search.job_search
~~~~~~~~~~~~~~~~~~
Automates the Naukri.com job-search flow using Playwright:
filling keywords, selecting experience, entering location,
and clicking Search.
"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import AppConfig

# ── Naukri DOM selectors (from CLAUDE.md) ────────────────────
_SEARCHBAR        = "div#ni-gnb-searchbar"
_KEYWORD_INPUT    = 'input.suggestor-input[placeholder*="keyword"]'
_EXPERIENCE_INPUT = "input#experienceDD"
_LOCATION_INPUT   = 'input.suggestor-input[placeholder="Enter location"]'
_SEARCH_BUTTON    = "button.nI-gNb-sb__icon-wrapper"


def _select_experience(page: Page, years: str) -> None:
    """Click the experience dropdown and pick the matching option."""
    page.click(_EXPERIENCE_INPUT)
    page.wait_for_timeout(800)

    target_text = f"{years} Year" if years != "0" else "Fresher"

    # Try to find and click the matching dropdown option
    options = page.query_selector_all("ul li, div.dropdownPrimary li")
    for opt in options:
        txt = (opt.inner_text() or "").strip()
        if txt.lower().startswith(target_text.lower()):
            opt.click()
            print(f"[search] Selected experience: {txt}")
            return

    print(f"[search] ⚠  Could not find experience '{years}' – skipping.")


def _enter_suggestor_value(page: Page, selector: str, value: str, label: str) -> None:
    """Type into a suggestor input and press Enter to accept."""
    page.click(selector)
    page.wait_for_timeout(300)
    page.fill(selector, value)
    page.wait_for_timeout(1200)       # wait for auto-suggest
    page.press(selector, "Enter")     # accept first suggestion
    print(f"[search] Entered {label}: {value}")


def search_jobs(page: Page, config: AppConfig) -> None:
    """
    Execute a job search on Naukri.com.

    Prerequisites: driver must be logged in and on the homepage.
    """
    # 1 ── Expand search bar ────────────────────────────────
    print("[search] Expanding search bar …")
    page.click(_SEARCHBAR)
    page.wait_for_timeout(1000)

    # 2 ── Enter keyword(s) ─────────────────────────────────
    keyword_str = ", ".join(config.keywords) if config.keywords else ""
    if keyword_str:
        _enter_suggestor_value(page, _KEYWORD_INPUT, keyword_str, "keyword")

    # 3 ── Select experience ────────────────────────────────
    if config.experience:
        _select_experience(page, config.experience)
        page.wait_for_timeout(500)

    # 4 ── Enter location ───────────────────────────────────
    if config.location:
        _enter_suggestor_value(page, _LOCATION_INPUT, config.location, "location")
        page.wait_for_timeout(500)

    # 5 ── Click Search ─────────────────────────────────────
    print("[search] Clicking Search …")
    page.click(_SEARCH_BUTTON)

    # Wait for results page
    page.wait_for_timeout(3000)
    print("[search] ✅ Search executed – results page loaded.")
