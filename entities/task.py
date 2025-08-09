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

import uuid
from config.config import WORKLOAD


class Task:
    """
    A single workload item produced by an IoT device.
    Holds resource demands, size, priority, status, timing, and basic metrics.
    """

    def __init__(self, cpu_demand, storage_demand, memory_demand,
                 bandwidth, latency, priority=1):
        # Identity
        self.id = str(uuid.uuid4())

        # Resource demands (units are simulator-defined)
        self.cpu_demand = cpu_demand
        self.storage_demand = storage_demand
        self.memory_demand = memory_demand

        # Network characteristics at creation (used by schedulers/metrics)
        self.bandwidth = bandwidth
        self.latency = latency

        # Priority / flag
        self.priority = priority
        self.flag = priority  # kept for backward compatibility

        # Assignment fields
        self.server_assigned = None      # kept for compatibility with older code
        self.assigned_server = None      # current field used by set_server()

        # Data size (central knob from WORKLOAD)
        self.data_size_kb = WORKLOAD["data_per_device_kb"]

        # Execution timeline
        self.execution_start_time = None
        self.execution_end_time = None
        self.status = "created"

        # Basic per-task metrics (filled by simulator/scheduler)
        self.delay = 0.0
        self.cost = 0.0
        self.energy = 0.0

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def set_server(self, server_name):
        """
        Mark this task as scheduled on a server.
        """
        self.assigned_server = server_name
        self.status = "scheduled"

    def is_assigned(self):
        """
        Returns True if legacy field `server_assigned` is set.
        NOTE: Preserved behavior; do not change to check `assigned_server`.
        """
        return self.server_assigned is not None

    def complete(self, start_time, end_time):
        """
        Mark the task as completed and record execution window.
        """
        self.execution_start_time = start_time
        self.execution_end_time = end_time
        self.status = "completed"

    def fail(self):
        """
        Mark the task as failed.
        """
        self.status = "failed"

    def execution_delay(self):
        """
        Duration between start and end times (0 if not both are set).
        """
        if self.execution_start_time is not None and self.execution_end_time is not None:
            return self.execution_end_time - self.execution_start_time
        return 0

    # ------------------------------------------------------------------
    # Serialization / logging
    # ------------------------------------------------------------------

    def to_dict(self):
        """
        Export task fields for logging/reporting.
        """
        return {
            "id": self.id,
            "cpu_demand": self.cpu_demand,
            "storage_demand": self.storage_demand,
            "memory_demand": self.memory_demand,  # included for completeness
            "bandwidth": self.bandwidth,
            "latency": self.latency,
            "priority": self.priority,
            "data_size_kb": self.data_size_kb,
            "server": self.assigned_server,
            "status": self.status,
            "start_time": self.execution_start_time,
            "end_time": self.execution_end_time,
            "delay": self.delay,
            "cost": self.cost,
            "energy": self.energy,
        }

    def __str__(self):
        """
        Human-readable summary (short ID).
        """
        short_id = self.id[:6]
        return (
            f"Task({short_id}) | CPU: {self.cpu_demand} | Storage: {self.storage_demand} | "
            f"Memory: {self.memory_demand} | Data: {self.data_size_kb}KB | "
            f"Priority: {self.priority} | Status: {self.status}"
        )
