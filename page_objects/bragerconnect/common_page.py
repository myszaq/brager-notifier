from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import BaseCase


class CommonPage:
    main_panel_link: str = "//div[@class='text'][contains(., 'Panel główny')]/.."
    login_button: str = "//button[contains(., 'Zaloguj')]"
    status_container = "div[role='status']"

    def is_main_page_loaded(self, sb: BaseCase) -> bool:
        # noinspection PyBroadException
        try:
            sb.wait_for_element_not_visible(self.login_button, timeout=3)
        except Exception:
            return False

        try:
            wait = WebDriverWait(sb.driver, timeout=10, poll_frequency=0.25)
            wait.until(lambda _: sb.is_element_visible(self.main_panel_link))
        except TimeoutException:
            pass
        return sb.is_element_visible(self.main_panel_link)

    def get_browser_storage_data(self, sb: BaseCase) -> dict:
        sb.wait_for_text_visible("Pomyślnie załadowano moduły!", self.status_container, timeout=10)
        js_script = r"""
return {
    selectedObjectId: localStorage.getItem('selectedObjectId'),
    accessToken: sessionStorage.getItem('accessToken'),
    refreshToken: sessionStorage.getItem("refreshToken")
};
"""
        return sb.execute_script(js_script)

    def set_browser_storage_data(self, sb: BaseCase, storage_data: dict):
        # case when we don't have all expected values in the dict
        required_keys = ["selectedObjectId", "accessToken", "refreshToken"]
        if not all(k in storage_data and storage_data[k] for k in required_keys):
            return

        js_script = f"""
localStorage.setItem('selectedObjectId', '{storage_data["selectedObjectId"]}');
sessionStorage.setItem('accessToken', '{storage_data["accessToken"]}');
sessionStorage.setItem('refreshToken', '{storage_data["refreshToken"]}');
"""
        sb.execute_script(js_script)
