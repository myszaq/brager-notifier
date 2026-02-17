import base64

from seleniumbase import BaseCase, SB

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
from page_objects.bragerconnect.login_page import LoginPage
from page_objects.bragerconnect.modules_page import ModulesPage
from services.login_service import LoginService
from utils.config_provider import ConfigProvider
from utils.logger import logger


class BragerService:
    login_page = LoginPage()
    dashboard_page = DashboardPage()
    modules_page = ModulesPage()

    page_url = ConfigProvider.get_brager_config_option("brager_url")
    object_name = ConfigProvider.get_brager_config_option("user_object")
    module_name = ConfigProvider.get_brager_config_option("module_name")
    email = base64.b64decode(secrets.brager_email).decode("utf-8")
    password = base64.b64decode(secrets.brager_password).decode("utf-8")
    fuel_level = None
    boiler_status = None
    boiler_temperature = None

    def collect_device_data(self) -> DeviceData:
        logger.info("Connecting to BragerOne application.")
        with SB(browser="chrome", maximize=True, headless=False) as sb:
            # actual timeout will be twice as much (30 seconds) due to the retry in SeleniumBase
            sb.driver.set_page_load_timeout(15)

            try:
                try:
                    sb.open(self.page_url)
                except Exception as e:
                    logger.error(f"Could not open page {self.page_url}! Exception: %s", e)
                    raise

                login_service = LoginService()
                login_service.brager_login(sb)
                self.dashboard_page.wait_for_dashboard_loaded(sb, self.module_name)
                self.fuel_level = self.dashboard_page.get_fuel_level(sb)
                self.boiler_status = self.dashboard_page.get_boiler_status(sb)
                self.boiler_temperature = self.dashboard_page.get_boiler_temperature(sb)

                # collect available data from the dashboard
                boiler_data = self._get_basic_boiler_data(sb)
                return_data = self._get_return_data(sb)
                burner_data = self._get_burner_data(sb)
                fuel_data = self._get_basic_fuel_data(sb)

                # the remaining data require opening specific components pages
                self.modules_page.open_components_page(sb)

                boiler_data = self._get_remaining_boiler_data(sb, boiler_data)
                valve_data = self._get_valve_data(sb)
                dhw_data = self._get_dhw_data(sb)
                fuel_data = self._get_remaining_fuel_data(sb, fuel_data)

                self.dashboard_page.logout(sb)

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
                sb.save_screenshot("error_screenshot.png", "logs")
                raise

    def _get_basic_boiler_data(self, sb: BaseCase) -> BoilerData:
        temperature = self.dashboard_page.get_boiler_temperature(sb)
        setting = self.dashboard_page.get_boiler_setting(sb)
        status = self.dashboard_page.get_boiler_status(sb)
        pump_status = self.dashboard_page.get_boiler_pump_status(sb)

        return BoilerData(boiler_temperature=temperature, boiler_setting=setting, boiler_status=status, boiler_pump_status=pump_status)

    def _get_remaining_boiler_data(self, sb: BaseCase, boiler_data: BoilerData) -> BoilerData:
        boiler_page = BoilerPage(sb)
        outdoor_temperature = boiler_page.get_outdoor_temperature(sb)
        boiler_data.outdoor_temperature = outdoor_temperature

        return boiler_data

    def _get_valve_data(self, sb: BaseCase):
        valve_page = ValvePage(sb)
        temperature = valve_page.get_valve_temperature(sb)
        setting = valve_page.get_valve_setting(sb)
        pump_status = valve_page.get_valve_pump_status(sb)
        oper_mode = valve_page.get_valve_operating_mode(sb)

        return ValveData(valve_temperature=temperature, valve_setting=setting, valve_pump_status=pump_status,
                         valve_operating_mode=oper_mode)

    def _get_dhw_data(self, sb: BaseCase) -> DHWData:
        dhw_page = DHWPage(sb)
        temperature = dhw_page.get_dhw_temperature(sb)
        setting = dhw_page.get_dhw_setting(sb)
        pump_status = dhw_page.get_dhw_pump_status(sb)
        oper_mode = dhw_page.get_dhw_operating_mode(sb)

        return DHWData(dhw_temperature=temperature, dhw_setting=setting, dhw_pump_status=pump_status, dhw_operating_mode=oper_mode)

    def _get_return_data(self, sb: BaseCase) -> ReturnData:
        temperature = self.dashboard_page.get_return_temperature(sb)
        pump_status = self.dashboard_page.get_return_pump_status(sb)

        return ReturnData(return_temperature=temperature, return_pump_status=pump_status)

    def _get_burner_data(self, sb: BaseCase) -> BurnerData:
        power = self.dashboard_page.get_burner_power(sb)
        flame_brightness = self.dashboard_page.get_flame_brightness(sb)
        blower_efficiency = self.dashboard_page.get_blower_efficiency(sb)

        return BurnerData(burner_power=power, flame_brightness=flame_brightness, blower_efficiency=blower_efficiency)

    def _get_basic_fuel_data(self, sb: BaseCase) -> FuelData:
        fuel_level = self.dashboard_page.get_fuel_level(sb)

        return FuelData(fuel_level=fuel_level)

    def _get_remaining_fuel_data(self, sb: BaseCase, fuel_data: FuelData) -> FuelData:
        feeder_page = FeederPage(sb)
        fuel_amount = feeder_page.get_burned_fuel_amount(sb)

        burner_page = BurnerPage(sb)
        fuel_in_24h = burner_page.get_burned_fuel_in_24h(sb)

        fuel_data.burned_fuel_amount = fuel_amount
        fuel_data.burned_fuel_in_24h = fuel_in_24h
        return fuel_data
