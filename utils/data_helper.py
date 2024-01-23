import pandas as pd
from utils.data_types import *
from utils.constraints import *

## Mapping for numpy


def get_data_from_excel(sheet_name: str):
    data = pd.read_excel(DATA_PATH, sheet_name=sheet_name).to_dict("records")
    return data


def write_data_to_file_excel(data: list[object], name_file, sheet_name: str):
    dfs = [pd.DataFrame([obj.__dict__ for obj in list]) for list in data.rows]
    with pd.ExcelWriter(f"Data/{name_file}") as writer:
        for i, df in enumerate(dfs):
            df.to_excel(writer, sheet_name=f"{sheet_name} {i}", index=False)
