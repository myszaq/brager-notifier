from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


class SeleniumHelpers:
    """
    Set of helper methods handling web elements, inspired by the methods of SeleniumBase.
    """

    def __init__(self, driver, timeout=10):
        """
        Initialize SeleniumHelpers with a WebDriver instance and default timeout.

        :param driver: Selenium WebDriver instance
        :param timeout: Default timeout in seconds for waiting methods (default 10)
        """
        self.driver = driver
        self.timeout = timeout

    def wait_for_element_visible(self, selector: str, by=None, timeout=None):
        """
        Wait until the element is visible on the page.

        :param selector: Element selector (CSS or XPath)
        :param by: Optional selector type (auto-detected if None)
        :param timeout: Timeout in seconds (defaults to self.timeout)
        :return: WebElement once it becomes visible
        """
        actual_timeout = timeout or self.timeout
        actual_by = by or self._detect_selector_type(selector)

        return WebDriverWait(self.driver, actual_timeout).until(
            conditions.visibility_of_element_located((actual_by, selector))
        )

    def wait_for_element_not_visible(self, selector: str, by=None, timeout=None):
        """
        Wait until the element is not visible on the page.

        This passes if:
        - the element becomes invisible
        - the element is removed from DOM

        :param selector: Element selector (CSS or XPath)
        :param by: Optional selector type (auto-detected if None)
        :param timeout: Timeout in seconds (defaults to self.timeout)
        :return: True if condition is met
        """
        actual_timeout = timeout or self.timeout
        actual_by = by or self._detect_selector_type(selector)

        return WebDriverWait(self.driver, actual_timeout).until(
            conditions.invisibility_of_element_located((actual_by, selector))
        )

    def wait_for_element_not_present(self, selector: str, by=None, timeout=None):
        """
        Wait until the element is no longer present in the DOM.

        This passes only when:
        - the element is completely removed from DOM

        :param selector: Element selector (CSS or XPath)
        :param by: Optional selector type (auto-detected if None)
        :param timeout: Timeout in seconds (defaults to self.timeout)
        :return: True if condition is met
        """
        actual_timeout = timeout or self.timeout
        actual_by = by or self._detect_selector_type(selector)

        def element_not_present(driver):
            elements = driver.find_elements(actual_by, selector)
            return len(elements) == 0

        return WebDriverWait(self.driver, actual_timeout).until(
            element_not_present
        )

    def wait_for_text_visible(self, text: str, selector: str = None, by=None, timeout=None):
        """
        Wait until the given text is visible on the page.

        :param text: Text to wait for
        :param selector: Optional element selector (CSS or XPath).
                         If None, searches the whole page body.
        :param by: Optional selector type (auto-detected if None)
        :param timeout: Timeout in seconds (defaults to self.timeout)
        :return: True once the text is visible
        """
        actual_timeout = timeout or self.timeout
        actual_by = by or self._detect_selector_type(selector)

        if selector:
            return WebDriverWait(self.driver, actual_timeout).until(
                conditions.text_to_be_present_in_element((actual_by, selector), text)
            )
        else:
            return WebDriverWait(self.driver, actual_timeout).until(
                lambda driver: text in driver.find_element(By.TAG_NAME, "body").text
            )

    def click(self, selector: str, by=None):
        """
        Wait until the element is visible and clickable, then click it.

        :param selector: Element selector (CSS or XPath)
        :param by: Optional selector type (auto-detected if None)
        :return: WebElement that was clicked
        """
        actual_by = by or self._detect_selector_type(selector)
        element = self.wait_for_element_visible(selector, actual_by)

        # Wait until the element is clickable
        WebDriverWait(self.driver, self.timeout).until(
            conditions.element_to_be_clickable((actual_by, selector))
        )

        element.click()
        return element

    def type(self, selector: str, text: str, by=None, clear_first=True, timeout=None):
        """
        Wait until the element is visible, optionally clear it, then type the given text.

        :param selector: Element selector (CSS or XPath)
        :param text: Text to type into the element
        :param by: Optional selector type (auto-detected if None)
        :param clear_first: Whether to clear the element before typing (default True)
        :param timeout: Timeout in seconds (defaults to self.timeout)
        :return: WebElement where text was typed
        """
        actual_timeout = timeout or self.timeout
        actual_by = by or self._detect_selector_type(selector)
        element = self.wait_for_element_visible(selector, actual_by, actual_timeout)

        if clear_first:
            element.clear()
        element.send_keys(text)
        return element

    def get_text(self, selector: str, by=None):
        """
        Wait until the element is visible, then return its text.

        :param selector: Element selector (CSS or XPath)
        :param by: Optional selector type (auto-detected if None)
        :return: Text content of the element
        """
        actual_by = by or self._detect_selector_type(selector)
        element = self.wait_for_element_visible(selector, actual_by)
        return element.text

    def get_attribute(self, selector: str, attribute_name: str, by=None, timeout=None):
        """
        Get attribute value from an element.

        :param selector: Element selector (CSS or XPath)
        :param attribute_name: Name of the attribute to retrieve
        :param by: Optional selector type (auto-detected if None)
        :param timeout: Timeout in seconds (defaults to self.timeout)
        :return: Attribute value (str or None)
        """
        actual_timeout = timeout or self.timeout
        actual_by = by or self._detect_selector_type(selector)
        element = WebDriverWait(self.driver, actual_timeout).until(
            conditions.visibility_of_element_located((actual_by, selector))
        )

        return element.get_attribute(attribute_name)

    def execute_script(self, script, *args):
        """
        Execute JavaScript in the context of the current page.

        :param script: JavaScript code as string
        :param args: Optional arguments passed to the script
        :return: Value returned by the script
        """
        return self.driver.execute_script(script, *args)

    def refresh_page(self):
        """
        Refresh the current page.
        Equivalent of SB's sb.refresh_page().
        """
        self.driver.refresh()

    def is_element_visible(self, selector: str, by=None):
        """
        Check if the element is visible on the page.

        :param selector: Element selector (CSS or XPath)
        :param by: Optional selector type (auto-detected if None)
        :return: True if the element is visible, False otherwise
        """
        actual_by = by or self._detect_selector_type(selector)
        # noinspection PyBroadException
        try:
            self.wait_for_element_visible(selector, actual_by)
            return True
        except Exception:
            return False

    def assert_text_visible(self, text: str, selector: str = None, by=None, timeout=None):
        """
        Assert that the given text is visible.

        :param text: Expected text
        :param selector: If provided, checks inside a specific element.
                         If None, checks the whole page body.
        :param by: Optional selector type (auto-detected if None)
        :param timeout: Timeout in seconds (defaults to self.timeout)
        """
        actual_timeout = timeout or self.timeout

        try:
            if selector:
                actual_by = by or self._detect_selector_type(selector)
                WebDriverWait(self.driver, actual_timeout).until(
                    conditions.text_to_be_present_in_element((actual_by, selector), text)
                )
            else:
                WebDriverWait(self.driver, actual_timeout).until(
                    lambda driver: text in driver.find_element(By.TAG_NAME, "body").text
                )
        except TimeoutException:
            if selector:
                raise AssertionError(f"Text '{text}' was not visible in element '{selector}' after {actual_timeout} seconds.")
            else:
                raise AssertionError(f"Text '{text}' was not visible on the page after {actual_timeout} seconds.")

    def _detect_selector_type(self, selector: str):
        xpath_indicators = ("//", "./", "(/")
        if selector.startswith(xpath_indicators) or selector.startswith("("):
            return By.XPATH

        return By.CSS_SELECTOR
