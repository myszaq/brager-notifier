from selenium.webdriver.remote.webdriver import WebDriver
from utils.selenium_helpers import SeleniumHelpers


class LoginPage:
    password_field: str = "#login_password"
    login_button: str = "#login_btn"
    start_button: str = "#menu_top_home"

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.sh = SeleniumHelpers(driver)

    def login(self, password: str):
        self.sh.wait_for_element_visible(self.login_button)
        self.sh.type(self.password_field, password)
        self.sh.click(self.login_button)
        self.sh.wait_for_element_not_present(self.login_button)
