import base64

import secrets
from model.boiler_data import BoilerData
from model.burner_data import BurnerData
from model.device_data import DeviceData
from model.dhw_data import DHWData
from model.fuel_data import FuelData
from model.return_data import ReturnData
from model.valve_data import ValveData
from page_objects.bragerconnect.components_page import BoilerPage, BurnerPage, DHWPage, FeederPage, ValvePage
from page_objects.bragerconnect.dashboard_page import DashboardPage
from page_objects.bragerconnect.modules_page import ModulesPage
from services.browser_client import BrowserClient
from services.login_service import LoginService
from utils.config_provider import ConfigProvider
from utils.logger import logger
from utils.selenium_helpers import SeleniumHelpers


class BragerService:
    page_url = ConfigProvider.get_brager_config_option("brager_url")
    object_name = ConfigProvider.get_brager_config_option("user_object")
    module_name = ConfigProvider.get_brager_config_option("module_name")
    email = base64.b64decode(secrets.brager_email).decode("utf-8")
    password = base64.b64decode(secrets.brager_password).decode("utf-8")
    fuel_level = None
    boiler_status = None
    boiler_temperature = None

    def __init__(self):
        self.sh = None
        self._driver = None
        self._modules_page = None
        self._dashboard_page = None

    def collect_device_data(self) -> DeviceData:
        logger.info("Connecting to BragerOne application.")
        with BrowserClient(headless=True) as client:
            self._driver = client.driver
            self._dashboard_page = DashboardPage(client.driver)
            self._modules_page = ModulesPage(client.driver)
            self.sh = SeleniumHelpers(client.driver)

            client.driver.set_page_load_timeout(30)
            try:
                try:
                    client.open(self.page_url)
                except Exception as e:
                    logger.error(f"Could not open page {self.page_url}! Exception: %s", e)
                    raise

                login_service = LoginService(client)
                login_service.brager_login()
                self._dashboard_page.wait_for_dashboard_loaded(self.module_name)
                logger.info("Reading device data from BragerOne application.")
                self.fuel_level = self._dashboard_page.get_fuel_level()
                self.boiler_status = self._dashboard_page.get_boiler_status()
                self.boiler_temperature = self._dashboard_page.get_boiler_temperature()

                # collect available data from the dashboard
                boiler_data = self._get_basic_boiler_data()
                return_data = self._get_return_data()
                burner_data = self._get_burner_data()
                fuel_data = self._get_basic_fuel_data()

                # the remaining data require opening specific components pages
                self._modules_page.open_components_page()

                boiler_data = self._get_remaining_boiler_data(boiler_data)
                valve_data = self._get_valve_data()
                dhw_data = self._get_dhw_data()
                fuel_data = self._get_remaining_fuel_data(fuel_data)

                # do not break collecting data if there was an error during log out
                try:
                    self._dashboard_page.logout()
                except Exception as e:
                    logger.error(f"Logging out from the application failed! Exception: %s", e)

                logger.info("Device data has been read and collected successfully.")
                return DeviceData(
                    boiler=boiler_data,
                    valve=valve_data,
                    dhw=dhw_data,
                    flow_return=return_data,
                    burner=burner_data,
                    fuel=fuel_data
                )
            except Exception as e:
                logger.error("Could not collect device data from Brager page! Exception: %s", e, exc_info=True)
                self.sh.save_screenshot("logs/error_screenshot.png")
                raise

    def _get_basic_boiler_data(self) -> BoilerData:
        temperature = self._dashboard_page.get_boiler_temperature()
        setting = self._dashboard_page.get_boiler_setting()
        status = self._dashboard_page.get_boiler_status()
        pump_status = self._dashboard_page.get_boiler_pump_status()

        return BoilerData(boiler_temperature=temperature, boiler_setting=setting, boiler_status=status, boiler_pump_status=pump_status)

    def _get_remaining_boiler_data(self, boiler_data: BoilerData) -> BoilerData:
        boiler_page = BoilerPage(self._driver)
        outdoor_temperature = boiler_page.get_outdoor_temperature()
        boiler_data.outdoor_temperature = outdoor_temperature

        return boiler_data

    def _get_valve_data(self):
        valve_page = ValvePage(self._driver)
        temperature = valve_page.get_valve_temperature()
        setting = valve_page.get_valve_setting()
        pump_status = valve_page.get_valve_pump_status()
        oper_mode = valve_page.get_valve_operating_mode()

        return ValveData(valve_temperature=temperature, valve_setting=setting, valve_pump_status=pump_status,
                         valve_operating_mode=oper_mode)

    def _get_dhw_data(self) -> DHWData:
        dhw_page = DHWPage(self._driver)
        temperature = dhw_page.get_dhw_temperature()
        setting = dhw_page.get_dhw_setting()
        pump_status = dhw_page.get_dhw_pump_status()
        oper_mode = dhw_page.get_dhw_operating_mode()

        return DHWData(dhw_temperature=temperature, dhw_setting=setting, dhw_pump_status=pump_status, dhw_operating_mode=oper_mode)

    def _get_return_data(self) -> ReturnData:
        temperature = self._dashboard_page.get_return_temperature()
        pump_status = self._dashboard_page.get_return_pump_status()

        return ReturnData(return_temperature=temperature, return_pump_status=pump_status)

    def _get_burner_data(self) -> BurnerData:
        power = self._dashboard_page.get_burner_power()
        flame_brightness = self._dashboard_page.get_flame_brightness()
        blower_efficiency = self._dashboard_page.get_blower_efficiency()

        return BurnerData(burner_power=power, flame_brightness=flame_brightness, blower_efficiency=blower_efficiency)

    def _get_basic_fuel_data(self) -> FuelData:
        fuel_level = self._dashboard_page.get_fuel_level()

        return FuelData(fuel_level=fuel_level)

    def _get_remaining_fuel_data(self, fuel_data: FuelData) -> FuelData:
        feeder_page = FeederPage(self._driver)
        fuel_amount = feeder_page.get_burned_fuel_amount()

        burner_page = BurnerPage(self._driver)
        fuel_in_24h = burner_page.get_burned_fuel_in_24h()

        fuel_data.burned_fuel_amount = fuel_amount
        fuel_data.burned_fuel_in_24h = fuel_in_24h
        return fuel_data
