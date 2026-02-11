from dataclasses import dataclass


@dataclass
class ValveData:
    valve_temperature: float
    valve_setting: int
    valve_pump_status: str
    valve_operating_mode: str
