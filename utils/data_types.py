from typing import TypedDict

# CONSTANTS
TIME_MACHINE_SETUP = 100
TIME_OPERATOR_FOR_EACH_WORK = 50
MAX_TIME_MACHINE_FOR_EACH_WORK = 50

COST_MACHINE_SETUP = 100
_DAILY_WORKING_HOURS = 10
DAILY_WORKING_MINUTES = _DAILY_WORKING_HOURS * 60
DAYS = 10
NUMBER_OF_MACHINES = 4
NUMBER_OF_PRODUCTS = 5


# DATA TYPES
class Machine(TypedDict):
    name: str
    pallets: int


class WorkType(TypedDict):
    id: str
    time_machine_needed: int


class CustomerDeadline(TypedDict):
    id_work_type: str
    quantity: int


class WorkToDo(WorkType):
    quantity_to_work: int


class WorkedQuantity(WorkType):
    worked_quantity: int
