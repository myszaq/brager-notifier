from seleniumbase import BaseCase
from utils.logger import logger

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

    def open_sms_view(self, sb: BaseCase):
        if sb.is_element_visible(self.sms_container):
            return
        sb.click(self.sms_menu_button)
        sb.assert_text_visible(self.messages_header)

    def reload_page(self, sb: BaseCase):
        sb.refresh_page()
        sb.wait_for_text(self.messages_header)

    def compose_sms(self, sb: BaseCase, recipients: str, content: str) -> bool:
        self.prepare_sms(sb, recipients, content)

        if sb.is_element_visible(self.sms_error_container):
            error_msg = sb.get_text(self.sms_error_container)
            raise RuntimeError(f"Could not send the sms to recipients: {recipients}! Error message: {error_msg}")
        self.send_sms(sb)

        sb.wait_for_element(self.loading_dialog)
        sb.wait_for_text(self.sending_message, self.loading_dialog)
        sb.wait_for_text(self.attempts_message, self.loading_dialog, timeout=90)

        status_message = sb.get_text(self.loading_dialog)
        sb.wait_for_element_not_visible(self.loading_dialog)

        if self.success_message in status_message:
            return True
        else:
            logger.error(f"An error message occurred while trying to send the sms: {status_message}.")
            return False

    def prepare_sms(self, sb: BaseCase, recipients: str, content: str):
        sb.click(self.new_sms_button)
        sb.wait_for_element(self.recipient_field)
        sb.wait_for_element(self.sms_content_field)
        sb.type(self.recipient_field, recipients)
        sb.type(self.sms_content_field, content)

    def send_sms(self, sb: BaseCase):
        sb.click(self.send_sms_button)
