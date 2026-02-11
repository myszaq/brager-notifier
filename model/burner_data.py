from dataclasses import dataclass


@dataclass
class BurnerData:
    burner_power: float
    flame_brightness: int
    blower_efficiency: int
