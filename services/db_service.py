import base64
from datetime import datetime

import mariadb
from mariadb import Connection, Cursor

import secrets
from model.boiler_data import BoilerData
from model.burner_data import BurnerData
from model.device_data import DeviceData
from model.dhw_data import DHWData
from model.fuel_data import FuelData
from model.return_data import ReturnData
from model.valve_data import ValveData
from utils.config_provider import ConfigProvider
from utils.logger import logger


class DBService:
    conn: Connection = None
    cursor: Cursor = None

    db_name = ConfigProvider.get_database_config_option("db_name")
    db_host = ConfigProvider.get_database_config_option("db_host")
    db_port = ConfigProvider.get_database_config_option("db_port")
    db_user = base64.b64decode(secrets.db_user).decode("utf-8")
    db_password = base64.b64decode(secrets.db_password).decode("utf-8")

    def save_device_data(self, device_data: DeviceData, previous_fuel_level: int = None):
        try:
            self._connect_to_database()
            measurement_id = self._save_main_measurement()
            self._save_boiler_data(measurement_id, device_data.boiler)
            self._save_valve_data(measurement_id, device_data.valve)
            self._save_dhw_data(measurement_id, device_data.dhw)
            self._save_return_data(measurement_id, device_data.flow_return)
            self._save_burner_data(measurement_id, device_data.burner)
            self._save_fuel_data(measurement_id, device_data.fuel)

            # save date of fuel refill if it was detected
            if previous_fuel_level is not None:
                self._save_fuel_refill(measurement_id, previous_fuel_level)
            self.conn.commit()
            logger.debug("Device data has been successfully stored in the database. Measurement id: %d", measurement_id)
        except mariadb.Error as e:
            logger.error("Could not save device data into database! Exception: %s", e, exc_info=True)
            if self.conn:
                self.conn.rollback()
            raise

        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()

    def _connect_to_database(self):
        try:
            self.conn = mariadb.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                autocommit=False
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as e:
            logger.error("Could not connect to database! Exception: %s", e, exc_info=True)
            raise e

    def _save_main_measurement(self) -> int:
        self.cursor.execute("INSERT INTO measurements () VALUES ()")
        return self.cursor.lastrowid

    def _save_boiler_data(self, measurement_id: int, boiler_data: BoilerData):
        sql = """
               INSERT INTO boiler_params
               (measurement_id, boiler_temperature, boiler_setting, boiler_status, boiler_pump_status, outdoor_temperature)
               VALUES (?, ?, ?, ?, ?, ?)
           """
        values = (
            measurement_id,
            boiler_data.boiler_temperature,
            boiler_data.boiler_setting,
            boiler_data.boiler_status,
            boiler_data.boiler_pump_status,
            boiler_data.outdoor_temperature
        )

        self.cursor.execute(sql, values)

    def _save_valve_data(self, measurement_id: int, valve_data: ValveData):
        sql = """
            INSERT INTO valve_params
            (measurement_id, valve_temperature, valve_setting, valve_pump_status, valve_operating_mode)
            VALUES (?, ?, ?, ?, ?)
        """
        values = (
            measurement_id,
            valve_data.valve_temperature,
            valve_data.valve_setting,
            valve_data.valve_pump_status,
            valve_data.valve_operating_mode
        )

        self.cursor.execute(sql, values)

    def _save_dhw_data(self, measurement_id: int, dhw_data: DHWData):
        sql = """
            INSERT INTO dhw_params
            (measurement_id, dhw_temperature, dhw_setting, dhw_pump_status, dhw_operating_mode)
            VALUES (?, ?, ?, ?, ?)
        """
        values = (
            measurement_id,
            dhw_data.dhw_temperature,
            dhw_data.dhw_setting,
            dhw_data.dhw_pump_status,
            dhw_data.dhw_operating_mode
        )

        self.cursor.execute(sql, values)

    def _save_return_data(self, measurement_id: int, return_data: ReturnData):
        sql = """
            INSERT INTO return_params
            (measurement_id, return_temperature, return_pump_status)
            VALUES (?, ?, ?)
        """
        values = (
            measurement_id,
            return_data.return_temperature,
            return_data.return_pump_status
        )

        self.cursor.execute(sql, values)

    def _save_burner_data(self, measurement_id: int, burner_data: BurnerData):
        sql = """
            INSERT INTO burner_params
            (measurement_id, burner_power, flame_brightness, blower_efficiency)
            VALUES (?, ?, ?, ?)
        """
        values = (
            measurement_id,
            burner_data.burner_power,
            burner_data.flame_brightness,
            burner_data.blower_efficiency
        )

        self.cursor.execute(sql, values)

    def _save_fuel_data(self, measurement_id: int, fuel_data: FuelData):
        sql = """
            INSERT INTO fuel_params
            (measurement_id, fuel_level, burned_fuel_amount, burned_fuel_in_24h)
            VALUES (?, ?, ?, ?)
        """
        values = (
            measurement_id,
            fuel_data.fuel_level,
            fuel_data.burned_fuel_amount,
            fuel_data.burned_fuel_in_24h
        )

        self.cursor.execute(sql, values)

    def _save_fuel_refill(self, measurement_id: int, previous_fuel_level: int):
        sql = """
            INSERT INTO fuel_refills
            (measurement_id, previous_fuel_level, refill_date)
            VALUES (?, ?, ?)
        """
        values = (
            measurement_id,
            previous_fuel_level,
            datetime.now()
        )

        self.cursor.execute(sql, values)
