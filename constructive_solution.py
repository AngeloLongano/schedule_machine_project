import pandas as pd
from utils.data_types import *
from utils.data_helper import *
from utils.plot_helper import draw_gantt_chart

machines: list[Machine] = get_data_from_excel("machines")
work_types: list[WorkType] = get_data_from_excel("work types")
supplier_orders: list[SupplierOrder] = get_data_from_excel("supplier order")
customer_deadlines: list[CustomerDeadline] = get_data_from_excel("customer order")

from utils.algorithms import *

solution = Solution(
    machines,
    work_types,
    supplier_orders,
    customer_deadlines,
)

solution.constructive_solution()

draw_gantt_chart(solution.schedule, work_types)
