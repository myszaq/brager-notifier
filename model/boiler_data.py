from dataclasses import dataclass


@dataclass
class BoilerData:
    boiler_temperature: float
    boiler_setting: int
    boiler_status: str
    boiler_pump_status: str
    outdoor_temperature: float = None
