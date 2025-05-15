import json
import os
from utils.config_provider import PROJECT_ROOT_DIR


class DataService:
    json_file_path = os.path.join(PROJECT_ROOT_DIR, "data", "persistence.json")
    file_content: dict = None

    def __init__(self):
        if self.data_file_exists():
            self.read_data_file()
        else:
            # create template for output json without any data
            self.file_content = {
                "last_read_date": "",
                "last_fuel_level": 0,
                "fuel_refill_dates": []
            }
            self.save_data_file()

    def data_file_exists(self) -> bool:
        return os.path.exists(self.json_file_path)

    def read_data_file(self):
        with open(self.json_file_path, "r") as input_file:
            self.file_content = json.load(input_file)

    def save_data_file(self):
        json_object = json.dumps(self.file_content, indent=4)
        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
        with open(self.json_file_path, "w") as output_file:
            output_file.write(json_object)

    def get_last_read_date(self) -> str | None:
        if "last_read_date" in self.file_content:
            return self.file_content["last_read_date"]
        return None

    def set_last_read_date(self, last_read_date: str):
        self.file_content["last_read_date"] = last_read_date

    def get_last_fuel_level(self) -> int | None:
        if "last_fuel_level" in self.file_content:
            return self.file_content["last_fuel_level"]
        return None

    def set_last_fuel_level(self, last_fuel_level: int):
        self.file_content["last_fuel_level"] = last_fuel_level

    def save_fuel_refill_date(self, refill_date: str):
        if "fuel_refill_dates" in self.file_content:
            self.file_content["fuel_refill_dates"].append(refill_date)
        else:
            self.file_content["fuel_refill_dates"] = [refill_date]
