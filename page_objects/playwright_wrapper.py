"""
playwright_wrapper.py
A production-grade Playwright wrapper for Python automation frameworks.
"""

import logging
import os
import sys
from datetime import datetime
from functools import wraps
from typing import Optional, Any

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Locator, \
    TimeoutError as PlaywrightTimeoutError


# =========================
# Custom Exceptions
# =========================
class ElementNotFound(Exception):
    """Raised when an element cannot be found on the page."""
    pass

class ActionFailed(Exception):
    """Raised when an action on an element fails."""
    pass

class NavigationError(Exception):
    """Raised when navigation or page load fails."""
    pass

# =========================
# Logger Utility
# =========================
class Logger:
    """Logger utility for Playwright wrapper."""
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger = logging.getLogger("PlaywrightWrapper")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
        # File handler
        file_handler = logging.FileHandler(os.path.join(self.log_dir, "framework.log"), encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        # Add handlers
        if not self.logger.hasHandlers():
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        else:
            # Avoid duplicate handlers
            self.logger.handlers.clear()
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

# =========================
# Screenshot-on-error Decorator
# =========================
def screenshot_on_error(method):
    """Decorator to capture screenshot and log error on exception."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            logger = getattr(self, "logger", None)
            page = getattr(self, "page", None)
            screenshots_dir = getattr(self, "screenshots_dir", "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            screenshot_path = os.path.join(screenshots_dir, f"error_{timestamp}.png")
            if page:
                try:
                    page.screenshot(path=screenshot_path, full_page=True)
                    if logger:
                        logger.error(f"Screenshot captured: {screenshot_path}")
                except Exception as se:
                    if logger:
                        logger.error(f"Failed to capture screenshot: {se}")
            if logger:
                logger.error(f"Exception in {method.__name__}: {e}")
            raise
    return wrapper

# =========================
# Element Wrapper
# =========================
class Element:
    """
    Wrapper for Playwright Locator object, providing robust actions and error handling.
    """
    _valid_methods = [
        "click", "fill", "hover", "type", "press", "select_option", "get_text", "get_attribute",
        "wait_for", "is_visible", "is_hidden", "is_enabled", "screenshot"
    ]

    def __init__(self, locator: Locator, page: Page, logger: Logger, screenshots_dir: str = "screenshots"):
        self.locator = locator
        self.page = page
        self.logger = logger
        self.screenshots_dir = screenshots_dir

    def _suggest_method(self, name: str) -> str:
        from difflib import get_close_matches
        suggestion = get_close_matches(name, self._valid_methods, n=1)
        return f"Did you mean: {suggestion[0]}()?" if suggestion else "No similar method found."

    def __getattr__(self, name: str) -> Any:
        if name not in self._valid_methods:
            msg = f"Element has no method '{name}'. {self._suggest_method(name)}"
            self.logger.error(msg)
            raise AttributeError(msg)
        return getattr(self, name)

    @screenshot_on_error
    def click(self, timeout: int = 10000) -> "Element":
        """Click the element."""
        try:
            self.locator.click(timeout=timeout)
            self.logger.info(f"Clicked element: {self.locator}")
            return self
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout clicking element: {self.locator}")
            raise ActionFailed(f"Timeout clicking element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to click element: {e}")
            raise ActionFailed(f"Failed to click element: {e}")

    @screenshot_on_error
    def fill(self, value: str, timeout: int = 10000) -> "Element":
        """Fill the element with value."""
        try:
            self.locator.fill(value, timeout=timeout)
            self.logger.info(f"Filled element: {self.locator} with value: {value}")
            return self
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout filling element: {self.locator}")
            raise ActionFailed(f"Timeout filling element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to fill element: {e}")
            raise ActionFailed(f"Failed to fill element: {e}")

    @screenshot_on_error
    def hover(self, timeout: int = 10000) -> "Element":
        """Hover over the element."""
        try:
            self.locator.hover(timeout=timeout)
            self.logger.info(f"Hovered over element: {self.locator}")
            return self
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout hovering element: {self.locator}")
            raise ActionFailed(f"Timeout hovering element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to hover element: {e}")
            raise ActionFailed(f"Failed to hover element: {e}")

    @screenshot_on_error
    def type(self, text: str, timeout: int = 10000) -> "Element":
        """Type text into the element."""
        try:
            self.locator.type(text, timeout=timeout)
            self.logger.info(f"Typed '{text}' into element: {self.locator}")
            return self
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout typing into element: {self.locator}")
            raise ActionFailed(f"Timeout typing into element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to type into element: {e}")
            raise ActionFailed(f"Failed to type into element: {e}")

    @screenshot_on_error
    def press(self, key: str, timeout: int = 10000) -> "Element":
        """Press a key on the element."""
        try:
            self.locator.press(key, timeout=timeout)
            self.logger.info(f"Pressed '{key}' on element: {self.locator}")
            return self
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout pressing key on element: {self.locator}")
            raise ActionFailed(f"Timeout pressing key on element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to press key on element: {e}")
            raise ActionFailed(f"Failed to press key on element: {e}")

    @screenshot_on_error
    def select_option(self, value: Any, timeout: int = 10000) -> "Element":
        """Select option(s) in a <select> element."""
        try:
            self.locator.select_option(value, timeout=timeout)
            self.logger.info(f"Selected option '{value}' in element: {self.locator}")
            return self
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout selecting option in element: {self.locator}")
            raise ActionFailed(f"Timeout selecting option in element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to select option: {e}")
            raise ActionFailed(f"Failed to select option: {e}")

    @screenshot_on_error
    def get_text(self, timeout: int = 10000) -> str:
        """Get text content of the element."""
        try:
            text = self.locator.text_content(timeout=timeout)
            self.logger.info(f"Got text from element: {self.locator} -> {text}")
            return text
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout getting text from element: {self.locator}")
            raise ActionFailed(f"Timeout getting text from element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to get text: {e}")
            raise ActionFailed(f"Failed to get text: {e}")

    @screenshot_on_error
    def get_attribute(self, name: str, timeout: int = 10000) -> Optional[str]:
        """Get attribute value of the element."""
        try:
            value = self.locator.get_attribute(name, timeout=timeout)
            self.logger.info(f"Got attribute '{name}' from element: {self.locator} -> {value}")
            return value
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout getting attribute from element: {self.locator}")
            raise ActionFailed(f"Timeout getting attribute from element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to get attribute: {e}")
            raise ActionFailed(f"Failed to get attribute: {e}")

    @screenshot_on_error
    def wait_for(self, state: str = "visible", timeout: int = 10000) -> "Element":
        """Wait for element to be in a given state."""
        try:
            self.locator.wait_for(state=state, timeout=timeout)
            self.logger.info(f"Waited for element: {self.locator} to be {state}")
            return self
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout waiting for element: {self.locator} to be {state}")
            raise ActionFailed(f"Timeout waiting for element: {self.locator} to be {state}")
        except Exception as e:
            self.logger.error(f"Failed to wait for element: {e}")
            raise ActionFailed(f"Failed to wait for element: {e}")

    @screenshot_on_error
    def is_visible(self, timeout: int = 10000) -> bool:
        """Check if element is visible."""
        try:
            visible = self.locator.is_visible(timeout=timeout)
            self.logger.info(f"Element {self.locator} is visible: {visible}")
            return visible
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout checking visibility for element: {self.locator}")
            raise ActionFailed(f"Timeout checking visibility for element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to check visibility: {e}")
            raise ActionFailed(f"Failed to check visibility: {e}")

    @screenshot_on_error
    def is_hidden(self, timeout: int = 10000) -> bool:
        """Check if element is hidden."""
        try:
            hidden = self.locator.is_hidden(timeout=timeout)
            self.logger.info(f"Element {self.locator} is hidden: {hidden}")
            return hidden
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout checking hidden for element: {self.locator}")
            raise ActionFailed(f"Timeout checking hidden for element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to check hidden: {e}")
            raise ActionFailed(f"Failed to check hidden: {e}")

    @screenshot_on_error
    def is_enabled(self, timeout: int = 10000) -> bool:
        """Check if element is enabled."""
        try:
            enabled = self.locator.is_enabled(timeout=timeout)
            self.logger.info(f"Element {self.locator} is enabled: {enabled}")
            return enabled
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout checking enabled for element: {self.locator}")
            raise ActionFailed(f"Timeout checking enabled for element: {self.locator}")
        except Exception as e:
            self.logger.error(f"Failed to check enabled: {e}")
            raise ActionFailed(f"Failed to check enabled: {e}")

    @screenshot_on_error
    def screenshot(self, path: Optional[str] = None, full_page: bool = True) -> str:
        """Take screenshot of the element."""
        try:
            os.makedirs(self.screenshots_dir, exist_ok=True)
            if not path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                path = os.path.join(self.screenshots_dir, f"element_{timestamp}.png")
            self.locator.screenshot(path=path)
            self.logger.info(f"Screenshot of element saved: {path}")
            return path
        except Exception as e:
            self.logger.error(f"Failed to take element screenshot: {e}")
            raise ActionFailed(f"Failed to take element screenshot: {e}")

# =========================
# BasePage
# =========================
class BasePage:
    """
    Base page object for Playwright automation, provides common actions and helpers.
    """
    def __init__(self, page: Page, logger: Logger, screenshots_dir: str = "screenshots"):
        self.page = page
        self.context = page.context
        self.browser = self.context.browser
        self.logger = logger
        self.screenshots_dir = screenshots_dir
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def find(self, selector: str) -> Element:
        """Find an element by selector and return Element wrapper."""
        try:
            locator = self.page.locator(selector)
            if not locator:
                self.logger.error(f"Element not found: {selector}")
                raise ElementNotFound(f"Element not found: {selector}")
            self.logger.info(f"Found element: {selector}")
            return Element(locator, self.page, self.logger, self.screenshots_dir)
        except Exception as e:
            self.logger.error(f"Failed to find element: {e}")
            raise ElementNotFound(f"Failed to find element: {e}")

    @screenshot_on_error
    def wait_for_url(self, url: str, timeout: int = 10000) -> None:
        """Wait for the page URL to match the given URL."""
        try:
            self.page.wait_for_url(url, timeout=timeout)
            self.logger.info(f"Waited for URL: {url}")
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout waiting for URL: {url}")
            raise NavigationError(f"Timeout waiting for URL: {url}")
        except Exception as e:
            self.logger.error(f"Failed to wait for URL: {e}")
            raise NavigationError(f"Failed to wait for URL: {e}")

    @screenshot_on_error
    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 10000) -> None:
        """Wait for a selector to be in a given state."""
        try:
            self.page.wait_for_selector(selector, state=state, timeout=timeout)
            self.logger.info(f"Waited for selector: {selector} to be {state}")
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout waiting for selector: {selector} to be {state}")
            raise ElementNotFound(f"Timeout waiting for selector: {selector} to be {state}")
        except Exception as e:
            self.logger.error(f"Failed to wait for selector: {e}")
            raise ElementNotFound(f"Failed to wait for selector: {e}")

    @screenshot_on_error
    def take_screenshot(self, path: Optional[str] = None, full_page: bool = True) -> str:
        """Take screenshot of the page."""
        try:
            os.makedirs(self.screenshots_dir, exist_ok=True)
            if not path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                path = os.path.join(self.screenshots_dir, f"page_{timestamp}.png")
            self.page.screenshot(path=path, full_page=full_page)
            self.logger.info(f"Screenshot of page saved: {path}")
            return path
        except Exception as e:
            self.logger.error(f"Failed to take page screenshot: {e}")
            raise ActionFailed(f"Failed to take page screenshot: {e}")

    @screenshot_on_error
    def assert_text(self, selector: str, expected: str, timeout: int = 10000) -> None:
        """Assert that the text of an element matches expected value using pytest_check (soft assert)."""
        try:
            import pytest_check as check
            actual = self.page.locator(selector).text_content(timeout=timeout)
            check.equal(actual, expected, f"Text assertion failed: expected '{expected}', got '{actual}'")
            self.logger.info(f"Asserted text for {selector}: '{actual}' == '{expected}'")
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout asserting text for selector: {selector}")
            raise ActionFailed(f"Timeout asserting text for selector: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to assert text: {e}")
            raise ActionFailed(f"Failed to assert text: {e}")

# =========================
# BrowserManager
# =========================
class BrowserManager:
    """
    Manages Playwright browser, context, and page lifecycle with centralized logging and error handling.
    """
    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logger = Logger()
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.logger.log_dir, exist_ok=True)

    def start_browser(self) -> None:
        """Start Playwright browser."""
        try:
            self.playwright = sync_playwright().start()
            browser_launcher = getattr(self.playwright, self.browser_type)
            self.browser = browser_launcher.launch(headless=self.headless)
            self.logger.info(f"Started browser: {self.browser_type}, headless={self.headless}")
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise NavigationError(f"Failed to start browser: {e}")

    def stop_browser(self) -> None:
        """Stop Playwright browser and cleanup."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("Stopped browser and cleaned up resources.")
        except Exception as e:
            self.logger.error(f"Failed to stop browser: {e}")
            raise NavigationError(f"Failed to stop browser: {e}")

    def new_context(self, **kwargs) -> BrowserContext:
        """Create a new browser context."""
        try:
            self.context = self.browser.new_context(**kwargs)
            self.logger.info("Created new browser context.")
            return self.context
        except Exception as e:
            self.logger.error(f"Failed to create new context: {e}")
            raise NavigationError(f"Failed to create new context: {e}")

    def new_page(self) -> Page:
        """Create a new page in the current context."""
        try:
            if not self.context:
                self.new_context()
            self.page = self.context.new_page()
            self.logger.info("Created new page.")
            return self.page
        except Exception as e:
            self.logger.error(f"Failed to create new page: {e}")
            raise NavigationError(f"Failed to create new page: {e}")

    @property
    def get_logger(self) -> Logger:
        """Get the logger instance."""
        return self.logger

    @property
    def get_screenshots_dir(self) -> str:
        """Get the screenshots' directory."""
        return self.screenshots_dir

# =========================
# End of playwright_wrapper.py
# =========================
