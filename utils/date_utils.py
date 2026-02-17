from datetime import datetime

DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"


def get_current_datetime() -> str:
    return datetime.now().strftime(DATETIME_FORMAT)


def get_time_difference(datetime_first: str, datetime_last: str) -> int:
    time_diff = get_datetime_from_string(datetime_last) - get_datetime_from_string(datetime_first)
    return int(time_diff.total_seconds())


def get_datetime_from_string(input_str: str) -> datetime:
    try:
        return datetime.strptime(input_str, DATETIME_FORMAT)
    except ValueError:
        raise
