from selenium.common.exceptions import ElementNotVisibleException

from services.browser_client import BrowserClient
from utils.selenium_helpers import SeleniumHelpers


class LoginPage:
    page_title: str = "h1.pageTitle"
    email_container: str = "//input[@id='input-v-3']/.."
    email_field: str = "#input-v-3"
    password_container: str = "//input[@id='input-v-5']/.."
    password_field: str = "#input-v-5"
    login_button: str = "//button[contains(., 'Zaloguj')]"
    next_button: str = "//button[contains(., 'Dalej')]"
    choose_object_dropdown: str = "//label[text()='Wybierz obiekt']/.."
    choose_object_dropdown2: str = "//label[text()='Wybierz obiekt']/../div[@class='v-field__input']"
    choose_object_option: str = "div.v-list-item-title:contains('{0}')"

    def __init__(self, browser_client: BrowserClient):
        self.browser = browser_client
        self.sh = SeleniumHelpers(self.browser.driver)

    def proceed_to_login(self):
        self.sh.wait_for_element_visible(self.login_button, timeout=10)
        self.sh.click(self.login_button)
        self.sh.wait_for_text_visible("Zaloguj się", self.page_title, timeout=5)

    def login_user(self, email: str, password: str):
        self.sh.click(self.email_container)
        self.sh.type(self.email_field, email)
        self.sh.click(self.password_container)
        self.sh.type(self.password_field, password)
        self.sh.click(self.next_button)
        self.sh.wait_for_text_visible("Wybierz rolę", self.page_title, timeout=10)

    def choose_object(self, object_name: str):
        try:
            self.sh.click(self.choose_object_dropdown)
            self.sh.wait_for_element_visible(self.choose_object_option.format(object_name))
        except ElementNotVisibleException:
            self.sh.click(self.choose_object_dropdown)
            self.sh.click(self.choose_object_dropdown2)
            self.sh.wait_for_element_visible(self.choose_object_option.format(object_name))

        self.sh.click(self.choose_object_option.format(object_name))
        self.sh.click(self.next_button)
