"""
orangehrm_page.py
Sample Page Object Model for OrangeHRM demo site using Playwright wrapper.
"""

import pytest_check as check

from page_objects.playwright_wrapper import BasePage


class OrangeHRMPage(BasePage):
    """
    Page Object Model for OrangeHRM demo site.
    Includes all main elements/components for login and signup.
    """
    def __init__(self, page, logger, screenshots_dir="screenshots"):
        super().__init__(page, logger, screenshots_dir)

    # Locators
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "button[type='submit']"
    LOGIN_ERROR = "div.oxd-alert-content-text"
    DASHBOARD_HEADER = "h6.oxd-text.oxd-text--h6.oxd-topbar-header-title"
    SIGNUP_LINK = "a[href*='register']"
    SIGNUP_USERNAME = "input[name='reg_username']"
    SIGNUP_EMAIL = "input[name='reg_email']"
    SIGNUP_PASSWORD = "input[name='reg_password']"
    SIGNUP_SUBMIT = "button[type='submit']"
    SIGNUP_SUCCESS = "div.signup-success"

    def login(self, username: str, password: str):
        """Perform login action."""
        self.find(self.USERNAME_INPUT).fill(username)
        self.find(self.PASSWORD_INPUT).fill(password)
        self.find(self.LOGIN_BUTTON).click()
        self.logger.info(f"Attempted login with username: {username}")

    def assert_login_success(self):
        """Soft assert that dashboard header is visible after login."""
        self.wait_for_selector(self.DASHBOARD_HEADER)
        header = self.find(self.DASHBOARD_HEADER)
        check.is_true(header.is_visible(), "Dashboard header should be visible after login.")
        self.logger.info("Login success assertion complete.")

    def assert_login_failure(self):
        """Soft assert that login error message is visible after failed login."""
        self.wait_for_selector(self.LOGIN_ERROR)
        error = self.find(self.LOGIN_ERROR)
        check.is_true(error.is_visible(), "Login error message should be visible after failed login.")
        self.logger.info("Login failure assertion complete.")

    def go_to_signup(self):
        """Navigate to signup page."""
        self.find(self.SIGNUP_LINK).click()
        self.wait_for_url("**/register")
        self.logger.info("Navigated to signup page.")

    def signup(self, username: str, email: str, password: str):
        """Perform signup action."""
        self.find(self.SIGNUP_USERNAME).fill(username)
        self.find(self.SIGNUP_EMAIL).fill(email)
        self.find(self.SIGNUP_PASSWORD).fill(password)
        self.find(self.SIGNUP_SUBMIT).click()
        self.logger.info(f"Attempted signup with username: {username}, email: {email}")

    def assert_signup_success(self):
        """Soft assert that signup success message is visible."""
        self.wait_for_selector(self.SIGNUP_SUCCESS)
        success = self.find(self.SIGNUP_SUCCESS)
        check.is_true(success.is_visible(), "Signup success message should be visible.")
        self.logger.info("Signup success assertion complete.")

