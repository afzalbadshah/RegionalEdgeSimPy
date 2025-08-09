# scheduler/base_scheduler.py

from abc import ABC, abstractmethod

class BaseScheduler(ABC):
    """
    Abstract base class for all scheduling algorithms.
    Every scheduler must implement the `schedule` method.
    """

    @abstractmethod
    def schedule(self, tasks, servers, current_time):
        """
        Assigns tasks to servers based on the implemented algorithm.
        
        Args:
            tasks (list): List of Task objects to be scheduled.
            servers (list): List of Server objects (Edge, Regional, Cloud).
            current_time (float): Current simulation time.
        
        Returns:
            list: List of (task, server) tuples representing assignments.
        """
        pass

    def log_assignment(self, task, server):
        """
        Optional utility method to log or print task assignment.
        """
        #print(f"📦 Assigned Task {task.id} → {server.name}")
