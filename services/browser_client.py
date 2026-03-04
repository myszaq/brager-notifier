from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from utils.config_provider import ConfigProvider
from utils.logger import logger


class BrowserClient:

    def open(self, url: str):
        self.driver.get(url)

    def refresh(self):
        self.driver.refresh()

    def __init__(self, browser: str = None, headless: bool = True, driver_path: str = None, binary_path: str = None, ):
        self._browser_name = browser or ConfigProvider.get_browser_config_option("browser_name")
        self._headless = headless
        self._driver_path = driver_path or ConfigProvider.get_browser_config_option("driver_path")
        self._binary_path = binary_path or ConfigProvider.get_browser_config_option("binary_path")
        self.driver = None

    def __enter__(self):
        if self._browser_name == "chrome":
            options = ChromeOptions()
            if self._headless:
                options.add_argument("--headless=new")

            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--lang=pl-PL")
            options.add_argument("--disable-blink-features=AutomationControlled")

            # disable automation bar (what you already use)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            # disable password manager & save password popup, set proper browser language
            prefs = {
                "intl.accept_languages": "pl,pl-PL",
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)

            service = ChromeService(self._driver_path) if self._driver_path else ChromeService()
            try:
                self.driver = webdriver.Chrome(service=service, options=options)
            except WebDriverException as e:
                logger.error("Chrome driver could not start: %s", e)
                raise
        elif self._browser_name == "firefox":
            options = FirefoxOptions()
            if self._headless:
                options.add_argument("--headless")
            options.set_preference("intl.accept_languages", "pl,pl-PL")
            if self._binary_path:
                options.binary_location = self._binary_path
            service = FirefoxService(self._driver_path) if self._driver_path else FirefoxService()
            try:
                self.driver = webdriver.Firefox(service=service, options=options)
            except WebDriverException as e:
                logger.error("Firefox driver could not start: %s", e)
                raise
        else:
            raise ValueError(f"Unsupported browser: {self._browser_name}")

        if self._headless:
            self.driver.set_window_size(1920, 1080)
        else:
            self.driver.maximize_window()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
            self.driver = None
