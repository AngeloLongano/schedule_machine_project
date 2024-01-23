from utils.data_types import *
from utils.data_helper import *
from utils.constraints import *
from utils.entities_choice import *

machines: list[Machine] = get_data_from_excel("machines")
work_types: list[WorkType] = get_data_from_excel("work types")
supplier_orders: list[SupplierOrder] = get_data_from_excel("supplier order")
customer_deadlines: list[CustomerDeadline] = get_data_from_excel("customer order")

solution = Solution(
    machines,
    work_types,
    supplier_orders,
    customer_deadlines,
)

solution.constructive_solution()

print(solution)

# write_data_to_file_excel(inventory, "inventory.xlsx", "day")

print("ciao")
# TODO: generate tasks
