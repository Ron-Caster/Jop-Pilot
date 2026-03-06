"""
auth.login
~~~~~~~~~~~
Automates the Naukri.com login flow using Playwright and
DOM selectors from the project specification (CLAUDE.md).
"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import AppConfig

# ── Naukri DOM selectors (from CLAUDE.md) ────────────────────
_LOGIN_LINK     = "a#login_Layer"
_EMAIL_INPUT    = 'input[placeholder="Enter your active Email ID / Username"]'
_PASSWORD_INPUT = 'input[type="password"][placeholder="Enter your password"]'
_LOGIN_BUTTON   = "button.btn-primary.loginButton"

_NAUKRI_URL     = "https://www.naukri.com/"
_HOMEPAGE_PATH  = "/mnjuser/homepage"


def login(page: Page, config: AppConfig, timeout: int = 20_000) -> None:
    """
    Log in to Naukri.com.

    Steps
    -----
    1. Navigate to the Naukri homepage.
    2. Click the *Login* link to open the side-drawer.
    3. Enter email and password.
    4. Click the *Login* button.
    5. Wait until the browser is redirected to the homepage.
    """
    # 1 ── Navigate to Naukri ───────────────────────────────
    print("[auth] Navigating to Naukri.com …")
    page.goto(_NAUKRI_URL, wait_until="domcontentloaded")

    # 2 ── Click Login link ─────────────────────────────────
    print("[auth] Opening login drawer …")
    page.click(_LOGIN_LINK, timeout=timeout)

    # 3 ── Fill credentials ─────────────────────────────────
    print("[auth] Entering credentials …")
    page.fill(_EMAIL_INPUT, config.email, timeout=timeout)
    page.wait_for_timeout(500)

    page.fill(_PASSWORD_INPUT, config.password, timeout=timeout)

    # 4 ── Click Login button ───────────────────────────────
    page.wait_for_timeout(500)
    print("[auth] Clicking Login …")
    page.click(_LOGIN_BUTTON, timeout=timeout)

    # 5 ── Wait for redirect ────────────────────────────────
    print("[auth] Waiting for homepage redirect …")
    page.wait_for_url(f"**{_HOMEPAGE_PATH}*", timeout=timeout)
    print("[auth] ✅ Login successful!")
