import pandas as pd
from utils.algorithms import Schedule
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


def print_solution(schedule: list[Schedule]):
    for schedule_machine in schedule:
        print(f"Macchina {schedule_machine.machine}")
        for i_j, job in enumerate(schedule_machine.list_jobs):
            print(f"Job {i_j}")
            print(
                f"Lista lavorazioni: {[(w['id'],w['time_machine_needed']) for w in job.list_works]}"
            )
            print(
                f"Cicli di produzione {job.worked_quantity} e prodotti {job.worked_quantity*len(job.list_works)} elementi ({len(job.list_works)} alla volta)"
            )
            print(
                f"Tempo di produzione {job.time_needed()} minuti ({job.time_needed()/DAILY_WORKING_MINUTES} giorni)"
            )
            print("\n")


def write_solution_to_excel(
    schedule: list[Schedule], path_file: str = "Data/schedule.xlsx"
):
    name_machines = [
        f"{s.machine['name']} {s.machine['pallets']} pallets" for s in schedule
    ]
    list_data = [
        [
            {
                "job": i_job,
                "work_in_parallel": len(j.list_works),
                "work_type": w["id"],
                "time_machine_needed": w["time_machine_needed"],
                "quantity_to_produce": j.worked_quantity,
                "total_time_machine_needed": j.time_needed(),
                "days_machine_needed": j.time_needed() / DAILY_WORKING_MINUTES,
            }
            for i_job, j in enumerate(s.list_jobs)
            for w in j.list_works
        ]
        for s in schedule
    ]
    write_data_to_excel(list_data, name_machines, path_file)
