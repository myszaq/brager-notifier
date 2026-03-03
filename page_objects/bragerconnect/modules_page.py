from selenium.webdriver.remote.webdriver import WebDriver
from utils.selenium_helpers import SeleniumHelpers


class ModulesPage:
    modules_page_link: str = "a.iNavigationRecord[href$='modules']"
    dev_id_container: str = "div.box span.title"
    default_component: str = "Kocioł"
    component_title_header: str = "div.iSideContent h2"

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.sh = SeleniumHelpers(driver)

    def open_components_page(self):
        self.sh.wait_for_element_visible(self.modules_page_link, timeout=3)
        self.sh.click(self.modules_page_link)

        self.sh.wait_for_element_visible(self.dev_id_container, timeout=3)
        self.sh.click(self.dev_id_container)
        self.sh.wait_for_text_visible(self.default_component, self.component_title_header, timeout=5)
