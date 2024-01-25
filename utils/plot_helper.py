import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from utils.data_types import *
from utils.data_helper import *
from utils.algorithms import *


def draw_gantt_chart(
    solution: Solution,
    name: str = "Schedule",
    is_label_work_type: bool = False,
    is_label_time: bool = False,
    is_label_days: bool = False,
    is_label_quantity: bool = False,
    is_label_job: bool = False,
    is_color_by_jobs: bool = False,
    is_grid_axis_x: bool = False,
    step_days: int = 2,
):
    schedule: list[Schedule] = solution.schedule
    work_types: list[WorkType] = get_data_from_excel("work types")
    num_jobs = solution.jobs_used()

    total_pallets = sum(
        [schedule_machine.machine["pallets"] for schedule_machine in schedule]
    )
    total_time = DAILY_WORKING_MINUTES * DAYS

    generate_colors = [
        {"id": w["id"], "color": list(mcolors.TABLEAU_COLORS)[i]}
        for i, w in enumerate(work_types)
    ]

    height_bar = 10
    padding_bar = 4

    padding_label_pallet_start = padding_bar + height_bar / 2
    step_pos_y = height_bar + padding_bar

    bars_step = np.arange(
        padding_bar,
        step_pos_y * (total_pallets) + padding_bar,
        step_pos_y,
    )

    labels_pallets_step = np.arange(
        padding_label_pallet_start,
        step_pos_y * (total_pallets) + padding_label_pallet_start,
        step_pos_y,
    )

    labels_pallets = [
        f"{schedule_machine.machine['name']} [{i_pallet+1}]"
        for schedule_machine in schedule
        for i_pallet in range(schedule_machine.machine["pallets"])
    ]

    labels_day_step = np.arange(
        0, total_time + DAILY_WORKING_MINUTES, DAILY_WORKING_MINUTES * step_days
    )
    labels_day = [f"day {i}" for i in range(0, DAYS + 1, step_days)]

    fig, ax = plt.subplots(layout="constrained")
    ax.set_title(name)

    index_slot = 0
    count_job = 0
    for i_schedule, schedule_machine in enumerate(schedule):
        for i_pallet in range(schedule_machine.machine["pallets"]):
            for i_job, job in enumerate(schedule_machine.list_jobs):
                if i_job == 0:
                    start_time = 0

                size = job.time_needed()
                if i_pallet < len(job.list_works):
                    ax.broken_barh(
                        [
                            (start_time, size),
                        ],
                        (bars_step[index_slot], height_bar),
                        facecolor=(
                            list(mcolors.TABLEAU_COLORS)[i_schedule + i_job]
                            if is_color_by_jobs
                            else next(
                                color["color"]
                                for color in generate_colors
                                if color["id"] == job.list_works[i_pallet]["id"]
                            )
                        ),
                        label=job.list_works[i_pallet]["id"],
                    )
                    if is_label_work_type:
                        ax.annotate(
                            job.list_works[i_pallet]["id"],
                            (start_time, labels_pallets_step[index_slot]),
                        )
                    if is_label_job:
                        ax.annotate(
                            f"J{i_job}",
                            (start_time, labels_pallets_step[index_slot]),
                        )
                    if is_label_time:
                        ax.annotate(
                            f"{job.time_needed()} min",
                            (start_time + size, labels_pallets_step[index_slot]),
                        )
                    if is_label_days:
                        ax.annotate(
                            f"{job.time_needed() // DAILY_WORKING_MINUTES} days",
                            (start_time + size, labels_pallets_step[index_slot]),
                        )
                    if is_label_quantity:
                        ax.annotate(
                            job.worked_quantity,
                            (start_time + size, labels_pallets_step[index_slot]),
                        )

                start_time += size
            index_slot += 1

    # Set the y-axis limits and tick labels
    ax.set_ylim(0, total_pallets * step_pos_y + padding_bar)
    ax.set_xlim(0, total_time)

    ax.set_yticks(labels_pallets_step)
    ax.set_yticklabels(labels_pallets)
    # Set x-axis label

    ax.set_xticks(labels_day_step)
    ax.set_xticklabels(labels_day)

    # Make grid lines visible
    if is_grid_axis_x:
        ax.grid(axis="x")

    # Display the Gantt chart
    plt.show()
