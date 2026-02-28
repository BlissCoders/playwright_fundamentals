import pytest
from dotenv import load_dotenv

from src.pages.dashboard_page import DashboardPage
from src.pages.login_page import LoginPage


class TestHomeAndLogin:

    #Load Environment Variables
    load_dotenv()
    @pytest.mark.login
    def test_login_with_valid_credentials(self, playwright_page):
        """
        Test Case: Login with valid credentials
                   Should be able to login with valid credentials
        Steps:
        1. Navigate to 'https://blisscoders.pythonanywhere.com/login'
        2. Enter valid username: admin@test.com
        3. Enter valid password: Password123
        4. Click login button
        5. Should see the message: 'Successful login!'
        """
        login_page = LoginPage.open(page=playwright_page)
        login_page.login(_username="admin@test.com", _password="Password123")

    @pytest.mark.login
    def test_login_with_invalid_credentials(self, playwright_page):
        """
        Test Case: Login with invalid credentials
                   Should not be able to login with invalid credentials
        Steps:
        1. Navigate to 'https://blisscoders.pythonanywhere.com/login'
        2. Enter valid username: invalid_user
        3. Enter valid password: invalid_password
        4. Click login button
        5. Should not see the message: 'Successful login!'
        """
        login_page = LoginPage.open(page=playwright_page)
        login_page.login(_username="invalid_user", _password="invalid_password")

    @pytest.mark.home
    def test_home_screen(self, playwright_page):
        """
        Test Case: Validate the home page

        Steps:
        1. Navigate to "https://blisscoders.pythonanywhere.com/"
        2. Should have a header text of "QA Playwright Demo App"
        3. Should have instruction text of "This application is designed to demonstrate:"
        4. Should see five bullet points under instructions as follows:
            - Proper locator strategies
            - Form validation testing
            - Async loading behavior
            - Dynamic filtering
            - UI testing best practices
        """
        dashboard_page = DashboardPage.open(page=playwright_page)
        dashboard_page.verify_title()
        dashboard_page.verify_header_text()
        dashboard_page.verify_instruction_text()
        dashboard_page.verify_bullet_items()
