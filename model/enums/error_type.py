from enum import StrEnum


class ErrorType(StrEnum):
    READ_DATA_ERROR = "read_data_error"
    SAVE_DATA_ERROR = "save_data_error"