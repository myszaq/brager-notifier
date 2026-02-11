from dataclasses import dataclass

from model.boiler_data import BoilerData
from model.burner_data import BurnerData
from model.dhw_data import DHWData
from model.fuel_data import FuelData
from model.return_data import ReturnData
from model.valve_data import ValveData


@dataclass
class DeviceData:
    boiler: BoilerData
    valve: ValveData
    dhw: DHWData
    flow_return: ReturnData
    burner: BurnerData
    fuel: FuelData
