import base64

from seleniumbase import BaseCase

import secrets
from page_objects.bragerconnect.common_page import CommonPage
from page_objects.bragerconnect.login_page import LoginPage
from services.app_data_service import AppDataService
from utils.config_provider import ConfigProvider
from utils.logger import logger


class LoginService:
    common_page = CommonPage()
    login_page = LoginPage()
    data_service = AppDataService()

    object_name = ConfigProvider.get_brager_config_option("user_object")
    module_name = ConfigProvider.get_brager_config_option("module_name")
    email = base64.b64decode(secrets.brager_email).decode("utf-8")
    password = base64.b64decode(secrets.brager_password).decode("utf-8")

    def brager_login(self, sb: BaseCase):
        current_browser_storage = self.data_service.get_browser_storage()
        if current_browser_storage:
            self.common_page.set_browser_storage_data(sb, current_browser_storage)
            sb.refresh_page()

            if self.common_page.is_main_page_loaded(sb):
                logger.info("Existing browser storage data has been reused successfully.")
            else:
                logger.warn("Existing browser storage data was invalid or expired, performing logging in.")
                sb.refresh_page()
                self._login(sb)
                self._save_browser_storage_data(sb)
        else:
            logger.info("No existing browser storage data has been found.")
            self._login(sb)
            self._save_browser_storage_data(sb)

    def _login(self, sb: BaseCase):
        try:
            self.login_page.proceed_to_login(sb)
            self.login_page.login_user(sb, self.email, self.password)
            logger.info(f"User {self.email} has logged in successfully.")
        except Exception as e:
            logger.error(f"Could not login user {self.email}! Exception: %s", e, exc_info=True)
            raise

        try:
            self.login_page.choose_object(sb, self.object_name)
            logger.info(f"Object {self.object_name} has been selected successfully.")
        except Exception as e:
            logger.error(f"Could not select object {self.object_name}! Exception: %s", e, exc_info=True)
            raise

    def _save_browser_storage_data(self, sb: BaseCase):
        current_browser_storage = self.common_page.get_browser_storage_data(sb)
        self.data_service.set_browser_storage(current_browser_storage)
        self.data_service.save_data_file()
        logger.info("New browser storage data has been retrieved and saved for the next usage.")
