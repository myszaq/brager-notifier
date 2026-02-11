from dataclasses import dataclass


@dataclass
class ReturnData:
    return_temperature: float
    return_pump_status: str
