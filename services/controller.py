import traceback
from dataclasses import dataclass

import mariadb

from model.enums.error_type import ErrorType
from model.notification_data import NotificationData
from services.brager_service import BragerService
from services.app_data_service import AppDataService
from services.db_service import DBService
from services.email_service import EmailService
from services.notification_service import NotificationService
from services.router_service import RouterService
from utils import date_utils
from utils.config_provider import ConfigProvider
from utils.logger import logger


@dataclass
class BragerData:
    fuel_level: int
    boiler_status: str
    boiler_temperature: str


class Controller:
    brager_service = BragerService()
    router_service = RouterService()
    data_service = AppDataService()
    db_service = DBService()

    full_fuel_level = 100
    low_fuel_level = ConfigProvider.get_brager_config_option("low_fuel_level")
    critical_fuel_level = ConfigProvider.get_brager_config_option("critical_fuel_level")
    recipients_list = ConfigProvider.get_router_config_option("recipients")

    def execute(self):
        try:
            last_fuel_level = self.data_service.get_last_fuel_level()
            device_data = self.brager_service.collect_device_data()
            notification_data = NotificationData(
                fuel_level=device_data.fuel.fuel_level,
                boiler_status=device_data.boiler.boiler_status,
                boiler_temperature=device_data.boiler.boiler_temperature
            )
            logger.info(f"Current fuel level: {notification_data.fuel_level}%. "
                        f"Boiler temperature: {notification_data.boiler_temperature}°C. "
                        f"Boiler status: {notification_data.boiler_status}.")
            self.data_service.set_last_read_date(date_utils.get_current_datetime())
            self.data_service.set_last_fuel_level(notification_data.fuel_level)
            self.data_service.save_data_file()

            previous_full_level = last_fuel_level if (device_data.fuel.fuel_level == 100 and last_fuel_level != 100) else None
            # save the content of device_data to DB
            self.db_service.save_device_data(device_data, previous_full_level)
            NotificationService().set_notification_data(notification_data).send_sms_notification()
        except mariadb.Error as e:
            logger.error("An error occurred during the execution of the program. Exception: %s", e, exc_info=True)
            self._handle_error(ErrorType.SAVE_DATA_ERROR)
        except (RuntimeError, Exception) as e:
            logger.error("An error occurred during the execution of the program. Exception: %s", e, exc_info=True)
            self._handle_error(ErrorType.READ_DATA_ERROR)

    def _handle_error(self, error_type: ErrorType):
        email_service = EmailService()
        email_service.set_error_type(error_type)
        if error_type == ErrorType.READ_DATA_ERROR:
            email_service.set_screenshot_path("logs/error_screenshot.png")

        email_service.set_attachment_path("logs/app_execution.log")
        email_service.set_error_log(traceback.format_exc())
        email_service.send_email()
