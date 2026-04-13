import time
from typing import Callable
from selenium.common import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
from .logger import logger

RETRYABLE_EXCEPTIONS = (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)


def get_raw_temperature(input_str: str) -> str:
    return input_str.replace("°C", "")


def run_method_with_retry(function: Callable, *args, on_retry: Callable | None = None, attempts: int = 2):
    last_exception = None

    for i in range(attempts):
        try:
            return function(*args)
        except RETRYABLE_EXCEPTIONS as e:
            last_exception = e
            logger.warning(f"Method {function.__qualname__} failed on attempt #{i + 1}: {e}")

            if i < attempts - 1:
                if on_retry is not None:
                    on_retry()
                time.sleep(0.5)

    logger.error(f"Method {function.__qualname__} failed after {attempts} attempts!")
    raise last_exception
