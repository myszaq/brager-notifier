from dataclasses import dataclass
from services.brager_service import BragerService
from services.data_service import DataService
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
    data_service = DataService()

    full_fuel_level = 100
    low_fuel_level = ConfigProvider.get_brager_config_option("low_fuel_level")
    critical_fuel_level = ConfigProvider.get_brager_config_option("critical_fuel_level")
    recipients_list = ConfigProvider.get_router_config_option("recipients")

    def execute(self):
        is_refilled = False
        brager_data = self.get_brager_data()
        if brager_data is None:
            return

        logger.info(f"Current fuel level: {brager_data.fuel_level}%. "
                    f"Boiler temperature: {brager_data.boiler_temperature}. "
                    f"Boiler status: {brager_data.boiler_status}.")
        if self.low_fuel_level >= brager_data.fuel_level > self.critical_fuel_level:
            logger.info(f"Detected low fuel level: {brager_data.fuel_level}%! A corresponding message will be sent.")
            self.send_low_fuel_level_message(brager_data)
        elif brager_data.fuel_level <= self.critical_fuel_level:
            logger.info(f"Detected critical fuel level: {brager_data.fuel_level}%! A corresponding message will be sent.")
            self.send_critical_fuel_level_message(brager_data)
        elif brager_data.fuel_level == self.full_fuel_level and self.data_service.get_last_fuel_level() != self.full_fuel_level:
            logger.info("Detected recent fuel refill. A corresponding message will be sent.")
            self.send_full_fuel_level_message(brager_data)
            is_refilled = True
        else:
            logger.info("Fuel is on optimal level. There is nothing left to do.")

        self.data_service.set_last_read_date(date_utils.get_current_date_time())
        self.data_service.set_last_fuel_level(brager_data.fuel_level)
        if is_refilled:
            self.data_service.save_fuel_refill_date(date_utils.get_current_date_time())
        self.data_service.save_data_file()

    def get_brager_data(self) -> BragerData | None:
        if self.brager_service.execute():
            fuel_level = self.brager_service.get_fuel_level()
            boiler_status = self.brager_service.get_boiler_status()
            boiler_temperature = self.brager_service.get_boiler_temperature()
            return BragerData(fuel_level, boiler_status, boiler_temperature)
        else:
            logger.error("Could not collect boiler data! Please check error log for details.")
            return None

    def send_low_fuel_level_message(self, brager_data: BragerData):
        low_fuel_message_tpl: str = ConfigProvider.get_brager_config_option("low_fuel_level_message").strip()
        for recipient in self.recipients_list:
            low_fuel_message = low_fuel_message_tpl.format(
                recipient["name"], brager_data.fuel_level, brager_data.boiler_temperature, brager_data.boiler_status
            )
            self.router_service.execute(low_fuel_message, recipient["phone_number"])

    def send_critical_fuel_level_message(self, brager_data: BragerData):
        critical_fuel_message_tpl = ConfigProvider.get_brager_config_option("critical_fuel_level_message").strip()
        for recipient in self.recipients_list:
            critical_fuel_message = critical_fuel_message_tpl.format(
                recipient["name"], brager_data.fuel_level, brager_data.boiler_temperature, brager_data.boiler_status
            )
            self.router_service.execute(critical_fuel_message, recipient["phone_number"])

    def send_full_fuel_level_message(self, brager_data: BragerData):
        full_fuel_message_tpl = ConfigProvider.get_brager_config_option("full_fuel_level_message").strip()
        for recipient in self.recipients_list:
            critical_fuel_message = full_fuel_message_tpl.format(
                recipient["name"], brager_data.boiler_temperature, brager_data.boiler_status
            )
            self.router_service.execute(critical_fuel_message, recipient["phone_number"])
