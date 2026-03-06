"""
browser.driver
~~~~~~~~~~~~~~~
Factory for Playwright Firefox browser instances.
"""

from __future__ import annotations

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from config.settings import AppConfig


class BrowserSession:
    """Wraps Playwright lifecycle so callers get a simple object."""

    def __init__(self, config: AppConfig) -> None:
        self._pw = sync_playwright().start()
        self._browser: Browser = self._pw.firefox.launch(
            headless=config.headless,
        )
        self._context: BrowserContext = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
                "Gecko/20100101 Firefox/121.0"
            ),
        )
        self.page: Page = self._context.new_page()
        self.page.set_default_timeout(config.implicit_wait * 1000)
        print("[browser] ✅ Firefox browser ready.")

    def close(self) -> None:
        self._context.close()
        self._browser.close()
        self._pw.stop()
        print("[browser] Browser closed.")


def create_browser(config: AppConfig) -> BrowserSession:
    """Create and return a configured Firefox browser session."""
    return BrowserSession(config)
