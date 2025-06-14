import pytest
pytest.skip("Placeholders or async remained after retries", allow_module_level=True)


import pytest
from playwright.async_api import Playwright, async_playwright, Page

@pytest.fixture(scope="function")
    async def page(request):
    browser = await async_playwright().chromium.launch()
    page = await browser.new_page()
    yield page
    await page.close()
    await browser.close()

@pytest.mark.asyncio
    async def test_buy_it_now(page):
    await page.goto("https://www.ebay.com/")
    await page.wait_for_selector("#mainContent > div > div:nth-child(1) > div > div:nth-child(1) > div > a[href*='BuyItNow']")
    buy_it_now_button = await page.querySelector("#mainContent > div > div:nth-child(1) > div > div:nth-child(1) > div > a[href*='BuyItNow']")
    await buy_it_now_button.click()

    # Fill in payment and shipping details if prompted (not shown in user story)

    await page.wait_for_selector("#gs-signin-button")
    await page.click("#gs-signin-button")
    await page.fill("#signin-email", "test@example.com")
    await page.fill("#signin-password", "password")
    await page.click("#signin-submit")