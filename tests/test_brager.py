import base64

import pytest

import secrets
from page_objects.bragerconnect.dashboard_page import DashboardPage
from page_objects.bragerconnect.login_page import LoginPage
from utils.config_provider import ConfigProvider
from utils.logger import logger


class TestBrager:

    @pytest.fixture(autouse=True)
    def setup_pages(self, browser):
        self.browser = browser
        self.login_page = LoginPage(browser.driver)
        self.dashboard_page = DashboardPage(browser.driver)

    def test_brager_page(self, browser):
        logger.info("Starting brager test")
        page_url = ConfigProvider.get_brager_config_option("brager_url")
        object_name = ConfigProvider.get_brager_config_option("user_object")
        module_name = ConfigProvider.get_brager_config_option("module_name")
        email = base64.b64decode(secrets.brager_email).decode("utf-8")
        password = base64.b64decode(secrets.brager_password).decode("utf-8")

        try:
            browser.driver.maximize_window()
            browser.driver.set_page_load_timeout(30)
            browser.open(page_url)
            self.login_page.proceed_to_login()
            self.login_page.login_user(email, password)
            self.login_page.choose_object(object_name)

            self.dashboard_page.wait_for_dashboard_loaded(module_name)

            fuel_level = self.dashboard_page.get_fuel_level()
            boiler_status = self.dashboard_page.get_boiler_status()
            boiler_temperature = self.dashboard_page.get_boiler_temperature()
            self.dashboard_page.logout()
        except Exception as e:
            pytest.fail(f"Brager test failed! Exception: {str(e)}")

        print("Paliwo: ", fuel_level)
        print("Status: ", boiler_status)
        print("Temperatura: ", boiler_temperature)
