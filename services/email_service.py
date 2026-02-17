import base64
import smtplib
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path
from smtplib import SMTPException

import secrets
from services.data_service import DataService
from utils import date_utils
from utils.config_provider import ConfigProvider
from utils.logger import logger


class EmailService:
    data_service = DataService()

    mail_from: str = ConfigProvider.get_mailer_config_option("mail_from")
    mail_from_name: str = ConfigProvider.get_mailer_config_option("mail_from_name")
    recipients_list: list = ConfigProvider.get_mailer_config_option("recipients")
    mail_subject: str = ConfigProvider.get_mailer_config_option("mail_subject")
    fallback_message: str = ConfigProvider.get_mailer_config_option("fallback_message")
    smtp_host: str = ConfigProvider.get_mailer_config_option("smtp_host")
    smtp_port: int = ConfigProvider.get_mailer_config_option("smtp_port")
    # time interval expressed in hours
    error_email_time_interval: int = ConfigProvider.get_mailer_config_option("send_error_email_interval")

    def __init__(self):
        self._screenshot_path = None
        self._attachment_path = None
        self._error_log = None

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
            self.data_service.set_last_mail_date(date_utils.get_current_datetime())
            self.data_service.save_data_file()
        except Exception:
            logger.error("Sending notification email failed!")
            pass

    # send actual email via smtplib
    def _send_email_helper(self, recipient: dict):
        logger.info(f"Sending notification email to {recipient["email"]}...")

        msg = EmailMessage()
        msg["From"] = self._build_from_address()
        msg["To"] = self._build_to_address(recipient)
        msg["Subject"] = self.mail_subject
        msg.set_content(self.fallback_message)

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
        last_mail_date = self.data_service.get_last_mail_date()
        if not last_mail_date:
            return True

        raw_time_delta = date_utils.get_time_difference(last_mail_date, date_utils.get_current_datetime())
        time_delta_hours = raw_time_delta / (60 * 60)
        if time_delta_hours >= self.error_email_time_interval:
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
        html_content = html_content.replace("${log_message}", self._error_log)
        html_content = html_content.replace("${error_screenshot_src}", f"cid:{image_cid[1:-1]}")

        return html_content
