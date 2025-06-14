import pytest
pytest.skip("Placeholders or async remained after retries", allow_module_level=True)

# 
# import pytest
# from playwright.async_api import Playwright, async_playwright
# 
# @pytest.fixture(scope="function")
#     async def playwright():
#     async with async_playwright() as p:
#         yield p
# 
# @pytest.mark.asyncio
#     async def test_order_history(playwright):
#     browser = playwright.chromium
#     context = await browser.new_context()
#     await context.goto("https://magento.softwaretestingboard.com/")
# 
#     await context.authenticate("valid_email@example.com", "valid_password")
#     await context.click("#topcart > a > span.actions > a")
#     await context.click("#block-my-account > div > ul > li:nth-child(2) > a")
# 
#     orders_page = await context.current_page()
#     await orders_page.wait_for_selector("#sales_order_grid > tbody > tr")
# 
#     assert orders_page.is_visible("#sales_order_grid > tbody > tr:nth-child(1) > td:nth-child(1) > a > span")
#     assert orders_page.is_visible("#sales_order_grid > tbody > tr:nth-child(1) > td:nth-child(3) > a")
#     assert orders_page.is_visible("#sales_order_grid > tbody > tr:nth-child(1) > td
