"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
- This is the main simulator. Students typically plug their scheduler here.
"""

import time
from collections import defaultdict

from entities.server          import Server
from workload.generator       import WorkloadGenerator
from scheduler.base_scheduler import BaseScheduler
from core.reporter            import task_reporter
from mobility.manager         import MobilityManager
from mobility.mobile_entity   import MobileEntity
from mobility.random_waypoint import RandomWaypoint
from config.config            import SERVER_CONFIG, WORKLOAD, MOBILITY_CONFIG
from config.metrics           import (
    calculate_transmission_delay,
    calculate_propagation_delay,
    calculate_transmission_cost,
    calculate_processing_cost,
    calculate_edge_energy,
    calculate_regional_energy,
    calculate_cloud_energy,
    calculate_cpu_utilization,
    calculate_memory_utilization,
    calculate_storage_utilization,
    calculate_congestion,
)


class Simulator:
    """
    Orchestrates the simulation: builds servers/devices, generates tasks, calls the
    scheduler, applies allocations, and reports metrics.

    How students integrate a scheduler:
    -----------------------------------
    1) Implement your class that inherits BaseScheduler and defines:
         def schedule(self, tasks, servers, current_time): -> list of (task, server)
       - 'tasks' is a list of Task objects to place this round.
       - 'servers' is a list of Server objects (Edge/Regional/Cloud instances).
       - Return a list of (task, chosen_server_object).

    2) In your application/entry file:
         from scheduler.my_scheduler import MyScheduler
         sim = Simulator(scheduler=MyScheduler())
         sim.run()

    3) The simulator will call your schedule() and then:
       - Mark tasks complete,
       - Update server resources,
       - Compute and log per-server metrics.

    Keep your schedule() logic simple first (e.g., pick the least-loaded server), then
    iterate.
    """

    def __init__(self, scheduler: BaseScheduler):
        self.scheduler = scheduler
        self.current_time = 0
        self.servers = []
        self.tasks = []
        self.generator = WorkloadGenerator()
        self._initialize_servers()

        # -------------------------
        # DEVICE ENTITIES SETUP
        # -------------------------
        # Create one MobileEntity per possible device index (up to max_devices).
        device_entities = []
        num_servers = len(self.servers)

        for i in range(WORKLOAD["max_devices"]):
            # Start each device near a server (round-robin assignment to spread them).
            srv = self.servers[i % num_servers]
            init_pos = [srv.x, srv.y]

            # Create the mobile entity and attach to that server.
            ent = MobileEntity(
                entity_id=i,
                init_pos=init_pos,
                speed=MOBILITY_CONFIG.get("default_speed_m_s", 0.0),
            )
            ent.attached_server = srv

            # Give each device a simple Random Waypoint controller.
            ent.mobility = RandomWaypoint(
                MOBILITY_CONFIG["area"],
                MOBILITY_CONFIG["speed_range"],
                MOBILITY_CONFIG["pause_time"],  # or pause_range if that's the field name
            )

            device_entities.append(ent)

        # Hand off servers + devices to the mobility manager.
        self.mobility = MobilityManager(self.servers, device_entities)

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------

    def _initialize_servers(self):
        """
        Build server objects for Edge/Regional/Cloud using SERVER_CONFIG.
        """
        self.servers = []

        for tier, spec in SERVER_CONFIG.items():
            count = spec.get("num_datacenters", 1)
            for i in range(count):
                srv = Server(
                    name=f"{tier}_{i+1}",
                    index=i,
                    cpu_capacity=spec["cpu"],
                    memory_capacity=spec["memory"],
                    storage_capacity=spec["storage"],
                    bandwidth=spec["bandwidth"],
                    latency=spec["latency"],
                    cost=spec["cost"],
                    tx_cost=spec.get("tx_cost", 0.0),
                )
                # Ensure availability starts full.
                srv.available_cpu = srv.cpu_capacity
                srv.available_memory = srv.memory_capacity
                srv.available_storage = srv.storage_capacity
                self.servers.append(srv)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        """
        Run all rounds. Each round:
        1) Update mobility (devices/servers), account handover delay.
        2) Release completed tasks.
        3) Generate new tasks for this round.
        4) Ask the scheduler to assign tasks → (task, server) pairs.
        5) Apply allocations, mark completions, and update resources.
        6) Compute and report metrics per server.
        7) Advance global clock.
        """
        total_rounds = (
            (WORKLOAD["max_devices"] - WORKLOAD["start_devices"]) //
            WORKLOAD["increment"]
        ) + 1

        for round_no in range(1, total_rounds + 1):
            # 1) Mobility update (returns handover count and total extra delay).
            ho_count, ho_delay = self.mobility.update_all()
            self.current_time += ho_delay
            mob_metrics = self.mobility.get_metrics()

            # 2) Release server resources from tasks that finished earlier.
            for srv in self.servers:
                srv.release_completed_tasks(self.current_time)

            # 3) Generate this round's tasks and tag them with a device (entity) id.
            self.tasks = self.generator.generate_tasks(round_no)
            for idx, task in enumerate(self.tasks):
                task.entity_id = idx
            num_devices = len(self.tasks)

            # ------------------------------------------------------------------
            # 4) SCHEDULER INTEGRATION POINT
            # ------------------------------------------------------------------
            # Call the student's scheduler.
            # Expected return: list of (task_object, server_object)
            assignments = self.scheduler.schedule(self.tasks, self.servers, self.current_time)

            initial_count = num_devices
            assigned_count = len(assignments)
            failed_count = initial_count - assigned_count

            # 5) Remove assigned tasks from "pending" list (kept for compatibility).
            self.tasks = [t for t in self.tasks if not t.is_assigned()]

            # 6) Mark tasks as completed and update server resource availability.
            for task, srv in assignments:
                task.complete(
                    start_time=self.current_time,
                    end_time=self.current_time + srv.latency,
                )
                # Deduct resources (bounded at 0 to avoid negative values).
                srv.available_cpu = max(srv.available_cpu - task.cpu_demand, 0)
                srv.available_storage = max(srv.available_storage - task.data_size_kb, 0)
                mem_req = getattr(task, "memory_demand", task.cpu_demand)
                srv.available_memory = max(srv.available_memory - mem_req, 0)

            # 7) Compute & report per-server metrics (includes average signal strength).
            for srv in self.servers:
                # All tasks that were placed on this server this round.
                assigned_here = [t for t, s in assignments if s is srv]
                if not assigned_here:
                    continue

                total_data = sum(t.data_size_kb for t in assigned_here)

                # Accumulators
                tx_delay = 0.0
                prop_delay = 0.0
                tx_cost = 0.0
                proc_cost = 0.0
                energy = 0.0

                # Per-task signal samples
                signals = []

                for t in assigned_here:
                    # Signal from the device (by entity_id) to this server.
                    dev = self.mobility.entities[t.entity_id]
                    sig = dev.signal_strength(srv)
                    signals.append(sig)

                    # Delays
                    tx_delay += calculate_transmission_delay(t.data_size_kb, srv.name)
                    prop_delay += calculate_propagation_delay(srv.name)

                    # Costs
                    tier = srv.name.split("_")[0]
                    tx_cost += calculate_transmission_cost(
                        t.data_size_kb, SERVER_CONFIG[tier]["tx_cost"]
                    )
                    proc_cost += calculate_processing_cost(t.cpu_demand, srv.cost)

                    # Energy by tier
                    if tier == "Edge":
                        energy += calculate_edge_energy(t.data_size_kb)
                    elif tier == "Regional":
                        energy += calculate_regional_energy(t.data_size_kb)
                    else:
                        energy += calculate_cloud_energy(t.data_size_kb)

                # Averages and utilizations
                avg_signal = round(sum(signals) / len(signals), 2) if signals else 0.0

                used_cpu = srv.cpu_capacity - srv.available_cpu
                used_memory = srv.memory_capacity - srv.available_memory
                used_storage = srv.storage_capacity - srv.available_storage

                cpu_util = round(used_cpu / srv.cpu_capacity * 100, 2)
                memory_util = round(used_memory / srv.memory_capacity * 100, 2)
                storage_util = round(used_storage / srv.storage_capacity * 100, 2)
                congestion = calculate_congestion(total_data, srv.bandwidth)

                # Report a single row per server for this round.
                metrics = {
                    "round_no": round_no,
                    "devices": num_devices,
                    "workload": total_data,
                    **mob_metrics,
                    "avg_signal": avg_signal,
                    "cpu_util": cpu_util,
                    "memory_util": memory_util,
                    "storage_util": storage_util,
                    "layer": srv.name,
                    "avg_tx": round(tx_delay / len(assigned_here), 2),
                    "avg_prop": round(prop_delay / len(assigned_here), 2),
                    "tx_cost": round(tx_cost, 2),
                    "proc_cost": round(proc_cost, 2),
                    "energy": round(energy, 4),
                    "congestion": congestion,
                    "flag": assigned_here[0].priority,
                    "failed": failed_count,
                }
                task_reporter.report(metrics)

            # 8) Advance the global clock by one time unit.
            self.current_time += 1
