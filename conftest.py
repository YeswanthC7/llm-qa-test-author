# conftest.py  (place at repo root)

import os
import re
import pytest
from playwright.sync_api import expect, Page


# ── Helper to decide if the user is already logged-in ──────────────────────
def _is_logged_in(page: Page) -> bool:
    # crude: look for the account menu text "Sign Out" in header
    try:
        return page.locator("text=Sign Out").first.is_visible(timeout=1_000)
    except Exception:
        return False


# ── Session-scoped, authenticated page (or None) ──────────────────────────
@pytest.fixture(scope="session")
def auth_context(browser) -> Page | None:
    """
    If MAGENTO_USER / MAGENTO_PASS env vars exist, log in once and
    return a Page that stays logged-in for the whole test run.
    If creds are absent, return None so auth-required tests can skip.
    """
    user = os.getenv("MAGENTO_USER")
    pw   = os.getenv("MAGENTO_PASS")

    if not (user and pw):
        return None  # no creds → tests that rely on login must skip

    page = browser.new_page()
    page.goto("https://magento.softwaretestingboard.com/")

    # avoid re-logging if session cookies already valid
    if not _is_logged_in(page):
        page.goto("https://magento.softwaretestingboard.com/customer/account/login/")
        page.fill("#email", user)
        page.fill("#pass", pw)
        page.click("#send2")

    # confirm we actually landed in the account-logged state
    expect(page).to_have_url(re.compile(r"magento\.softwaretestingboard\.com"), timeout=10_000)
    yield page
    page.close()


# ── Convenience fixture for individual tests needing login ────────────────
@pytest.fixture
def logged_page(auth_context: Page | None, page: Page) -> Page:
    """
    Give a logged-in Page to a test **if** creds are present.
    Otherwise skip the test cleanly.
    Usage in test:  def test_xyz(logged_page):
    """
    if auth_context is None:
        pytest.skip("Auth-only flow – set MAGENTO_USER / MAGENTO_PASS to run")
    return auth_context
