from model.enums.notification_type import FuelNotificationType
from model.notification_data import NotificationData
from services.app_data_service import AppDataService
from services.router_service import RouterService
from utils import date_utils
from utils.config_provider import ConfigProvider
from utils.logger import logger


class NotificationService:
    router_service = RouterService()
    data_service = AppDataService()

    full_fuel_level = 100
    low_fuel_level = ConfigProvider.get_brager_config_option("low_fuel_level")
    critical_fuel_level = ConfigProvider.get_brager_config_option("critical_fuel_level")
    recipients_list = ConfigProvider.get_router_config_option("recipients")
    # time interval expressed in hours
    notification_time_interval: int = ConfigProvider.get_brager_config_option("notification_time_interval")
    warning_notification_types = [FuelNotificationType.LOW_FUEL, FuelNotificationType.CRITICAL_FUEL]

    def __init__(self):
        self._notification_data = None

    def set_notification_data(self, notification_data: NotificationData):
        self._notification_data = notification_data
        return self

    def send_sms_notification(self):
        notification_type = self._get_notification_type()

        if notification_type not in self.warning_notification_types:
            logger.info("Currently fuel is at optimal level.")
        if not self._should_send_sms(notification_type):
            return

        current_datetime = date_utils.get_current_datetime()
        if notification_type == FuelNotificationType.REFILL_FUEL:
            self.data_service.save_fuel_refill_date(current_datetime)

        is_sms_sent = False
        match notification_type:
            case FuelNotificationType.LOW_FUEL:
                self._send_low_fuel_level_message(self._notification_data)
                is_sms_sent = True
            case FuelNotificationType.CRITICAL_FUEL:
                self._send_critical_fuel_level_message(self._notification_data)
                is_sms_sent = True
            case FuelNotificationType.REFILL_FUEL:
                self._send_full_fuel_level_message(self._notification_data)
                is_sms_sent = True

        if is_sms_sent:
            self.data_service.set_last_sms_date(current_datetime)
        self.data_service.set_last_notification_type(notification_type)
        self.data_service.save_data_file()

    def _should_send_sms(self, current_notification_type: FuelNotificationType) -> bool:
        last_sms_date = self.data_service.get_last_sms_date()
        last_notification_type = self.data_service.get_last_notification_type()
        if not last_sms_date or not last_notification_type:
            return True

        raw_time_delta = date_utils.get_time_difference(last_sms_date, date_utils.get_current_datetime())
        time_delta_hours = raw_time_delta / (60 * 60)

        if current_notification_type != last_notification_type:
            # always send notification if fuel status has changed
            return True
        elif time_delta_hours >= self.notification_time_interval and current_notification_type in self.warning_notification_types:
            # also send notification if current fuel status is dangerous and enough time passed since last notification
            return True

        return False

    def _get_notification_type(self) -> FuelNotificationType:
        current_fuel_level = self._notification_data.fuel_level
        if self.low_fuel_level >= current_fuel_level > self.critical_fuel_level:
            return FuelNotificationType.LOW_FUEL
        elif current_fuel_level <= self.critical_fuel_level:
            return FuelNotificationType.CRITICAL_FUEL
        elif current_fuel_level == self.full_fuel_level:
            return FuelNotificationType.REFILL_FUEL
        else:
            return FuelNotificationType.OK_FUEL

    def _send_low_fuel_level_message(self, notification_data: NotificationData):
        logger.info(f"Detected low fuel level: {notification_data.fuel_level}%! A corresponding message will be sent.")
        low_fuel_message_tpl: str = ConfigProvider.get_brager_config_option("low_fuel_level_message").strip()
        for recipient in self.recipients_list:
            low_fuel_message = low_fuel_message_tpl.format(
                recipient["name"], notification_data.fuel_level, notification_data.boiler_temperature, notification_data.boiler_status
            )
            self.router_service.execute(low_fuel_message, recipient["phone_number"])

    def _send_critical_fuel_level_message(self, notification_data: NotificationData):
        logger.info(f"Detected critical fuel level: {notification_data.fuel_level}%! A corresponding message will be sent.")
        critical_fuel_message_tpl = ConfigProvider.get_brager_config_option("critical_fuel_level_message").strip()
        for recipient in self.recipients_list:
            critical_fuel_message = critical_fuel_message_tpl.format(
                recipient["name"], notification_data.fuel_level, notification_data.boiler_temperature, notification_data.boiler_status
            )
            self.router_service.execute(critical_fuel_message, recipient["phone_number"])

    def _send_full_fuel_level_message(self, notification_data: NotificationData):
        logger.info("Detected recent fuel refill. A corresponding message will be sent.")
        full_fuel_message_tpl = ConfigProvider.get_brager_config_option("full_fuel_level_message").strip()
        for recipient in self.recipients_list:
            critical_fuel_message = full_fuel_message_tpl.format(
                recipient["name"], notification_data.boiler_temperature, notification_data.boiler_status
            )
            self.router_service.execute(critical_fuel_message, recipient["phone_number"])
