import base64
from seleniumbase import BaseCase
import secrets
from page_objects.bragerconnect.dashboard_page import DashboardPage
from page_objects.bragerconnect.login_page import LoginPage
from utils.config_provider import ConfigProvider


class BragerTest(BaseCase):
    login_page = LoginPage()
    dashboard_page = DashboardPage()

    def test_brager_page(self):
        page_url = ConfigProvider.get_brager_config_option("brager_url")
        object_name = ConfigProvider.get_brager_config_option("user_object")
        module_name = ConfigProvider.get_brager_config_option("module_name")
        email = base64.b64decode(secrets.brager_email).decode("utf-8")
        password = base64.b64decode(secrets.brager_password).decode("utf-8")

        self.driver.maximize_window()
        # actual timeout will be twice as much (30 seconds) due to the retry in SeleniumBase
        self.driver.set_page_load_timeout(15)
        self.open(page_url)
        self.login_page.proceed_to_login(self)
        self.login_page.login_user(self, email, password)
        self.login_page.choose_object(self, object_name)

        self.dashboard_page.wait_for_dashboard_loaded(self, module_name)
        fuel_level = self.dashboard_page.get_fuel_level(self)
        boiler_status = self.dashboard_page.get_boiler_status(self)
        boiler_temperature = self.dashboard_page.get_boiler_temperature(self)
        self.dashboard_page.logout(self)

        print("Paliwo: ", fuel_level)
        print("Status: ", boiler_status)
        print("Temperatura: ", boiler_temperature)
