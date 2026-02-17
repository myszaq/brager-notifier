from dataclasses import dataclass


@dataclass
class NotificationData:
    fuel_level: int
    boiler_status: str
    boiler_temperature: float