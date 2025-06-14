import pytest
pytest.skip("Placeholders or async remained after retries", allow_module_level=True)


import pytest
from playwright.async_api import Playwright, async_context, expect

@pytest.fixture(scope="function")
    async def playwright():
    async with Playwright().chromium() as browser:
        context = await browser.new_context()
        yield context
    await context.close()
    await browser.close()

@pytest.mark.asyncio
@async_context
    async def test_add_to_cart(playwright):
    async with playwright as p:
        context = await p.new_context()
        page = await context.new_page("https://www.ebay.com/")

        # Search for an item
    await page.goto("search.html?q=item+to+test")
    await page.click("#mainContent > div.s-item__infoClearance > div > a[href*='viewitem']")

        # Add to cart
    await page.click("#AddToCartButton")

        # Assert mini-cart icon shows "1 item"
    await expect(page).to_have_css("#miniCartIcon > span", text="1")

        # Assert cart total matches the item’s price
        cart_page = await page.goto("viewMyCart.html")
        cart_total = await page.inner_text("#totalPrice")
        assert cart_total.strip() == "$X.XX"  # Replace X.XX with the item's price

    await context.