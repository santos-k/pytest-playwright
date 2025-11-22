import pytest
from playwright.sync_api import Page

@pytest.fixture(autouse=True)
def open_maximized(page: Page):
    """
    Autouse fixture: set the page viewport to the screen's available size and attempt to maximize
    the browser window. This is best-effort — it sets viewport, tries JS resize, and for Chromium
    uses CDP to set the windowState to 'maximized'. Fail silently if any step is unsupported.
    """
    try:
        # get host available screen size and set the viewport accordingly
        size = page.evaluate("() => ({ width: window.screen.availWidth, height: window.screen.availHeight })")
        if isinstance(size, dict) and "width" in size and "height" in size:
            page.set_viewport_size({"width": int(size["width"]), "height": int(size["height"])})
    except Exception:
        pass

    try:
        # attempt a JS resize (may be blocked by some browsers/security settings)
        page.evaluate("() => { window.moveTo(0,0); window.resizeTo(screen.availWidth, screen.availHeight); }")
    except Exception:
        pass

    try:
        # for Chromium-based browsers, attempt to use CDP to set the native window to maximized
        # (works when Playwright is driving a real browser -- ignored in non-Chromium engines)
        session = page.context.new_cdp_session(page)
        res = session.send("Browser.getWindowForTarget")
        window_id = res.get("windowId")
        if window_id is not None:
            session.send("Browser.setWindowBounds", {"windowId": window_id, "bounds": {"windowState": "maximized"}})
    except Exception:
        pass

    yield
