import json
import os

from model.enums.notification_type import NotificationType
from utils.config_provider import PROJECT_ROOT_DIR


class DataService:
    json_file_path = os.path.join(PROJECT_ROOT_DIR, "data", "persistence.json")
    data_dict: dict = None

    def __init__(self):
        if self._data_file_exists():
            self._read_data_file()
        else:
            # create template for output json without any data
            browser_storage = {
                "selectedObjectId": 0,
                "accessToken": "",
                "refreshToken": ""
            }
            DataService.data_dict = {
                "last_read_date": "",
                "last_sms_date": "",
                "last_mail_date": "",
                "last_notification_type": NotificationType.OK_FUEL.value,
                "last_fuel_level": 0,
                "fuel_refill_dates": [],
                "browser_storage": browser_storage,
            }
            self.save_data_file()

    def save_data_file(self):
        json_object = json.dumps(DataService.data_dict, indent=4)
        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
        with open(self.json_file_path, "w") as output_file:
            output_file.write(json_object)

    def get_last_read_date(self) -> str | None:
        if "last_read_date" in DataService.data_dict:
            return DataService.data_dict["last_read_date"]
        return None

    def set_last_read_date(self, last_read_date: str):
        DataService.data_dict["last_read_date"] = last_read_date

    def get_last_sms_date(self) -> str | None:
        if "last_sms_date" in DataService.data_dict:
            return DataService.data_dict["last_sms_date"]
        return None

    def set_last_sms_date(self, last_sms_date: str):
        DataService.data_dict["last_sms_date"] = last_sms_date

    def get_last_notification_type(self) -> NotificationType | None:
        if "last_notification_type" in DataService.data_dict:
            return NotificationType(DataService.data_dict["last_notification_type"])
        return None

    def set_last_notification_type(self, notification_type: NotificationType):
        DataService.data_dict["last_notification_type"] = notification_type.value

    def get_last_mail_date(self) -> str | None:
        if "last_mail_date" in DataService.data_dict:
            return DataService.data_dict["last_mail_date"]

    def set_last_mail_date(self, last_mail_date: str):
        DataService.data_dict["last_mail_date"] = last_mail_date

    def get_last_fuel_level(self) -> int | None:
        if "last_fuel_level" in DataService.data_dict:
            return DataService.data_dict["last_fuel_level"]
        return None

    def set_last_fuel_level(self, last_fuel_level: int):
        DataService.data_dict["last_fuel_level"] = last_fuel_level

    def get_browser_storage(self) -> dict | None:
        if "browser_storage" in DataService.data_dict:
            return DataService.data_dict["browser_storage"]
        return None

    def set_browser_storage(self, browser_storage: dict):
        DataService.data_dict["browser_storage"] = browser_storage

    def save_fuel_refill_date(self, refill_date: str):
        if "fuel_refill_dates" in DataService.data_dict:
            DataService.data_dict["fuel_refill_dates"].append(refill_date)
        else:
            DataService.data_dict["fuel_refill_dates"] = [refill_date]

    def _read_data_file(self):
        with open(self.json_file_path, "r") as input_file:
            DataService.data_dict = json.load(input_file)

    def _data_file_exists(self) -> bool:
        return os.path.exists(self.json_file_path)
