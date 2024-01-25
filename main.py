from utils.data_types import *
from utils.data_helper import *
from utils.algorithms import *

machines: list[Machine] = get_data_from_excel("machines")
work_types: list[WorkType] = get_data_from_excel("work types")
customer_deadlines: list[CustomerDeadline] = get_data_from_excel("customer deadlines")

solution = Solution(
    machines,
    work_types,
    customer_deadlines,
)

solution.constructive_solution()

print(solution)

# write_data_to_file_excel(inventory, "inventory.xlsx", "day")

print("ciao")
# TODO: generate tasks
