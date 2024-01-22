from typing import TypedDict, Any
from enum import Enum

TIME_MACHINE_SETUP = 100
TIME_OPERATOR_FOR_EACH_WORK = 50
MAX_TIME_MACHINE = 50

COST_MACHINE_SETUP = 100
_DAILY_WORKING_HOURS = 10
DAILY_WORKING_MINUTES = _DAILY_WORKING_HOURS * 60
DAYS = 10
NUMBER_OF_MACHINES = 3
NUMBER_OF_PRODUCTS = 5


class Machine(TypedDict):
    id: str
    pallets: int


class WorkType(TypedDict):
    id: str
    id_raw_product: str
    id_final_product: str
    time_machine_needed: int


class Product(TypedDict):
    id: str
    type: str  # RAW or FINAL


class SupplierOrder(TypedDict):
    id: str
    id_raw_product: str
    quantity_to_add: int
    day: int


class CustomerOrder(TypedDict):
    id: str
    id_final_product: str
    quantity_to_remove: int
    day: int


class ProductDesired(TypedDict):
    general_id: str
    start_quantity: int
    total_quantity: int
    min_final_quantity: int  # TODO: maybe to remove
    max_final_quantity: int


class InventoryRow:
    def __init__(
        self,
        id_product: str,
        start_quantity: int,
        day: int,
    ):
        self.id_product = id_product
        self.start_quantity = start_quantity
        self.used_quantity = 0
        self.generated_quantity = 0
        self.day = day
        self.id = f"RI_{self.id_product}_D{self.day}"

    def current_quantity(self):
        """
        Method to calculate the current quantity of the product
        """
        return self.start_quantity + self.generated_quantity - self.used_quantity


class Inventory:
    def __init__(
        self,
        products: list[Product],
        products_desired: list[ProductDesired],
        days: int,
        customer_orders: list[CustomerOrder],
        supplier_orders: list[SupplierOrder],
    ):
        self.rows: list[list[InventoryRow]] = []
        self._init_rows(products_desired, days)
        self._add_customer_orders(customer_orders)
        self._add_supplier_orders(supplier_orders)
        [self._update_rows(p["id"]) for p in products]

    def _init_rows(self, products_desired: list[ProductDesired], days: int):
        """
        Method to initialize the rows of the inventory for the first day
        """
        for day in range(days):
            self.rows.append([])
            for product in products_desired:
                for type in ["R", "F"]:
                    row = InventoryRow(
                        id_product=f"{type}{product['id_general_product']}",
                        start_quantity=product["start_quantity"]
                        if day == 0 and type == "R"
                        else 0,
                        day=day,
                    )
                    self.rows[day].append(row)

    def check_inventory(self):
        # TODO : check if is correct
        return next(
            (
                (row, day)
                for day, rows_day in self.rows
                for row in rows_day
                if row.current_quantity() < 0
            ),
            True,
        )

    def current_quantity(self, id_product: str, day: int):
        row: InventoryRow = filter(lambda x: x.id_product == id_product, self.rows[day])
        return row.current_quantity()

    def _add_supplier_orders(self, supplier_orders: list[SupplierOrder]):
        for supplier_order in supplier_orders:
            row: InventoryRow = list(
                filter(
                    lambda x: x.id_product == supplier_order["id_raw_product"],
                    self.rows[supplier_order["day"]],
                )
            )[0]
            row.start_quantity += supplier_order["quantity_to_add"]

    def _add_customer_orders(self, customer_orders: list[CustomerOrder]):
        for customer_order in customer_orders:
            row: InventoryRow = list(
                filter(
                    lambda x: x.id_product == customer_order["id_final_product"],
                    self.rows[customer_order["day"]],
                )
            )[0]
            row.start_quantity -= customer_order["quantity_to_remove"]

    def _update_rows(self, id_product: str, day: int = 1):
        for d in range(day + 1, DAYS):
            previous_row: InventoryRow = list(
                filter(lambda x: x.id_product == id_product, self.rows[d - 1])
            )[0]
            previous_quantity = previous_row.current_quantity()

            row: InventoryRow = list(
                filter(lambda x: x.id_product == id_product, self.rows[d])
            )[0]
            row.start_quantity += previous_quantity

    def generate_quantity(self, id_product: str, day: int, quantity: int):
        row: InventoryRow = filter(lambda x: x.id_product == id_product, self.rows[day])
        row.generated_quantity += quantity
        self._update_rows(id_product, day)

    def use_quantity(self, id_product: str, day: int, quantity: int):
        row: InventoryRow = filter(lambda x: x.id_product == id_product, self.rows[day])
        row.used_quantity += quantity
        self._update_rows(id_product, day)


class QuantityUsed(TypedDict):
    id_raw_product: str
    quantity_to_remove: int


class QuantityGenerated(TypedDict):
    id_final_product: str
    quantity_to_add: int


class Job:
    counter_id = 0

    def __init__(
        self,
        list_works: list[WorkType],
        quantity_to_produce: int,
        day: int,
    ):
        self.id = f"T{Job.counter_id}"
        Job.counter_id += 1
        self.list_works = list_works
        self.quantity_to_produce = quantity_to_produce

    def products_generated(self) -> list[QuantityGenerated]:
        return [
            {
                "id_final_product": w["id_final_product"],
                "quantity_to_add": self.quantity_to_produce,
            }
            for w in self.list_works
        ]

    def products_used(self) -> list[QuantityUsed]:
        return [
            {
                "id_raw_product": w["id_raw_product"],
                "quantity_to_remove": self.quantity_to_produce,
            }
            for w in self.list_works
        ]

    def time_machine_needed(self) -> int:
        # TODO: not considered time_machine_setup
        if self.list_works == []:
            return 0
        if len(self.list_works) == 1:
            return (
                self.list_works[0]["time_machine_needed"] + TIME_OPERATOR_FOR_EACH_WORK
            ) * self.quantity_to_produce

        return (
            sum([w["time_machine_needed"] for w in self.list_works])
            + TIME_OPERATOR_FOR_EACH_WORK
        ) * self.quantity_to_produce


class ScheduleMachine:
    machine: Machine
    list_jobs: list[Job]

    def __init__(self, machine: Machine, list_jobs: list[Job]):
        self.machine = machine
        self.list_jobs = list_jobs

    def calculate_time(self):
        return sum([j.time_machine_needed() for j in self.jobs])

    def calculate_cost(self):
        return sum([COST_MACHINE_SETUP for _ in self.jobs])

    def remaining_time(self):
        return DAILY_WORKING_MINUTES * DAYS - self.calculate_time()
