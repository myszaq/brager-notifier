from seleniumbase import BaseCase


class LoginPage:
    password_field: str = "#login_password"
    login_button: str = "#login_btn"
    start_button: str = "#menu_top_home"

    def login(self, sb: BaseCase, password: str):
        sb.wait_for_element(self.login_button)
        sb.type(self.password_field, password)
        sb.click(self.login_button)
        sb.wait_for_element_not_present(self.login_button)
