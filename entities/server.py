"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
"""

import math
from config.config import WORKLOAD, SERVER_CONFIG, MOBILITY_CONFIG
from mobility.random_waypoint import RandomWaypoint


class Server:
    """
    Represents a computing server (Edge, Regional, or Cloud) in the simulation.
    Each server has:
    - Name and index
    - Resource capacities (CPU, memory, storage, bandwidth)
    - Network cost and latency
    - Physical position (x, y) and optional mobility
    """

    def __init__(self, name, index, cpu_capacity, storage_capacity,
                 memory_capacity, bandwidth, latency, cost, tx_cost=0.0):
        # Basic details
        self.name = name
        self.index = index
        self.cpu_capacity = cpu_capacity
        self.storage_capacity = storage_capacity
        self.memory_capacity = memory_capacity
        self.bandwidth = bandwidth
        self.latency = latency
        self.cost = cost
        self.tx_cost = tx_cost

        # Position setup (from SERVER_CONFIG)
        tier = name.split('_')[0]  # e.g., "Edge_1" → "Edge"
        self.x, self.y = SERVER_CONFIG[tier]["positions"][self.index]
        self.location = self.x  # kept for backward compatibility

        # Mobility (optional)
        if MOBILITY_CONFIG.get("enabled") and MOBILITY_CONFIG.get("apply_to_servers"):
            area = MOBILITY_CONFIG["area"]
            speed_range = MOBILITY_CONFIG["speed_range"]
            pause_time = MOBILITY_CONFIG["pause_time"]

            self.mobility = RandomWaypoint(area, speed_range, pause_time)

            # Start at configured static position
            try:
                self.mobility.pos = (self.x, self.y)
            except AttributeError:
                pass

            # Update to first simulated position
            self.x, self.y = self.mobility.next_position(0.0)
            self.location = self.x
        else:
            self.mobility = None

        # Current available resources
        self.available_cpu = cpu_capacity
        self.available_storage = storage_capacity
        self.available_memory = memory_capacity

        # Task tracking
        self.running_tasks = {}  # {task_id: (cpu, storage, memory, release_time)}
        self.total_data_transferred_kb = 0.0
        self.total_cost = 0.0

    # ------------------------------------------------------------------
    # Resource allocation methods
    # ------------------------------------------------------------------

    def can_allocate(self, cpu_demand, storage_demand, memory_demand=0):
        """
        Check if the server has enough resources to handle a new task.
        """
        return (
            self.available_cpu >= cpu_demand and
            self.available_storage >= storage_demand and
            self.available_memory >= memory_demand
        )

    def allocate(self, task_id, cpu_demand, storage_demand, memory_demand, release_time):
        """
        Allocate resources to a new task if possible.
        Returns True if allocation succeeds, otherwise False.
        """
        if self.can_allocate(cpu_demand, storage_demand, memory_demand):
            # Deduct resources
            self.available_cpu -= cpu_demand
            self.available_storage -= storage_demand
            self.available_memory -= memory_demand

            # Track the task
            self.running_tasks[task_id] = (cpu_demand, storage_demand, memory_demand, release_time)

            # Update transferred data and cost
            data_size_kb = WORKLOAD["data_per_device_kb"]
            self.total_data_transferred_kb += data_size_kb
            self.total_cost += (cpu_demand * self.cost) + (data_size_kb * self.tx_cost)
            return True
        return False

    def release_completed_tasks(self, current_time):
        """
        Free resources from tasks whose release time has passed.
        """
        completed = [tid for tid, (_, _, _, rt) in self.running_tasks.items() if current_time >= rt]
        for tid in completed:
            cpu, storage, memory, _ = self.running_tasks.pop(tid)
            self.available_cpu += cpu
            self.available_storage += storage
            self.available_memory += memory

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def utilization(self):
        """
        Returns CPU, storage, and memory utilization percentages.
        """
        cpu_util = 100 * (1 - self.available_cpu / self.cpu_capacity) if self.cpu_capacity else 0
        storage_util = 100 * (1 - self.available_storage / self.storage_capacity) if self.storage_capacity else 0
        memory_util = 100 * (1 - self.available_memory / self.memory_capacity) if self.memory_capacity else 0
        return round(cpu_util, 2), round(storage_util, 2), round(memory_util, 2)

    def congestion(self):
        """
        Returns congestion percentage based on transferred data and bandwidth.
        """
        return round((self.total_data_transferred_kb / self.bandwidth) * 100, 2)

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __str__(self):
        cpu_u, storage_u, mem_u = self.utilization()
        return (
            f"{self.name} Server | CPU: {cpu_u}% | Memory: {mem_u}% | Storage: {storage_u}% | "
            f"Tasks: {len(self.running_tasks)} | Cost: {round(self.total_cost, 2)} | "
            f"Congestion: {self.congestion()}%"
        )
