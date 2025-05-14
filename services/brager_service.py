import base64

from seleniumbase import SB
import secrets
from page_objects.bragerconnect.dashboard_page import DashboardPage
from page_objects.bragerconnect.login_page import LoginPage
from utils.config_provider import ConfigProvider
from utils.logger import logger


class BragerService:
    login_page = LoginPage()
    dashboard_page = DashboardPage()

    page_url = ConfigProvider.get_brager_config_option("brager_url")
    object_name = ConfigProvider.get_brager_config_option("user_object")
    module_name = ConfigProvider.get_brager_config_option("module_name")
    email = base64.b64decode(secrets.brager_email).decode("utf-8")
    password = base64.b64decode(secrets.brager_password).decode("utf-8")
    fuel_level = None
    boiler_status = None
    boiler_temperature = None

    def execute(self) -> bool:
        try:
            self.collect_boiler_data()
            return True
        except (RuntimeError, Exception):
            return False

    def collect_boiler_data(self):
        logger.info("Connecting to BragerOne application.")
        with SB(browser="chrome", maximize=True, headless=True) as sb:
            # actual timeout will be twice as much (30 seconds) due to the retry in SeleniumBase
            sb.driver.set_page_load_timeout(15)
            try:
                sb.open(self.page_url)
            except Exception as e:
                logger.error(f"Could not open page {self.page_url}! Exception: %s", e)
                raise

            try:
                self.login_page.proceed_to_login(sb)
                self.login_page.login_user(sb, self.email, self.password)
            except Exception as e:
                logger.error(f"Could not login user {self.email}! Exception: %s", e, exc_info=True)
                raise

            try:
                self.login_page.choose_object(sb, self.object_name)
            except Exception as e:
                logger.error(f"Could not choose object {self.object_name}! Exception: %s", e, exc_info=True)
                raise

            try:
                self.dashboard_page.wait_for_dashboard_loaded(sb, self.module_name)
                self.fuel_level = self.dashboard_page.get_fuel_level(sb)
                self.boiler_status = self.dashboard_page.get_boiler_status(sb)
                self.boiler_temperature = self.dashboard_page.get_boiler_temperature(sb)
                self.dashboard_page.logout(sb)
            except Exception as e:
                logger.error("Could not collect any data from the boiler! Exception: %s", e, exc_info=True)
                raise
        logger.info("Boiler data has been read and collected successfully.")

    def get_fuel_level(self) -> int:
        return self.fuel_level

    def get_boiler_status(self) -> str:
        return self.boiler_status

    def get_boiler_temperature(self) -> str:
        return self.boiler_temperature
