from seleniumbase import BaseCase


class ModulesPage:
    modules_page_link = "a.iNavigationRecord[href$='modules']"
    dev_id_container = "div.box span.title"
    default_component: str = "Kocioł"
    component_title_header: str = "div.iSideContent h2"

    def open_components_page(self, sb: BaseCase):
        sb.wait_for_element(self.modules_page_link, timeout=3)
        sb.click(self.modules_page_link)

        sb.wait_for_element(self.dev_id_container, timeout=3)
        sb.click(self.dev_id_container)
        sb.wait_for_text_visible(self.default_component, self.component_title_header, timeout=5)