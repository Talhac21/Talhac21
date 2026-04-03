from playwright.sync_api import sync_playwright


def manual_session_bootstrap() -> str:
    """Open browser for explicit manual login; returns serialized storage_state JSON."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://rivalregions.com")
        # Human login is required here.
        page.wait_for_timeout(45_000)
        storage = context.storage_state()
        browser.close()
        return str(storage)
