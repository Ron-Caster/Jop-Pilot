"""
search.job_search
~~~~~~~~~~~~~~~~~~
Navigates directly to a Naukri.com job search results URL
constructed from the config values.
"""

from __future__ import annotations

import re
from urllib.parse import quote, urljoin

from playwright.sync_api import Page

from config.settings import AppConfig


def _build_search_url(config: AppConfig) -> str:
    """
    Build a Naukri search URL like:
    https://www.naukri.com/ai-engineer-jobs-in-remote?k=ai+engineer&l=remote&experience=0&jobAge=1
    """
    keywords = config.keywords or [""]
    keyword_text = ", ".join([kw.strip() for kw in keywords if kw.strip()])
    if not keyword_text:
        keyword_text = ""
    location = (config.location or "").strip()

    # Slug for the path segment: "langchain, agentcore" → "langchain-agentcore"
    kw_slug = re.sub(r"[^a-z0-9]+", "-", keyword_text.lower()).strip("-")
    loc_slug = location.lower().replace(" ", "-") if location else ""

    # Query params
    params = []
    if keyword_text:
        params.append(f"k={quote(keyword_text.lower())}")
    if location:
        params.append(f"l={quote(location.lower())}")
    if config.experience:
        params.append(f"experience={config.experience}")
    if config.job_age:
        params.append(f"jobAge={config.job_age}")

    if location:
        url = f"https://www.naukri.com/{kw_slug}-jobs-in-{loc_slug}"
    else:
        url = f"https://www.naukri.com/{kw_slug}-jobs"

    if params:
        url += "?" + "&".join(params)

    return url


def _sort_by_date(page: Page) -> None:
    """Click the sort dropdown and select 'Date' to show newest first."""
    print("[search] Sorting by Date …")
    page.click("button#filter-sort")
    page.wait_for_timeout(800)
    page.click('li[title="Date"]')
    page.wait_for_timeout(2000)
    print("[search] ✅ Sorted by Date.")


_DEFAULT_AI_TERMS = [
    "ai",
    "artificial intelligence",
    "gen ai",
    "generative",
    "llm",
    "nlp",
    "machine learning",
    "ml",
    "python",
]


def _safe_text(el, selector: str) -> str:
    node = el.query_selector(selector)
    if not node:
        return ""
    return (node.inner_text() or "").strip()


def _safe_attr(el, selector: str, attr: str) -> str:
    node = el.query_selector(selector)
    if not node:
        return ""
    return (node.get_attribute(attr) or "").strip()


def _collect_all_jobs(page: Page) -> list[dict[str, str]]:
    """Collect all visible job cards from the results page."""
    try:
        page.wait_for_selector(
            "a.title[href], div.cust-job-tuple, div.srp-jobtuple-wrapper",
            timeout=15_000,
        )
    except Exception:
        return []

    jobs = page.evaluate(
        """
        () => {
            const anchors = Array.from(document.querySelectorAll('a.title[href]'));
            const results = [];
            const seen = new Set();

            for (const a of anchors) {
                const link = a.getAttribute('href') || '';
                if (!link || seen.has(link)) continue;
                seen.add(link);

                const card = a.closest('.cust-job-tuple')
                    || a.closest('.srp-jobtuple-wrapper')
                    || a.closest('article')
                    || a.parentElement;

                const getText = (sel) => {
                    const node = card ? card.querySelector(sel) : null;
                    return node ? (node.innerText || '').trim() : '';
                };

                const tags = card
                    ? Array.from(card.querySelectorAll('ul.tags-gt li'))
                        .map((li) => (li.innerText || '').trim())
                        .filter(Boolean)
                        .join(', ')
                    : '';

                results.push({
                    title: (a.innerText || '').trim(),
                    company: getText('a.comp-name, span.comp-name'),
                    location: getText('.loc span[title], .loc[title]'),
                    experience: getText('.exp span[title], .exp[title]'),
                    tags,
                    link,
                    text: card ? (card.innerText || '').trim() : (a.innerText || '').trim(),
                });
            }

            return results;
        }
        """
    )

    return jobs or []


def _filter_jobs_by_terms(
    jobs: list[dict[str, str]],
    terms: list[str],
) -> list[dict[str, str]]:
    normalized_terms = [t.strip().lower() for t in terms if t.strip()]
    if not normalized_terms:
        return []

    results: list[dict[str, str]] = []
    for job in jobs:
        text = (job.get("text", "") or "").lower()
        if any(term in text for term in normalized_terms):
            results.append(job)

    return results


def _has_selector(page: Page, selector: str) -> bool:
    return page.query_selector(selector) is not None


def _detect_apply_result(page: Page) -> str:
    if _has_selector(page, "div._chatBotContainer, div[id$='ChatbotContainer']"):
        return "Chatbot"
    if _has_selector(page, ".acp-header-container, .applied-job-content"):
        return "Applied"
    msg = page.query_selector("span.apply-message")
    if msg:
        text = (msg.inner_text() or "").lower()
        if "does not require you to apply again" in text:
            return "AlreadyApplied"
    if _has_selector(page, ".apply-status-header.red"):
        return "ApplyFailed"
    return "Unknown"


def _attempt_apply(page: Page) -> str:
    if _has_selector(page, "button#company-site-button"):
        return "CompanySite"

    if _has_selector(page, "button#walkin-button"):
        return "WalkIn"

    apply_button = page.query_selector("button#apply-button")
    if not apply_button:
        return "ApplyNotFound"

    try:
        apply_button.click(timeout=10_000)
    except Exception:
        return "ApplyClickFailed"
    page.wait_for_timeout(2000)

    result = _detect_apply_result(page)
    if result != "Unknown":
        return result

    # Wait a bit longer for slow post-apply pages
    for _ in range(3):
        page.wait_for_timeout(1000)
        result = _detect_apply_result(page)
        if result != "Unknown":
            return result

    return "Unknown"


def apply_to_jobs(
    page: Page,
    jobs: list[dict[str, str]],
    config: AppConfig,
) -> list[dict[str, str]]:
    """
    Open each job link and attempt to apply if enabled.
    Results are kept in memory and returned to the caller.
    """
    if not config.auto_apply:
        return jobs

    results: list[dict[str, str]] = []

    for job in jobs:
        link = job.get("link", "")
        if not link:
            job["apply_status"] = "MissingLink"
            results.append(job)
            continue

        print(f"[apply] Opening: {link}")
        apply_page = page.context.new_page()
        apply_page.goto(link, wait_until="domcontentloaded")
        apply_page.wait_for_timeout(1500)

        try:
            status = _attempt_apply(apply_page)
        except Exception:
            status = "ApplyError"
        job["apply_status"] = status
        print(f"[apply] Status: {status}")
        apply_page.close()
        results.append(job)

    return results


def _get_next_page_url(page: Page) -> str:
    href = page.evaluate(
        """
        () => {
            const container = document.querySelector('div.styles_pagination__oIvXh');
            if (!container) return '';
            const anchors = Array.from(container.querySelectorAll('a'));
            const next = anchors.find((a) => a.textContent.trim() === 'Next' && !a.hasAttribute('disabled'));
            return next ? (next.getAttribute('href') || '') : '';
        }
        """
    )

    if not href:
        return ""

    return urljoin(page.url, href)


def search_jobs(page: Page, config: AppConfig) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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
    if config.sort_by_date:
        _sort_by_date(page)

    all_jobs: list[dict[str, str]] = []
    ai_jobs: list[dict[str, str]] = []
    seen_all: set[str] = set()
    seen_ai: set[str] = set()
    base_terms = config.filter_terms or _DEFAULT_AI_TERMS
    terms = [t.lower() for t in base_terms] + [kw.lower() for kw in config.keywords]

    page_count = 0
    while True:
        page_count += 1
        # Collect all visible jobs (kept in memory only)
        page_jobs = _collect_all_jobs(page)
        if not page_jobs:
            print("[search] No jobs found on this page.")
            break
        for job in page_jobs:
            link = job.get("link", "")
            if link and link not in seen_all:
                seen_all.add(link)
                all_jobs.append(job)

            if config.max_jobs and len(all_jobs) >= config.max_jobs:
                break

        if config.max_jobs and len(all_jobs) >= config.max_jobs:
            break

        # Filter AI-related job cards
        page_ai = _filter_jobs_by_terms(page_jobs, terms)
        for job in page_ai:
            link = job.get("link", "")
            if link and link not in seen_ai:
                seen_ai.add(link)
                ai_jobs.append(job)

        if config.max_pages and page_count >= config.max_pages:
            break

        next_url = _get_next_page_url(page)
        if not next_url or next_url == page.url:
            break

        print(f"[search] Moving to next page: {next_url}")
        page.goto(next_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

    if config.max_jobs:
        all_jobs = all_jobs[:config.max_jobs]

    if config.auto_apply and ai_jobs:
        ai_jobs = apply_to_jobs(page, ai_jobs, config)

    print(f"[search] ✅ Found {len(all_jobs)} total job cards.")
    print(f"[search] ✅ Found {len(ai_jobs)} AI-matching job cards.")
    return all_jobs, ai_jobs
