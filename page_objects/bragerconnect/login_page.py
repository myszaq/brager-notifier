from selenium.common.exceptions import ElementNotVisibleException
from seleniumbase import BaseCase


class LoginPage:
    page_title: str = "h1.pageTitle"
    email_container: str = "//input[@id='input-3']/.."
    email_field: str = "#input-3"
    password_container: str = "//input[@id='input-5']/.."
    password_field: str = "#input-5"
    login_button: str = "//button[contains(., 'Zaloguj')]"
    next_button: str = "//button[contains(., 'Dalej')]"
    choose_object_dropdown: str = "//label[text()='Wybierz obiekt']/.."
    choose_object_dropdown2: str = "//label[text()='Wybierz obiekt']/../div[@class='v-field__input']"
    choose_object_option: str = "div.v-list-item-title:contains('{0}')"

    def proceed_to_login(self, sb: BaseCase):
        sb.wait_for_element_visible(self.login_button, timeout=10)
        sb.click(self.login_button)
        sb.wait_for_text_visible("Zaloguj się", self.page_title, timeout=5)

    def login_user(self, sb: BaseCase, email: str, password: str):
        sb.click(self.email_container)
        sb.type(self.email_field, email)
        sb.click(self.password_container)
        sb.type(self.password_field, password)
        sb.click(self.next_button)
        sb.wait_for_text_visible("Wybierz rolę", self.page_title, timeout=10)

    def choose_object(self, sb: BaseCase, object_name: str):
        try:
            sb.click(self.choose_object_dropdown)
            sb.wait_for_element(self.choose_object_option.format(object_name))
        except ElementNotVisibleException:
            sb.click(self.choose_object_dropdown)
            sb.click(self.choose_object_dropdown2)
            sb.wait_for_element(self.choose_object_option.format(object_name))

        sb.click(self.choose_object_option.format(object_name))
        sb.click(self.next_button)
