from utils.data_types import *


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

    def jobs_used(self):
        return sum([len(s.list_jobs) for s in self.schedule])

    def evaluate(self):
        pass
