from dataclasses import dataclass


@dataclass
class FuelData:
    fuel_level: int
    burned_fuel_amount: int = None
    burned_fuel_in_24h: float = None
