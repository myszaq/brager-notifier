from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from utils.selenium_helpers import SeleniumHelpers


class CommonPage:
    main_panel_link: str = "//div[@class='text'][contains(., 'Panel główny')]/.."
    login_button: str = "//button[contains(., 'Zaloguj')]"
    status_container: str = "div[role='status']"

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.sh = SeleniumHelpers(driver)

    def is_main_page_loaded(self) -> bool:
        # noinspection PyBroadException
        try:
            self.sh.wait_for_element_not_visible(self.login_button, timeout=3)
        except Exception:
            return False

        try:
            wait = WebDriverWait(self.driver, timeout=10, poll_frequency=0.25)
            wait.until(lambda _: self.sh.is_element_visible(self.main_panel_link))
        except TimeoutException:
            pass
        return self.sh.is_element_visible(self.main_panel_link)

    def get_browser_storage_data(self) -> dict:
        self.sh.wait_for_text_visible("Pomyślnie załadowano moduły!", self.status_container, timeout=15)
        js_script = r"""
return {
    selectedObjectId: localStorage.getItem('selectedObjectId'),
    accessToken: sessionStorage.getItem('accessToken'),
    refreshToken: sessionStorage.getItem("refreshToken")
};
"""
        return self.sh.execute_script(js_script)

    def set_browser_storage_data(self, storage_data: dict):
        # case when we don't have all expected values in the dict
        required_keys = ["selectedObjectId", "accessToken", "refreshToken"]
        if not all(k in storage_data and storage_data[k] for k in required_keys):
            return

        js_script = f"""
localStorage.setItem('selectedObjectId', '{storage_data["selectedObjectId"]}');
sessionStorage.setItem('accessToken', '{storage_data["accessToken"]}');
sessionStorage.setItem('refreshToken', '{storage_data["refreshToken"]}');
"""
        self.sh.execute_script(js_script)
