import enum


class NotificationType(enum.StrEnum):
    LOW_FUEL = "low_fuel"
    CRITICAL_FUEL = "critical_fuel"
    REFILL_FUEL = "refill_fuel"
    OK_FUEL = "ok_fuel"
