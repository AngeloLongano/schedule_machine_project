import time
from utils.data_types import *
from copy import deepcopy


class Job:
    def __init__(
        self,
        list_works: list[WorkType],
    ):
        self.list_works = list_works

    def time_per_unit(self) -> int:
        return (
            sum([w["time_machine_needed"] for w in self.list_works])
            + TIME_OPERATOR_FOR_EACH_WORK
        )

    def max_possible_quantity(self, remaining_time: int) -> int:
        # TODO: not considered time_machine_setup
        return remaining_time // self.time_per_unit()

    def confirmed_job(self, worked_quantity: int):
        self.worked_quantity = worked_quantity

    def time_needed(self) -> int:
        # TODO: not considered time_machine_setup
        return self.time_per_unit() * self.worked_quantity


class Schedule:
    def __init__(self, machine: Machine):
        self.machine: Machine = machine
        self.list_jobs = []

    def get_pallets(self):
        return self.machine["pallets"]

    def add_job(self, job: Job):
        self.list_jobs.append(job)

    def remove_job(self, job: Job):
        self.list_jobs.remove(job)

    def calculate_time(self):
        return sum([j.time_needed() for j in self.list_jobs])

    def remaining_time(self):
        return DAILY_WORKING_MINUTES * DAYS - self.calculate_time()


class Inventory:
    def __init__(
        self, work_types: list[WorkType], customer_deadlines: list[CustomerDeadline]
    ):
        self.list_worked_quantities: list[WorkedQuantity] = list(
            map(lambda w: {**w, "worked_quantity": 0}, work_types)
        )
        self.customer_deadlines = customer_deadlines

    def check_inventory(self) -> list[WorkToDo]:
        works_to_do: list[WorkToDo] = []

        for customer_deadline in self.customer_deadlines:
            find_inventory_row = next(
                (
                    i
                    for i in self.list_worked_quantities
                    if i["id"] == customer_deadline["id_work_type"]
                ),
                None,
            )

            if find_inventory_row["worked_quantity"] < customer_deadline["quantity"]:
                works_to_do.append(
                    {
                        "id": customer_deadline["id_work_type"],
                        "quantity_to_work": customer_deadline["quantity"]
                        - find_inventory_row["worked_quantity"],
                    }
                )
        works_to_do = [
            {**work_to_do, "time_machine_needed": work["time_machine_needed"]}
            for work_to_do in works_to_do
            for work in self.list_worked_quantities
            if work["id"] == work_to_do["id"]
        ]
        return works_to_do

    def add_job(self, job: Job):
        for w in job.list_works:
            find_inventory_row = next(
                (i for i in self.list_worked_quantities if i["id"] == w["id"]),
                None,
            )
            find_inventory_row["worked_quantity"] += job.worked_quantity

    def remove_job(self, job: Job):
        for w in job.list_works:
            find_inventory_row = next(
                (
                    i
                    for i in self.list_worked_quantities
                    if i["id_work_type"] == w["id"]
                ),
                None,
            )
            find_inventory_row["worked_quantity"] -= job.worked_quantity


# chooser jobs
def create_job_to_finish_different_works(
    works_to_do: list[WorkToDo], schedule: list[Schedule]
) -> Job:
    # Choose machine
    schedule_machine = max(
        schedule, key=lambda x: (x.remaining_time(), x.get_pallets())
    )

    # Choose works
    works_to_do.sort(key=lambda x: x["quantity_to_work"], reverse=True)
    works_chooses = works_to_do[: schedule_machine.get_pallets()]

    clean_list_works: list[WorkType] = [
        {"id": w["id"], "time_machine_needed": w["time_machine_needed"]}
        for w in works_chooses
    ]
    # Simulate job
    job = Job(clean_list_works)
    max_production = min(
        (
            job.max_possible_quantity(schedule_machine.remaining_time()),
            min([w["quantity_to_work"] for w in works_chooses]),
        )
    )
    if max_production == 0:
        return None

    # Confirm job and machine
    job.confirmed_job(max_production)
    schedule_machine.add_job(job)

    return job


def create_job_to_finish_work(
    works_to_do: list[WorkToDo], schedule: list[Schedule]
) -> Job:
    # Choose works
    work_choose = max(works_to_do, key=lambda x: x["quantity_to_work"])

    # Choose machine
    schedule_machine = max(
        schedule,
        key=lambda x: (
            x.remaining_time(),
            x.get_pallets(),
        ),
    )
    clean_list_work: list[WorkType] = [
        {
            "id": work_choose["id"],
            "time_machine_needed": work_choose["time_machine_needed"],
        }
        for _ in range(schedule_machine.get_pallets())
    ]
    # Simulate job
    job = Job(clean_list_work)
    max_production = min(
        (
            job.max_possible_quantity(schedule_machine.remaining_time()),
            work_choose["quantity_to_work"] // schedule_machine.get_pallets(),
        )
    )
    if max_production == 0:
        return None

    # Confirm job and machine
    job.confirmed_job(max_production)
    schedule_machine.add_job(job)

    return job


def insert_move(solution: "Solution") -> "Solution":
    solution.schedule.sort(key=lambda x: x.remaining_time(), reverse=True)
    [
        schedule.list_jobs.sort(key=lambda j: j.time_needed())
        for schedule in solution.schedule
    ]
    modified_solution = deepcopy(solution)
    for i_s, schedule in enumerate(solution.schedule):
        for i_job in range(len(schedule.list_jobs)):
            for i_other_s in range(len(solution.schedule)):
                if i_s != i_other_s:
                    is_inserted = modified_solution.insert_job(i_s, i_job, i_other_s)

                    if is_inserted and modified_solution.is_better_solution_than(
                        solution
                    ):
                        return modified_solution
                    else:
                        modified_solution = deepcopy(solution)


def swap_move(solution: "Solution") -> "Solution":
    solution.schedule.sort(key=lambda x: x.remaining_time(), reverse=True)
    [
        schedule.list_jobs.sort(key=lambda j: j.time_needed())
        for schedule in solution.schedule
    ]
    modified_solution = deepcopy(solution)
    for i_s_A, schedule in enumerate(solution.schedule):
        for i_job_A_to_B in range(len(schedule.list_jobs)):
            for i_s_B in range(len(solution.schedule)):
                for i_job_B_to_A in range(len(solution.schedule[i_s_B].list_jobs)):
                    if i_s_A != i_s_B and i_job_A_to_B != i_job_B_to_A:
                        is_swapped = modified_solution.swap_job(
                            i_s_A,
                            i_job_A_to_B,
                            i_s_B,
                            i_job_B_to_A,
                        )

                        if is_swapped and modified_solution.is_better_solution_than(
                            solution
                        ):
                            return modified_solution
                        else:
                            modified_solution = deepcopy(solution)


def local_search(
    start_solution,
    create_job_function: callable = create_job_to_finish_different_works,
    neighbor_function: callable = insert_move,
    stop_time_condition: int = 10000,
):
    start_solution.constructive_solution(create_job_function)
    other_solution = deepcopy(start_solution)
    start_time = time.time()
    other_solution = deepcopy(neighbor_function(other_solution))

    while (
        other_solution is not None
        and not start_solution.is_better_solution_than(other_solution)
        and time.time() - start_time < stop_time_condition
    ):
        start_solution = deepcopy(other_solution)
        other_solution = deepcopy(neighbor_function(other_solution))
    return start_solution


class Solution:
    def __init__(
        self,
        machines: list[Machine],
        work_types: list[WorkType],
        customer_deadlines: list[CustomerDeadline],
    ):
        self.schedule: list[Schedule] = list(map(lambda m: Schedule(m), machines))
        self.inventory = Inventory(work_types, customer_deadlines)
        self.status = "not evaluated"

    def constructive_solution(self, create_job_function: callable):
        works_to_do = self.inventory.check_inventory()
        while len(works_to_do) > 0:
            job = create_job_function(works_to_do, self.schedule)
            if job is None:
                self.status = "not constructable"
                break
            self.inventory.add_job(job)
            works_to_do = self.inventory.check_inventory()

        self.status = "constructed"

    def standard_order(self):
        self.schedule.sort(key=lambda x: x.machine["name"])
        [
            schedule.list_jobs.sort(key=lambda j: j.time_needed(), reverse=True)
            for schedule in self.schedule
        ]

    def can_insert_job(
        self, schedule_from_index: int, job_index: int, schedule_to_index
    ):
        schedule_from = self.schedule[schedule_from_index]
        job = schedule_from.list_jobs[job_index]
        schedule_to = self.schedule[schedule_to_index]
        if (
            schedule_to.get_pallets() >= schedule_from.get_pallets()
            and schedule_to.remaining_time() >= job.time_needed()
        ):
            return True
        return False

    def insert_job(self, schedule_from_index: int, job_index: int, schedule_to_index):
        if self.can_insert_job(schedule_from_index, job_index, schedule_to_index):
            job = self.schedule[schedule_from_index].list_jobs[job_index]
            self.schedule[schedule_from_index].remove_job(job)
            self.schedule[schedule_to_index].add_job(job)
            return True
        return False

    def swap_job(
        self,
        schedule_A_index: int,
        job_A_to_B_index: int,
        schedule_B_index,
        job_B_to_A_index,
    ):
        if self.can_insert_job(
            schedule_A_index, job_A_to_B_index, schedule_B_index
        ) and self.can_insert_job(schedule_B_index, job_B_to_A_index, schedule_A_index):
            self.insert_job(schedule_A_index, job_A_to_B_index, schedule_B_index)
            self.insert_job(schedule_B_index, job_B_to_A_index, schedule_A_index)
            return True
        return False

    def jobs_used(self):
        return sum([len(s.list_jobs) for s in self.schedule])

    def remaining_time(self):
        return sum([s.remaining_time() for s in self.schedule])

    def max_remaining_time(self):
        return max([s.remaining_time() for s in self.schedule])

    def is_better_solution_than(self, other_solution: "Solution"):
        return (
            self.jobs_used() < other_solution.jobs_used()
            or (
                self.jobs_used() == other_solution.jobs_used()
                and self.remaining_time() < other_solution.remaining_time()
            )
            or (
                self.jobs_used() == other_solution.jobs_used()
                and self.remaining_time() == other_solution.remaining_time()
                and self.max_remaining_time() > other_solution.max_remaining_time()
            )
        )
