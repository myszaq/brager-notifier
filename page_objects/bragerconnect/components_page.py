from selenium.webdriver.remote.webdriver import WebDriver
from typing_extensions import override
from utils import utils
from utils.selenium_helpers import SeleniumHelpers


class ComponentsPage:
    component_name: str
    component_name_header: str = "div.iSideContent h2"
    switch_view_button: str = "div.iSideContent h2 + button"
    switch_view_icon: str = "i.mdi-view-column-outline, i.mdi-view-agenda-outline, i.mdi-format-columns"

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.sh = SeleniumHelpers(driver)

        allowed_classes = ["mdi-view-agenda-outline", "mdi-format-columns"]
        self.sh.wait_for_element_visible(self.switch_view_button)

        if "mdi-view-column-outline" in self.sh.get_attribute(self.switch_view_icon, "class"):
            self.sh.click(self.switch_view_button)
            class_attr = self.sh.get_attribute(self.switch_view_icon, "class")
            assert any(item in class_attr for item in allowed_classes)

    # this method needs to be overridden by each child class
    def open_component(self):
        pass

    def _is_component_view_loaded(self) -> bool:
        if not self.sh.is_element_visible(self.component_name_header):
            return False
        if self.sh.get_text(self.component_name_header) == self.component_name:
            return True
        return False


class BoilerPage(ComponentsPage):
    component_name: str = "Ustawienia kotła"
    boiler_link: str = "a.iNavigationRecord[href$='boiler']"
    outdoor_temperature_container: str = "//p[text()='Temperatura zewnętrzna']/../following-sibling::div//p"

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        if not self._is_component_view_loaded():
            self.open_component()

    @override
    def open_component(self):
        self.sh.click(self.boiler_link)
        self.sh.wait_for_text_visible(self.component_name, self.component_name_header, timeout=5)

    def get_outdoor_temperature(self) -> float:
        value = utils.get_raw_temperature(self.sh.get_text(self.outdoor_temperature_container))
        return float(value)


class FeederPage(ComponentsPage):
    component_name: str = "Podajnik"
    feeder_link: str = "a.iNavigationRecord[href$='feeder']"
    burned_fuel_amount_container: str = "//p[text()='Ilość spalonego paliwa']/../following-sibling::div//p"

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        if not self._is_component_view_loaded():
            self.open_component()

    @override
    def open_component(self):
        self.sh.click(self.feeder_link)
        self.sh.wait_for_text_visible(self.component_name, self.component_name_header, timeout=5)

    def get_burned_fuel_amount(self) -> int:
        value = self.sh.get_text(self.burned_fuel_amount_container)
        value = value.replace("kg", "")
        return int(value)


class DHWPage(ComponentsPage):
    component_name: str = "Menu CWU"
    dhw_link: str = "a.iNavigationRecord[href$='dhw']"
    dhw_temperature_container: str = "//p[text()='Temperatura CWU']/../following-sibling::div//p"
    dhw_setting_container: str = "//p[text()='Nastawa cwu']/../following-sibling::div//p"
    dhw_operating_mode_container: str = "//p[text()='Tryb pracy CWU']/../following-sibling::div//p"
    dhw_pump_status_container: str = "//p[text()='Status pompy']/../following-sibling::div//p"

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        if not self._is_component_view_loaded():
            self.open_component()

    @override
    def open_component(self):
        self.sh.click(self.dhw_link)
        self.sh.wait_for_text_visible(self.component_name, self.component_name_header, timeout=5)

    def get_dhw_temperature(self) -> float:
        value = utils.get_raw_temperature(self.sh.get_text(self.dhw_temperature_container))
        return float(value)

    def get_dhw_setting(self) -> int:
        value = utils.get_raw_temperature(self.sh.get_text(self.dhw_setting_container))
        return int(value)

    def get_dhw_pump_status(self) -> str:
        return self.sh.get_text(self.dhw_pump_status_container)

    def get_dhw_operating_mode(self) -> str:
        return self.sh.get_text(self.dhw_operating_mode_container)


class BurnerPage(ComponentsPage):
    component_name: str = "Stan palnika"
    burner_link_section: str = "//div[@class='iNavigationRecord']/div[contains(text(),'Palnik')]"
    burner_select_button: str = "//div[@class='v-list-item-title'][text()='Stan palnika']/../.."
    burned_fuel_in_24h_container: str = "//p[text()='Spalone paliwo przez 24h']/../following-sibling::div//p"

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        if not self._is_component_view_loaded():
            self.open_component()

    @override
    def open_component(self):
        self.sh.wait_for_element_visible(self.burner_link_section, timeout=3)
        self.sh.click(self.burner_link_section)
        self.sh.wait_for_element_visible(self.burner_select_button)
        self.sh.click(self.burner_select_button)
        self.sh.wait_for_text_visible(self.component_name, self.component_name_header, timeout=5)

    def get_burned_fuel_in_24h(self) -> float:
        value = self.sh.get_text(self.burned_fuel_in_24h_container)
        value = value.replace("kg", "")
        return float(value)


class ValvePage(ComponentsPage):
    component_name: str = "Zawór mieszający 1"
    valves_link_section: str = "//div[@class='iNavigationRecord']/div[contains(text(),'Zawory')]"
    valve1_select_button: str = "//div[@class='v-list-item-title'][text()='Zawór mieszający 1']/../.."
    valve_temperature_container: str = "//p[text()='Temperatura zaworu 1']/../following-sibling::div//p"
    valve_setting_container: str = "//p[text()='Nastawa zaworu 1']/../following-sibling::div//p"
    valve_operating_mode_container: str = "//p[text()='Tryb pracy zaworu 1']/../following-sibling::div//p"
    valve_pump_status_container: str = "//p[text()='Status pompy']/../following-sibling::div//p"

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        if not self._is_component_view_loaded():
            self.open_component()

    @override
    def open_component(self):
        self.sh.wait_for_element_visible(self.valves_link_section, timeout=3)
        self.sh.click(self.valves_link_section)
        self.sh.wait_for_element_visible(self.valve1_select_button)
        self.sh.click(self.valve1_select_button)
        self.sh.wait_for_text_visible(self.component_name, self.component_name_header, timeout=5)

    def get_valve_temperature(self) -> float:
        value = utils.get_raw_temperature(self.sh.get_text(self.valve_temperature_container))
        return float(value)

    def get_valve_setting(self) -> int:
        value = utils.get_raw_temperature(self.sh.get_text(self.valve_setting_container))
        return int(value)

    def get_valve_pump_status(self) -> str:
        return self.sh.get_text(self.valve_pump_status_container)

    def get_valve_operating_mode(self) -> str:
        return self.sh.get_text(self.valve_operating_mode_container)
