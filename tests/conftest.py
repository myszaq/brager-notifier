import pytest

from services.browser_client import BrowserClient

driver_path = "C:\Program Files\Google\chromedriver-win64\chromedriver.exe"
@pytest.fixture
def browser():
    with BrowserClient("chrome", driver_path=driver_path, headless=False) as browser_client:
        yield browser_client
