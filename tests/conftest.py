"""
conftest.pyuuu
Shared pytest fixtures for Playwright wrapper and OrangeHRM tests.
"""

import pytest
from page_objects.playwright_wrapper import BrowserManager, Logger
import subprocess
import shutil
import sys
import os

@pytest.fixture(scope="session", autouse=True)
def ensure_playwright_installed():
    """
    One-time fixture to ensure Playwright browsers are installed before tests run.
    Handles Playwright CLI message: 'Please run the following command to download new browsers: playwright install'
    """
    if not shutil.which("playwright"):
        raise RuntimeError("Playwright CLI not found. Please install the 'playwright' package.")
    try:
        # Try to import Playwright and check for browser installation
        import playwright
        # Check if browsers are installed by running 'playwright install --check'
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "--check"
        ], capture_output=True, text=True)
        # If Playwright CLI or Python API reports browsers missing, install them
        if result.returncode != 0 or (
            result.stdout and "Please run the following command to download new browsers" in result.stdout
        ):
            install_result = subprocess.run([
                sys.executable, "-m", "playwright", "install"
            ], capture_output=True, text=True)
            if install_result.returncode != 0:
                raise RuntimeError(f"Failed to install Playwright browsers: {install_result.stderr}")
    except Exception as e:
        raise RuntimeError(f"Failed to ensure Playwright browsers are installed: {e}")

def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        choices=["chromium", "firefox", "webkit", "chrome", "edge"],
        help="Browser type: chromium, firefox, webkit, chrome, edge"
    )
    parser.addoption(
        "--ws",
        action="store",
        default="full_screen",
        help="Window size: full_screen, half_screen, or WIDTHxHEIGHT (e.g., 1280x720)"
    )

@pytest.fixture(scope="session")
def browser_manager(pytestconfig):
    browser_type = pytestconfig.getoption("--browser")
    ws = pytestconfig.getoption("--ws").lower()
    headless = False

    # Normalize browser type
    if browser_type in ["chrome", "edge"]:
        browser_type = "chromium"

    # Detect host screen size (best-effort)
    try:
        if os.name == 'nt':
            from ctypes import windll
            screen_w = windll.user32.GetSystemMetrics(0)
            screen_h = windll.user32.GetSystemMetrics(1)
        else:
            try:
                import tkinter as _tk
                _root = _tk.Tk()
                _root.withdraw()
                screen_w = _root.winfo_screenwidth()
                screen_h = _root.winfo_screenheight()
                _root.destroy()
            except Exception:
                screen_w, screen_h = 1920, 1080
    except Exception:
        screen_w, screen_h = 1920, 1080

    # Default: auto maximize (viewport will be set using detected screen size)
    context_args = {}
    half_screen = False

    # Determine window mode
    if ws in ["full_screen", "fs", "maximized", "max"]:
        # Full screen mode → set viewport to detected screen size
        context_args["viewport"] = {"width": screen_w, "height": screen_h}
        half_screen = False

    elif ws in ["half_screen", "hs"]:
        # Half screen: half width, full height
        context_args["viewport"] = {"width": int(screen_w / 2), "height": screen_h}
        half_screen = True

    else:
        # User-defined "WIDTHxHEIGHT"
        try:
            w, h = map(int, ws.split("x"))
            context_args["viewport"] = {"width": w, "height": h}
        except Exception:
            # fallback to full screen
            context_args["viewport"] = {"width": screen_w, "height": screen_h}

    # Start browser
    manager = BrowserManager(headless=headless, browser_type=browser_type)
    manager.start_browser()

    # Create context with dynamic viewport
    context = manager.new_context(**context_args)
    # Create and reuse the first page/tab — do not create additional pages here
    page = manager.new_page()

    # Ensure page has the expected viewport size (fallback if initial window was not resized)
    try:
        desired_viewport = context_args.get("viewport")
        if desired_viewport:
            page.set_viewport_size({"width": int(desired_viewport["width"]), "height": int(desired_viewport["height"])})
    except Exception:
        # As a final fallback, attempt JS resize
        try:
            page.evaluate("""
                window.moveTo(0,0);
                window.resizeTo(screen.availWidth, screen.availHeight);
            """)
        except Exception:
            pass

    manager.page = page
    yield manager

    manager.stop_browser()

@pytest.fixture(scope="function")
def page(browser_manager):
    # Reuse the first page created by browser_manager to avoid opening a second tab
    page = browser_manager.page
    if not page:
        # Fallback: create a page if for some reason manager.page wasn't set
        page = browser_manager.new_page()
        browser_manager.page = page
    yield page
    try:
        # Close only if it's not the manager's main page (keep manager.page for session reuse)
        if page is not browser_manager.page:
            page.close()
    except Exception:
        pass

@pytest.fixture(scope="function")
def logger():
    return Logger()
