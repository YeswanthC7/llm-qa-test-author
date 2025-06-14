import pytest
pytest.skip("Placeholders or async remained after retries", allow_module_level=True)


import pytest
from playwright.async_api import Playwright, async_playwright

@pytest.fixture(scope="function")
    async def playwright():
    async with async_playwright() as p:
        context = await p.chromium.launch(context=None)
        yield context
    await context.close()

@pytest.mark.asyncio
    async def test_logout(playwright):
    async with playwright as p:
        context = await p.new_context(viewport=None)
        page = await context.new_page()
    await page.goto("https://www.ebay.com/")

    await page.click("#userContentId > div > div > div > a[href*='signin']")
    await page.wait_for_selector("#gb > div > div > div > div > div > div > form > div:nth-child(1) > button")
    await page.click("#gb > div > div > div > div > div > div > form > div:nth-child(1) > button")

    await page.wait_for_response("**/", response => response.status() == 302)
        assert await page.is_redirected()

    await page.wait_for_selector("#signin > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div