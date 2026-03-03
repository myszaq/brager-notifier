from services.browser_client import BrowserClient
from utils.logger import logger
from utils.selenium_helpers import SeleniumHelpers


class SmsPage:
    sms_container: str = "#sms_page"
    sms_menu_button: str = "#menu_smstool"
    new_sms_button: str = "#sms_message_new"
    send_sms_button: str = "div[lang-id='sms.send.new']"
    recipient_field: str = "#sms_send_user_input"
    sms_content_field: str = "#sms_current_content"
    sms_error_container: str = "#sms_error_info"
    loading_dialog: str = "#utilStartSubmitDialog_contentId"

    messages_header: str = "Wiadomości SMS"
    attempts_message: str = "Pomyślne próby"
    sending_message: str = "Wysyłanie wiadomości SMS"
    success_message: str = "Wysyłanie wiadomości powiodło się"

    def __init__(self, browser_client: BrowserClient):
        self.browser = browser_client
        self.sh = SeleniumHelpers(self.browser.driver)

    def open_sms_view(self):
        if self.sh.is_element_visible(self.sms_container):
            return
        self.sh.click(self.sms_menu_button)
        self.sh.assert_text_visible(self.messages_header)

    def reload_page(self):
        self.sh.refresh_page()
        self.sh.wait_for_text_visible(self.messages_header)

    def compose_sms(self, recipients: str, content: str) -> bool:
        self._prepare_sms(recipients, content)

        if self.sh.is_element_visible(self.sms_error_container):
            error_msg = self.sh.get_text(self.sms_error_container)
            raise RuntimeError(f"Could not send the sms to recipients: {recipients}! Error message: {error_msg}")
        self._send_sms()

        self.sh.wait_for_element_visible(self.loading_dialog)
        self.sh.wait_for_text_visible(self.sending_message, self.loading_dialog)
        self.sh.wait_for_text_visible(self.attempts_message, self.loading_dialog, timeout=90)

        status_message = self.sh.get_text(self.loading_dialog)
        self.sh.wait_for_element_not_visible(self.loading_dialog)

        if self.success_message in status_message:
            return True
        else:
            logger.error(f"An error message occurred while trying to send the sms: {status_message}.")
            return False

    def _prepare_sms(self, recipients: str, content: str):
        self.sh.click(self.new_sms_button)
        self.sh.wait_for_element_visible(self.recipient_field)
        self.sh.wait_for_element_visible(self.sms_content_field)
        self.sh.type(self.recipient_field, recipients)
        self.sh.type(self.sms_content_field, content)

    def _send_sms(self):
        self.sh.click(self.send_sms_button)
