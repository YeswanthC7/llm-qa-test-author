import os, pytest

# ---- Skip the entire test file unless both creds are set ----
if not (os.getenv("EBAY_USER") and os.getenv("EBAY_PASS")):
    pytest.skip("Order-history flow disabled (no creds)", allow_module_level=True)

from playwright.sync_api import expect

def test_view_past_orders(page):
    page.goto("https://signin.ebay.com/")
    # If captcha shows, skip rather than fail
    if "captcha" in page.url or page.locator("text=security measure").is_visible(timeout=1000):
        pytest.skip("Captcha triggered – skipping automated login")

    page.fill("#userid", os.getenv("EBAY_USER"))
    page.click("#signin-continue-btn")
    page.fill("#pass", os.getenv("EBAY_PASS"))
    page.click("#sgnBt")

    page.locator("text=Purchase history").click()
    expect(page).to_have_url(lambda u: "PurchaseHistory" in u)
