import base64
import pytest

import secrets
from page_objects.router.dashboard_page import DashboardPage
from page_objects.router.login_page import LoginPage
from page_objects.router.sms_page import SmsPage
from utils.config_provider import ConfigProvider
from utils.logger import logger


class TestRouter:

    @pytest.fixture(autouse=True)
    def setup_pages(self, browser):
        self.browser = browser
        self.login_page = LoginPage(browser.driver)
        self.dashboard_page = DashboardPage(browser.driver)
        self.sms_page = SmsPage(browser.driver)

    def test_router_page(self, browser):
        logger.info("Starting router test")
        page_url = ConfigProvider.get_router_config_option("router_url")
        password = base64.b64decode(secrets.router_password).decode("utf-8")

        low_fuel_message = ConfigProvider.get_brager_config_option("low_fuel_level_message").strip()
        low_fuel_message = low_fuel_message.format("Michał", 20, "37°C", "Praca")

        browser.driver.maximize_window()
        browser.driver.set_page_load_timeout(30)
        browser.open(page_url)

        self.login_page.login(password)
        self.dashboard_page.navigate_to_tools_menu()
        self.sms_page.open_sms_view()
        status = self.sms_page.compose_sms("000000000", low_fuel_message)
        self.dashboard_page.logout()

        if status:
            print("Sending sms completed successfully!")
        else:
            print("Sending sms unfortunately failed for some reason.")
        assert status

    @pytest.mark.skip
    def test_sending_message(self, browser):
        for i in range(10):
            print(f"Test number {i + 1}")
            self.test_router_page(browser)
