import base64
from seleniumbase import SB
import secrets
from page_objects.router.dashboard_page import DashboardPage
from page_objects.router.login_page import LoginPage
from page_objects.router.sms_page import SmsPage
from utils.config_provider import ConfigProvider
from utils.logger import logger


class RouterService:
    login_page = LoginPage()
    dashboard_page = DashboardPage()
    sms_page = SmsPage()
    page_url = ConfigProvider.get_router_config_option("router_url")
    password = base64.b64decode(secrets.router_password).decode("utf-8")

    def execute(self, message: str, phone_number: str):
        try:
            self.send_message(message, phone_number)
        # slightly ugly solution to avoid throwing a bunch of exceptions from SB context manager
        except (RuntimeError, Exception):
            pass

    def send_message(self, message: str, phone_number: str):
        logger.info(f"Sending SMS with the content: {message}")
        with SB(browser="chrome", maximize=True, headless=True) as sb:
            # actual timeout will be twice as much (30 seconds) due to the retry in SeleniumBase
            sb.driver.set_page_load_timeout(15)
            try:
                sb.open(self.page_url)
            except Exception as e:
                logger.error(f"Could not open page {self.page_url}! Exception: %s", e)
                raise

            try:
                self.login_page.login(sb, self.password)
                self.dashboard_page.navigate_to_tools_menu(sb)
                self.sms_page.open_sms_view(sb)
            except Exception as e:
                logger.error("Could not access SMS tool view! Exception: %s", e, exc_info=True)
                raise

            try:
                send_status = self.sms_page.compose_sms(sb, phone_number, message)
                if send_status:
                    logger.info(f"SMS was sent successfully to phone number: {phone_number}.")
                else:
                    logger.error("Sending SMS failed!")
                    retries = 3
                    for i in range(retries):
                        logger.info(f"Retrying to send the SMS ({i + 1}/{retries})...")
                        self.sms_page.reload_page(sb)
                        send_status = self.sms_page.compose_sms(sb, phone_number, message)
                        if send_status:
                            logger.info(f"SMS was sent successfully to phone number: {phone_number}.")
                            break
                        else:
                            logger.error("Sending SMS failed!")

                self.dashboard_page.logout(sb)
            except Exception as e:
                logger.error("Could not send the SMS! Exception: %s", e, exc_info=True)
                raise
