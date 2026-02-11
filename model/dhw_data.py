from dataclasses import dataclass


@dataclass
class DHWData:
    dhw_temperature: float
    dhw_setting: int
    dhw_pump_status: str
    dhw_operating_mode: str
