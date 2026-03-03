from services.browser_client import BrowserClient
from utils.selenium_helpers import SeleniumHelpers


class DashboardPage:
    start_button: str = "#menu_top_home"
    tools_button: str = "#menu_top_tools"
    logout_button: str = "#loginallowed_btn div"

    def __init__(self, browser_client: BrowserClient):
        self.browser = browser_client
        self.sh = SeleniumHelpers(self.browser.driver)

    def navigate_to_tools_menu(self):
        self.sh.wait_for_element_visible(self.start_button)
        self.sh.click(self.tools_button)

    def logout(self):
        self.sh.click(self.logout_button)
