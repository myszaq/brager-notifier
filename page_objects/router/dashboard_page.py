from seleniumbase import BaseCase


class DashboardPage:
    start_button: str = "#menu_top_home"
    tools_button: str = "#menu_top_tools"
    logout_button: str = "#loginallowed_btn div"

    def navigate_to_tools_menu(self, sb: BaseCase):
        sb.wait_for_element(self.start_button)
        sb.click(self.tools_button)

    def logout(self, sb: BaseCase):
        sb.click(self.logout_button)
