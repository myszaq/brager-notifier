import base64

import secrets
from page_objects.bragerconnect.common_page import CommonPage
from page_objects.bragerconnect.login_page import LoginPage
from services.app_data_service import AppDataService
from services.browser_client import BrowserClient
from utils.config_provider import ConfigProvider
from utils.logger import logger
from utils.selenium_helpers import SeleniumHelpers
from utils import utils

class LoginService:
    data_service = AppDataService()

    object_name = ConfigProvider.get_brager_config_option("user_object")
    module_name = ConfigProvider.get_brager_config_option("module_name")
    email = base64.b64decode(secrets.brager_email).decode("utf-8")
    password = base64.b64decode(secrets.brager_password).decode("utf-8")

    def __init__(self, browser: BrowserClient):
        self._common_page = CommonPage(browser.driver)
        self._login_page = LoginPage(browser.driver)
        self._sh = SeleniumHelpers(browser.driver)

    def brager_login(self):
        utils.run_method_with_retry(self._login_page.wait_for_login_page, on_retry=self._sh.refresh_page)
        current_browser_storage = self.data_service.get_browser_storage()
        if current_browser_storage:
            self._common_page.set_browser_storage_data(current_browser_storage)
            self._sh.refresh_page()

            if self._common_page.is_main_page_loaded():
                logger.info("Existing browser storage data has been reused successfully.")
            else:
                logger.warn("Existing browser storage data was invalid or expired, performing logging in.")
                self._sh.refresh_page()
                self._login()
                self._save_browser_storage_data()
        else:
            logger.info("No existing browser storage data has been found.")
            self._login()
            self._save_browser_storage_data()

    def _login(self):
        if self._common_page.is_main_panel_visible():
            return

        try:
            self._login_page.proceed_to_login()
            self._login_page.login_user(self.email, self.password)
            logger.info(f"User {self.email} has logged in successfully.")
        except Exception as e:
            logger.error(f"Could not login user {self.email}! Exception: %s", e, exc_info=True)
            raise

        try:
            self._login_page.choose_object(self.object_name)
            logger.info(f"Object {self.object_name} has been selected successfully.")
        except Exception as e:
            logger.error(f"Could not select object {self.object_name}! Exception: %s", e, exc_info=True)
            raise

    def _save_browser_storage_data(self):
        current_browser_storage = self._common_page.get_browser_storage_data()
        self.data_service.set_browser_storage(current_browser_storage)
        self.data_service.save_data_file()
        logger.info("New browser storage data has been retrieved and saved for the next usage.")
