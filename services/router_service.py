import base64

import secrets
from page_objects.router.dashboard_page import DashboardPage
from page_objects.router.login_page import LoginPage
from page_objects.router.sms_page import SmsPage
from services.browser_client import BrowserClient
from utils.config_provider import ConfigProvider
from utils.logger import logger


class RouterService:
    page_url = ConfigProvider.get_router_config_option("router_url")
    password = base64.b64decode(secrets.router_password).decode("utf-8")

    def __init__(self):
        self._login_page = None
        self._dashboard_page = None
        self._sms_page = None

    def send_message(self, message: str, phone_number: str):
        logger.info(f"Sending SMS with the content: {message}")

        with BrowserClient(headless=True) as client:
            self._login_page = LoginPage(client.driver)
            self._dashboard_page = DashboardPage(client.driver)
            self._sms_page = SmsPage(client.driver)

            client.driver.maximize_window()
            client.driver.set_page_load_timeout(30)
            try:
                client.open(self.page_url)
            except Exception as e:
                logger.error(f"Could not open page {self.page_url}! Exception: %s", e)
                raise

            try:
                self._login_page.login(self.password)
                self._dashboard_page.navigate_to_tools_menu()
                self._sms_page.open_sms_view()
            except Exception as e:
                logger.error("Could not access SMS tool view! Exception: %s", e, exc_info=True)
                raise

            try:
                send_status = self._sms_page.compose_sms(phone_number, message)
                if send_status:
                    logger.info(f"SMS was sent successfully to phone number: {phone_number}.")
                else:
                    logger.error("Sending SMS failed!")
                    retries = 3
                    for i in range(retries):
                        logger.info(f"Retrying to send the SMS ({i + 1}/{retries})...")
                        self._sms_page.reload_page()
                        send_status = self._sms_page.compose_sms(phone_number, message)
                        if send_status:
                            logger.info(f"SMS was sent successfully to phone number: {phone_number}.")
                            break
                        else:
                            logger.error("Sending SMS failed!")

                self._dashboard_page.logout()
            except Exception as e:
                logger.error("Could not send the SMS! Exception: %s", e, exc_info=True)
                raise
