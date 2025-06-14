
from playwright.sync_api import sync_playwright, expect

def test_view_past_orders(page):
    playwright = sync_playwright()
    page.goto("https://www.ebay.com/")
    page.locator("#gb-signout > a").click()
    page.locator("#gb-signin > a:has-text('Sign in')").click()
    page.fill("#ap-email", "test@example.com")
    page.fill("#ap-password", "password")
    page.click("#signIn.sign-in-button")
    page.hover("#myebay > a:has-text('My eBay')")
    page.click("#purchase-history > a")

    expect(page).to_have_text("Purchase history")

    table = page.query_selector("#purchase-history-table")
    rows = table.query_all("tr")
    assert len(rows) > 0

    row = rows[0]
    order_date = row.query_selector("td:nth-child(1) > a")
    item_name = row.query_selector("td:nth-child(2) > a")
    price = row.query_selector("td:nth-child(3) > a")

    expect(order_date).to_have_text(str(int(time.time() - 3600)))  # Replace with a valid order