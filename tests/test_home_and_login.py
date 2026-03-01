import pytest
from dotenv import load_dotenv
from playwright.sync_api import expect

from src.pages.dashboard_page import DashboardPage
from src.pages.login_page import LoginPage


class TestHomeAndLogin:

    #Load Environment Variables
    load_dotenv()

    @pytest.mark.login
    @pytest.mark.parametrize("username, password",[
        pytest.param("admin@test.com","Password123", id="valid_user"),
        pytest.param("invalid@test.com","wrongpassword", id="invalid_user")
    ])
    def test_login_scenarios(self, playwright_page, username, password):
        login_page = LoginPage.open(page=playwright_page)
        login_page.login(_username=username, _password=password)

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
