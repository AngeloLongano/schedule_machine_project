from utils.data_helper import write_data_to_excel
from utils.data_types import *
import random

random.seed(0)

# UTIL FUNCTIONS


def list_random_with_fixed_sum(fixed_sum, num_values, step_value=5):
    random_numbers = [random.random() for _ in range(num_values)]

    sum_random_numbers = sum(random_numbers)

    normalized_numbers = [
        int((fixed_sum * num) / sum_random_numbers) for num in random_numbers
    ]

    normalized_numbers = [
        round(n / step_value) * step_value for num in normalized_numbers
    ]

    sum_random_numbers = sum(normalized_numbers)

    if sum_random_numbers < fixed_sum:
        normalized_numbers[normalized_numbers.index(min(normalized_numbers))] += (
            fixed_sum - sum_random_numbers
        )
    elif sum_random_numbers > fixed_sum:
        normalized_numbers[normalized_numbers.index(max(normalized_numbers))] -= (
            sum_random_numbers - fixed_sum
        )

    return normalized_numbers


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


# DEFINE DATA

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
write_data_to_excel(
    [machines, work_types, supplier_order, customer_order],
    ["machines", "work types", "supplier order", "customer order"],
)
