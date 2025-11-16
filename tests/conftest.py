"""
conftest.py
Shared pytest fixtures for Playwright wrapper and OrangeHRM tests.
"""

import pytest
from page_objects.playwright_wrapper import BrowserManager, Logger
import subprocess
import shutil
import sys

@pytest.fixture(scope="session", autouse=True)
def ensure_playwright_installed():
    """
    One-time fixture to ensure Playwright browsers are installed before tests run.
    """
    if not shutil.which("playwright"):
        raise RuntimeError("Playwright CLI not found. Please install the 'playwright' package.")
    try:
        # Check if browsers are installed by running 'playwright install --check'
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "--check"
        ], capture_output=True, text=True)
        if result.returncode != 0:
            # Install browsers if not installed
            subprocess.run([
                sys.executable, "-m", "playwright", "install"
            ], check=True)
    except Exception as e:
        raise RuntimeError(f"Failed to ensure Playwright browsers are installed: {e}")

@pytest.fixture(scope="session")
def browser_manager():
    manager = BrowserManager(headless=True)
    manager.start_browser()
    yield manager
    manager.stop_browser()

@pytest.fixture(scope="function")
def page(browser_manager):
    context = browser_manager.new_context()
    page = browser_manager.new_page()
    yield page
    page.close()
    context.close()

@pytest.fixture(scope="function")
def logger():
    return Logger()
