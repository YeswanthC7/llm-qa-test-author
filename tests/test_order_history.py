import pytest
pytest.skip("Placeholders or async remained after retries", allow_module_level=True)


import pytest
from playwright.async_api import Playwright, async_playwright

@pytest.fixture(scope="function")
    async def browser():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(no_sandbox=False)
        yield browser
    await browser.close()

@pytest.mark.asyncio
    async def test_order_history(browser):
    await browser.new_page()
    await browser.goto("https://www.ebay.com/")

    await browser.click("#gh-signin-link > span")
    await browser.fill("#i0118 > input", "valid_email@example.com")
    await browser.click("#i0118 > button")
    await browser.fill("#signin-email > input", "password")
    await browser.click("#signin-password > button")

    await browser.hover("#myebay > a")
    await browser.click("#gh-pdp-link-type-purchase-history")

    orders = await browser.query_selector_all("#s-item__info > table > tbody > tr")
    assert len(orders) > 0

    order = orders[0]
    order_date = await order.inner_text("#s-item__info-row:nth-child(1) > td:nth-child(2) > a")
    item_name = await