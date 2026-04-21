from selenium.webdriver.remote.webdriver import WebDriver
from utils import utils
from utils.selenium_helpers import SeleniumHelpers


class DashboardPage:
    main_panel_link: str = "//div[@class='text'][contains(., 'Panel główny')]/.."
    card_title: str = ".v-card-title"
    logout_link: str = "//div[@class='text'][contains(., 'Wyloguj')]/.."
    confirm_button: str = "//button[contains(., 'Potwierdź')]"
    status_container: str = "div[role='status']"
    dashboard_container: str = "div.tw-grid div.bDashboardTile"
    fuel_level_container: str = "div[role='progressbar'][aria-describedby='{0}']"
    fuel_level_tooltip_container: str = "//div[@role='tooltip'][contains(., 'Poziom paliwa')]"
    boiler_temperature_container: str = "//p[text()='Temperatura kotła']/../following-sibling::div//p"
    boiler_setting_container: str = "//p[text()='Nastawa kotła']/../following-sibling::div//p"
    boiler_status_container: str = "span[aria-describedby='{0}']"
    boiler_status_tooltip_container: str = "//div[@role='tooltip'][contains(., 'Status kotła')]"
    boiler_pump_status_container: str = "//p[text()='Status pompy']/../following-sibling::div//p"
    return_temperature_container: str = "//p[text()='Temperatura powrotu']/../following-sibling::div//p"
    return_pump_status_container: str = "//span[text()='Powrót']/../following-sibling::div/span"
    burner_power_container: str = "//p[text()='Moc palnika']/../following-sibling::div//p"
    flame_brightness_container: str = "//p[text()='Jasność płomienia']/../following-sibling::div//p"
    blower_efficiency_container: str = "//p[text()='Wydajność dmuchawy']/../following-sibling::div//p"

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.sh = SeleniumHelpers(driver)

    def wait_for_dashboard_loaded(self, module_name: str):
        self.sh.wait_for_element_visible(self.main_panel_link, timeout=15)
        if not self.sh.is_element_visible(self.card_title):
            self.sh.refresh_page()

        self.sh.assert_text_visible(module_name, self.card_title)
        self.sh.wait_for_text_visible("Pomyślnie załadowano moduły!", self.status_container, timeout=15)
        self.sh.wait_for_element_visible(self.dashboard_container, timeout=5)

    def logout(self):
        self.sh.click(self.logout_link)
        self.sh.wait_for_element_visible(self.confirm_button)
        self.sh.click(self.confirm_button)

    def get_fuel_level(self) -> int:
        tooltip_id = self.sh.get_attribute(self.fuel_level_tooltip_container, "id")
        fuel_level = self.sh.get_attribute(self.fuel_level_container.format(tooltip_id), "aria-valuenow")
        return int(fuel_level)

    def get_boiler_temperature(self) -> float:
        value = utils.get_raw_temperature(self.sh.get_text(self.boiler_temperature_container))
        return float(value)

    def get_boiler_setting(self) -> int:
        value = utils.get_raw_temperature(self.sh.get_text(self.boiler_setting_container))
        return int(value)

    def get_boiler_status(self) -> str:
        tooltip_id = self.sh.get_attribute(self.boiler_status_tooltip_container, "id")
        return self.sh.get_text(self.boiler_status_container.format(tooltip_id))

    def get_boiler_pump_status(self) -> str:
        return self.sh.get_text(self.boiler_pump_status_container)

    def get_return_temperature(self) -> float:
        value = utils.get_raw_temperature(self.sh.get_text(self.return_temperature_container))
        return float(value)

    def get_return_pump_status(self) -> str:
        return self.sh.get_text(self.return_pump_status_container)

    def get_burner_power(self) -> float:
        burner_power = self.sh.get_text(self.burner_power_container)
        burner_power = burner_power.replace("kW", "")
        return float(burner_power)

    def get_flame_brightness(self) -> int:
        flame_brightness = self.sh.get_text(self.flame_brightness_container)
        flame_brightness = flame_brightness.replace("%", "")
        return int(flame_brightness)

    def get_blower_efficiency(self) -> int:
        blower_efficiency = self.sh.get_text(self.blower_efficiency_container)
        blower_efficiency = blower_efficiency.replace("%", "")
        return int(blower_efficiency)
