from typing import TypedDict


class Machine(TypedDict):
    name: str
    pallets: int


class WorkType(TypedDict):
    id: str
    time_machine_needed: int


class SupplierOrder(TypedDict):
    id_work_type: str
    quantity: int


class CustomerDeadline(TypedDict):
    id_work_type: str
    quantity: int


class WorkToDo(WorkType):
    quantity_to_work: int


class WorkedQuantity(WorkType):
    worked_quantity: int
