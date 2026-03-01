import base64
import smtplib
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path
from smtplib import SMTPException

import secrets
from model.enums.error_type import ErrorType
from services.app_data_service import AppDataService
from utils import date_utils
from utils.config_provider import ConfigProvider
from utils.logger import logger


class EmailService:
    data_service = AppDataService()

    mail_from: str = ConfigProvider.get_mailer_config_option("mail_from")
    mail_from_name: str = ConfigProvider.get_mailer_config_option("mail_from_name")
    recipients_list: list = ConfigProvider.get_mailer_config_option("recipients")
    smtp_host: str = ConfigProvider.get_mailer_config_option("smtp_host")
    smtp_port: int = ConfigProvider.get_mailer_config_option("smtp_port")
    # time intervals expressed in hours
    error_email_time_intervals: dict = ConfigProvider.get_mailer_config_option("send_error_email_intervals")

    def __init__(self):
        self._error_type = None
        self._screenshot_path = None
        self._attachment_path = None
        self._error_log = None

    def set_error_type(self, error_type: ErrorType):
        self._error_type = error_type
        return self

    def set_error_log(self, error_log: str):
        self._error_log = error_log
        return self

    def set_screenshot_path(self, screenshot_path: str):
        self._screenshot_path = screenshot_path
        return self

    def set_attachment_path(self, attachment_path: str):
        self._attachment_path = attachment_path
        return self

    def send_email(self):
        if not self._should_send_email():
            return

        # noinspection PyBroadException
        try:
            for recipient in self.recipients_list:
                self._send_email_helper(recipient)
            self.data_service.set_last_mail_date(date_utils.get_current_datetime(), self._error_type)
            self.data_service.save_data_file()
        except Exception as e:
            logger.error("Sending notification email failed!", e, exc_info=True)
            pass

    # send actual email via smtplib
    def _send_email_helper(self, recipient: dict):
        logger.info(f"Sending notification email to {recipient["email"]}...")

        msg = EmailMessage()
        msg["From"] = self._build_from_address()
        msg["To"] = self._build_to_address(recipient)
        msg["Subject"] = email_template_config["mail_subject"][self._error_type]
        msg.set_content(email_template_config["fallback_message"])

        image_cid = make_msgid(domain="brager.com")
        html_content = self._build_html_content(recipient, image_cid)
        msg.add_alternative(html_content, subtype="html")

        attachment_path = Path(self._attachment_path)
        mime_type = "application/octet-stream"
        maintype, subtype = mime_type.split("/", 1)

        # prepare attachment with error log file
        try:
            with open(attachment_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=attachment_path.name
                )
        except OSError as e:
            logger.error("Could not read attachment file! Exception: %s", e, exc_info=True)

        # open error screenshot file and embed it into html content
        if self._screenshot_path is not None:
            try:
                with open(self._screenshot_path, "rb") as img:
                    msg.get_payload()[1].add_related(
                        img.read(),
                        maintype="image",
                        subtype="png",
                        cid=image_cid,
                        filename="error_screenshot.png",
                        disposition="inline"
                    )
            except OSError as e:
                logger.error("Could not read screenshot file! Exception: %s", e, exc_info=True)
                raise

        smtp_username = base64.b64decode(secrets.smtp_username).decode("utf-8")
        smtp_password = base64.b64decode(secrets.smtp_password).decode("utf-8")
        # send actual email
        try:
            mailserver = smtplib.SMTP(self.smtp_host, self.smtp_port)
            mailserver.ehlo()
            mailserver.starttls()
            mailserver.login(smtp_username, smtp_password)
            mailserver.send_message(msg)
            mailserver.close()
        except (SMTPException, OSError) as e:
            logger.error("Could not send notification email! Exception: %s", e, exc_info=True)
            raise

        logger.info("Notification email has been successfully sent.")

    def _should_send_email(self) -> bool:
        last_mail_date = self.data_service.get_last_mail_date(self._error_type)
        if not last_mail_date:
            return True

        raw_time_delta = date_utils.get_time_difference(last_mail_date, date_utils.get_current_datetime())
        time_delta_hours = raw_time_delta / (60 * 60)
        if time_delta_hours >= self.error_email_time_intervals[self._error_type]:
            return True

        return False

    def _build_from_address(self) -> Address:
        username, domain = self.mail_from.split("@")
        return Address(self.mail_from_name, username, domain)

    def _build_to_address(self, recipient: dict) -> Address:
        username, domain = recipient["email"].split("@")
        return Address(recipient["display_name"], username, domain)

    def _build_html_content(self, recipient: dict, image_cid: str):
        try:
            with open("resources/error_email_template.html", "r", encoding="utf-8") as f:
                html_content = f.read()
        except OSError as e:
            logger.error("Could not read email template file! Exception: %s", e, exc_info=True)
            raise

        html_content = html_content.replace("${user_name}", recipient["hello_name"])
        html_content = html_content.replace("${error_info}", email_template_config["error_info"][self._error_type])
        html_content = html_content.replace("${log_message}", self._error_log)
        html_content = html_content.replace("${error_screenshot_src}", f"cid:{image_cid[1:-1]}")
        html_content = html_content.replace("${img_display_style}", "block" if self._screenshot_path is not None else "none")

        return html_content


email_template_config = {
    "fallback_message": "Przepraszamy! Ta wiadomość jest w formacie HTML, ale Twój klient pocztowy niestety jego nie obsługuje.",
    "mail_subject": {
        ErrorType.READ_DATA_ERROR: "[BragerOne] Błąd pobierania danych z aplikacji",
        ErrorType.SAVE_DATA_ERROR: "[BragerOne] Błąd zapisu danych z aplikacji"
    },
    "error_info": {
        ErrorType.READ_DATA_ERROR: "Niestety w trakcie ostatniego pobierania danych z aplikacji Brager One wystąpił błąd.",
        ErrorType.SAVE_DATA_ERROR: "Niestety w trakcie ostatniego zapisu danych do bazy z aplikacji Brager One wystąpił błąd."
    }
}
