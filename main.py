import pandas as pd
from utils.data_types import *
from utils.data_helper import *

machine: list[Machine] = get_data_from_excel("machines")
products: list[Product] = get_data_from_excel("products")
work_types: list[WorkType] = get_data_from_excel("work types")
supplier_order: list[SupplierOrder] = get_data_from_excel("supplier order")
customer_order: list[CustomerOrder] = get_data_from_excel("customer order")
products_desired: list[ProductDesired] = get_data_from_excel("products desired")

inventory = Inventory(
    products=products,
    products_desired=products_desired,
    days=DAYS,
    customer_orders=customer_order,
    supplier_orders=supplier_order,
)

# inventory_day0: list[InventoryRow] = [
#     InventoryRow(
#         id_product=f"R{p['id_product']}",
#         start_quantity=p["start_quantity"],
#         day=0,
#     )
#     for i, p in enumerate(products_desired)
# ] + [
#     InventoryRow(
#         id_product=f"F{p['id_product']}",
#         start_quantity=0,
#         day=0,
#     )
#     for i, p in enumerate(products_desired)
# ]

# inventory: list[list[InventoryRow]] = [inventory_day0] + [
#     [
#         InventoryRow(id_product=r.id_product, start_quantity=0, day=d)
#         for i, r in enumerate(inventory_day0)
#     ]
#     for d in range(1, DAYS)
# ]

write_data_to_file_excel(inventory, "inventory.xlsx", "day")

print("ciao")
# TODO: generate tasks
