"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
- Generates tasks for each simulation round based on WORKLOAD settings.
"""

import random
from entities.task import Task
from config.config import WORKLOAD


class WorkloadGenerator:
    """
    Produces synthetic workload (tasks) to simulate IoT devices generating data.

    Students:
    - To change how tasks are generated, modify generate_tasks().
    - You can change demand values (CPU, storage, etc.) to simulate different
      application types or device capabilities.
    """

    def __init__(self):
        # Load central workload parameters from config
        self.start_devices = WORKLOAD["start_devices"]
        self.max_devices = WORKLOAD["max_devices"]
        self.increment = WORKLOAD["increment"]
        self.data_per_device_kb = WORKLOAD["data_per_device_kb"]

    def generate_tasks(self, round_no):
        """
        Generate tasks for the current round.

        Device count grows by 'increment' each round until max_devices.
        Each task gets identical CPU, storage, and memory demands
        (students can randomize or differentiate if needed).
        """
        tasks = []

        # Determine number of devices for this round
        current_devices = self.start_devices + ((round_no - 1) * self.increment)
        if current_devices > self.max_devices:
            current_devices = self.max_devices

        for device_id in range(current_devices):
            cpu_demand = self.data_per_device_kb
            storage_demand = self.data_per_device_kb
            memory_demand = self.data_per_device_kb
            bandwidth = self.data_per_device_kb

            # Assign a random priority (1 = high, 3 = low)
            priority = random.choice([1, 2, 3])

            task = Task(
                cpu_demand=cpu_demand,
                storage_demand=storage_demand,
                memory_demand=memory_demand,
                bandwidth=bandwidth,
                latency=None,  # can be set by scheduler if needed
                priority=priority
            )
            tasks.append(task)

        return tasks

    def reset(self):
        """
        Retained for compatibility (no internal state to reset here).
        """
        pass
