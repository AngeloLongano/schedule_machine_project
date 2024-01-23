from utils.helpers import list_random_with_fixed_sum
from utils.data_types import *
from utils.constraints import *
import pandas as pd
import random

random.seed(0)


def calculate_max_possible_products():
    max_products = 0
    for m in machines:
        if m["pallets"] == 1:
            max_products += int(
                DAILY_WORKING_MINUTES / (MAX_TIME_MACHINE + TIME_OPERATOR_FOR_EACH_WORK)
            )
        else:
            max_products += (
                int(
                    (DAILY_WORKING_MINUTES - TIME_OPERATOR_FOR_EACH_WORK)
                    // (MAX_TIME_MACHINE * m["pallets"])
                )
                * m["pallets"]
            )
    max_products *= DAYS
    return max_products


machines: list[Machine] = [
    {"name": "M1", "pallets": 1},
    {"name": "M2", "pallets": 1},
    {"name": "M3", "pallets": 2},
    {"name": "M4", "pallets": 3},
]

work_types: list[WorkType] = [
    {
        "id": f"W{i}",
        "time_machine_needed": random.randrange(10, MAX_TIME_MACHINE, 10),
    }
    for i in range(0, NUMBER_OF_PRODUCTS)
]

max_products = calculate_max_possible_products()
list_desired_quantity = list_random_with_fixed_sum(max_products, NUMBER_OF_PRODUCTS)


supplier_order: list[SupplierOrder] = [
    {
        "id_work_type": w["id"],
        "quantity": list_desired_quantity[i],
    }
    for i, w in enumerate(work_types)
]

customer_order: list[CustomerDeadline] = [
    {
        "id_work_type": w["id"],
        "quantity": list_desired_quantity[i],
    }
    for i, w in enumerate(work_types)
]


# WRITE DATA TO EXCEL

machines = pd.DataFrame(machines)
work_types = pd.DataFrame(work_types)
supplier_order = pd.DataFrame(supplier_order)
customer_order = pd.DataFrame(customer_order)

with pd.ExcelWriter(DATA_PATH) as writer:
    machines.to_excel(writer, sheet_name="machines", index=False)
    work_types.to_excel(writer, sheet_name="work types", index=False)
    supplier_order.to_excel(writer, sheet_name="supplier order", index=False)
    customer_order.to_excel(writer, sheet_name="customer order", index=False)
