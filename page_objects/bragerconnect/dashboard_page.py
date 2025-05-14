from seleniumbase import BaseCase


class DashboardPage:
    main_panel_link: str = "div.iNavigationDrawer a.router-link-active"
    card_title: str = ".v-card-title"
    logout_button: str = "//div[@class='text'][contains(., 'Wyloguj')]/.."
    confirm_button: str = "//button[contains(., 'Potwierdź')]"
    fuel_level_container: str = "div[role='progressbar'][aria-describedby='{0}']"
    fuel_level_tooltip_container: str = "//div[@role='tooltip'][contains(., 'Poziom paliwa')]"
    boiler_status_container: str = "span[aria-describedby='{0}']"
    boiler_status_tooltip_container: str = "//div[@role='tooltip'][contains(., 'Status kotła')]"
    boiler_temperature_container: str = "//p[text()='Temperatura kotła']/../following-sibling::div//p"

    def wait_for_dashboard_loaded(self, sb: BaseCase, module_name: str):
        sb.wait_for_element(self.main_panel_link, timeout=20)
        sb.assert_text_visible(module_name, self.card_title)

    def get_fuel_level(self, sb: BaseCase) -> int:
        tooltip_id = sb.get_attribute(self.fuel_level_tooltip_container, "id")
        fuel_level = sb.get_attribute(self.fuel_level_container.format(tooltip_id), "aria-valuenow")
        return int(fuel_level)

    def get_boiler_status(self, sb: BaseCase) -> str:
        tooltip_id = sb.get_attribute(self.boiler_status_tooltip_container, "id")
        boiler_status = sb.get_text(self.boiler_status_container.format(tooltip_id))
        return boiler_status

    def get_boiler_temperature(self, sb: BaseCase) -> str:
        return sb.get_text(self.boiler_temperature_container)

    def logout(self, sb: BaseCase):
        sb.click(self.logout_button)
        sb.wait_for_element(self.confirm_button)
        sb.click(self.confirm_button)
