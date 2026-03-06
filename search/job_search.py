"""
search.job_search
~~~~~~~~~~~~~~~~~~
Navigates directly to a Naukri.com job search results URL
constructed from the config values.
"""

from __future__ import annotations

from urllib.parse import quote

from playwright.sync_api import Page

from config.settings import AppConfig


def _build_search_url(config: AppConfig) -> str:
    """
    Build a Naukri search URL like:
    https://www.naukri.com/ai-engineer-jobs-in-remote?k=ai+engineer&l=remote&experience=0&jobAge=1
    """
    keyword = config.keywords[0] if config.keywords else ""
    location = config.location or "remote"

    # Slug for the path segment: "ai engineer" → "ai-engineer"
    kw_slug = keyword.lower().replace(" ", "-")
    loc_slug = location.lower().replace(" ", "-")

    # Query params
    k = quote(keyword.lower())
    l = quote(location.lower())

    url = (
        f"https://www.naukri.com/{kw_slug}-jobs-in-{loc_slug}"
        f"?k={k}&l={l}&experience={config.experience}"
    )

    if config.job_age:
        url += f"&jobAge={config.job_age}"

    return url


def _sort_by_date(page: Page) -> None:
    """Click the sort dropdown and select 'Date' to show newest first."""
    print("[search] Sorting by Date …")
    page.click("button#filter-sort")
    page.wait_for_timeout(800)
    page.click('li[title="Date"]')
    page.wait_for_timeout(2000)
    print("[search] ✅ Sorted by Date.")


def search_jobs(page: Page, config: AppConfig) -> None:
    """
    Navigate directly to the Naukri search results page,
    then sort results by Date.

    Prerequisites: browser must be logged in.
    """
    url = _build_search_url(config)
    print(f"[search] Navigating to: {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print("[search] ✅ Search results page loaded.")

    # Sort by date (newest first)
    _sort_by_date(page)
