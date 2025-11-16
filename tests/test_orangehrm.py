"""
test_orangehrm.py
Sample test cases for OrangeHRM login and signup using Playwright wrapper and soft assertions.
"""

import pytest
from page_objects.orangehrm_page import OrangeHRMPage

@pytest.fixture(scope="function")
def orangehrm(page, logger):
    return OrangeHRMPage(page, logger)

@pytest.mark.parametrize("username,password", [
    ("Admin", "admin123"),      # valid credentials
    ("invalid", "invalid123"),  # invalid credentials
])
def test_login(orangehrm, username, password):
    orangehrm.page.goto("https://opensource-demo.orangehrmlive.com/")
    orangehrm.login(username, password)
    if username == "Admin" and password == "admin123":
        orangehrm.assert_login_success()
    else:
        orangehrm.assert_login_failure()

@pytest.mark.skip("Signup flow is not available on OrangeHRM demo, example for structure only.")
def test_signup(orangehrm):
    orangehrm.page.goto("https://opensource-demo.orangehrmlive.com/")
    orangehrm.go_to_signup()
    orangehrm.signup("newuser", "newuser@example.com", "Password123!")
    orangehrm.assert_signup_success()
