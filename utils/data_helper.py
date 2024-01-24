import pandas as pd
from utils.data_types import *

PATH_PROBLEM_DATA = "Data/problem_data.xlsx"


def get_data_from_excel(sheet_name: str):
    data = pd.read_excel(PATH_PROBLEM_DATA, sheet_name=sheet_name).to_dict("records")
    return data


def write_data_to_excel(
    list_data: list[list[object]],
    sheet_name: list[str],
    path: str = PATH_PROBLEM_DATA,
):
    dfs = [pd.DataFrame(data) for data in list_data]
    with pd.ExcelWriter(path) as writer:
        [
            df.to_excel(writer, sheet_name=sheet_name[i], index=False)
            for i, df in enumerate(dfs)
        ]


def write_data_to_new_file_excel(data: list[object], name_file, sheet_name: str):
    dfs = [pd.DataFrame([obj.__dict__ for obj in list]) for list in data.rows]
    with pd.ExcelWriter(f"Data/{name_file}") as writer:
        for i, df in enumerate(dfs):
            df.to_excel(writer, sheet_name=f"{sheet_name} {i}", index=False)
