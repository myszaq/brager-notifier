from services.browser_client import BrowserClient
from utils.selenium_helpers import SeleniumHelpers


class ModulesPage:
    modules_page_link = "a.iNavigationRecord[href$='modules']"
    dev_id_container = "div.box span.title"
    default_component: str = "Kocioł"
    component_title_header: str = "div.iSideContent h2"

    def __init__(self, browser_client: BrowserClient):
        self.browser = browser_client
        self.sh = SeleniumHelpers(self.browser.driver)

    def open_components_page(self):
        self.sh.wait_for_element_visible(self.modules_page_link, timeout=3)
        self.sh.click(self.modules_page_link)

        self.sh.wait_for_element_visible(self.dev_id_container, timeout=3)
        self.sh.click(self.dev_id_container)
        self.sh.wait_for_text_visible(self.default_component, self.component_title_header, timeout=5)
