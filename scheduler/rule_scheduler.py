from scheduler.base_scheduler import BaseScheduler

class RuleBasedScheduler(BaseScheduler):
    def schedule(self, tasks, servers, current_time):
        results = []

        for task in tasks:
            assigned = False
            server = None

            # --- Check Edge servers ---
            eligible_edge = [
                s for s in servers
                if s.name.startswith("Edge") and s.can_allocate(task.cpu_demand, task.storage_demand, task.memory_demand)
            ]
            if eligible_edge:
                selected = min(eligible_edge, key=lambda s: s.available_cpu + s.available_memory + s.available_storage)
                release_time = current_time + selected.latency
                selected.allocate(task.id, task.cpu_demand, task.storage_demand, task.memory_demand, release_time)
                server = selected
                assigned = True

            # --- Check Regional if not assigned ---
            if not assigned:
                eligible_regional = [
                    s for s in servers
                    if s.name.startswith("Regional") and s.can_allocate(task.cpu_demand, task.storage_demand, task.memory_demand)
                ]
                if eligible_regional:
                    selected = min(eligible_regional, key=lambda s: s.available_cpu + s.available_memory + s.available_storage)
                    release_time = current_time + selected.latency
                    selected.allocate(task.id, task.cpu_demand, task.storage_demand, task.memory_demand, release_time)
                    server = selected
                    assigned = True

            # --- Check Cloud if not assigned ---
            if not assigned:
                eligible_cloud = [
                    s for s in servers
                    if s.name.startswith("Cloud") and s.can_allocate(task.cpu_demand, task.storage_demand, task.memory_demand)
                ]
                if eligible_cloud:
                    selected = min(eligible_cloud, key=lambda s: s.available_cpu + s.available_memory + s.available_storage)
                    release_time = current_time + selected.latency
                    selected.allocate(task.id, task.cpu_demand, task.storage_demand, task.memory_demand, release_time)
                    server = selected
                    assigned = True

            # Log unassigned task
            if not assigned:
                print(f"❌ Task {task.id} could not be assigned due to resource constraints.")

            results.append((task, server))

        return results
