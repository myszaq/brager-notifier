import base64
import pytest
from seleniumbase import BaseCase
import secrets
from page_objects.router.dashboard_page import DashboardPage
from page_objects.router.login_page import LoginPage
from page_objects.router.sms_page import SmsPage
from utils.config_provider import ConfigProvider
from utils.logger import logger


class RouterTest(BaseCase):
    login_page = LoginPage()
    dashboard_page = DashboardPage()
    sms_page = SmsPage()

    def test_router_page(self):
        logger.info("Starting router test")
        page_url = ConfigProvider.get_router_config_option("router_url")
        password = base64.b64decode(secrets.router_password).decode("utf-8")

        low_fuel_message = ConfigProvider.get_brager_config_option("low_fuel_level_message").strip()
        low_fuel_message = low_fuel_message.format("Henryk", 20, "37°C", "Praca")

        self.driver.maximize_window()
        # actual timeout will be twice as much (30 seconds) due to the retry in SeleniumBase
        self.driver.set_page_load_timeout(15)
        self.open(page_url)
        self.login_page.login(self, password)
        self.dashboard_page.navigate_to_tools_menu(self)
        self.sms_page.open_sms_view(self)
        status = self.sms_page.compose_sms(self, "000000000", low_fuel_message)
        self.dashboard_page.logout(self)

        if status:
            print("Sending sms completed successfully!")
        else:
            print("Sending sms unfortunately failed for some reason.")

    @pytest.mark.skip
    def test_sending_message(self):
        for i in range(10):
            print(f"Test number {i + 1}")
            self.test_router_page()
