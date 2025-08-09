"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
- This is the entry point where you pick a scheduler and run the simulator.
"""

import os
import sys

# ---------------------------------------------------------------------
# Import path setup
# ---------------------------------------------------------------------
# Ensure the project root is on sys.path so module imports work when
# running this file directly (python applications/MainApplication.py).
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(ROOT_DIR)

# ---------------------------------------------------------------------
# Choose a scheduler (students: plug yours here)
# ---------------------------------------------------------------------
from scheduler.rule_scheduler import RuleBasedScheduler
from scheduler.ppo_me_scheduler import PpoMEScheduler
# from scheduler.dqn_scheduler import DQNBasedScheduler  # example: if/when available

from core.simulator import Simulator


def main():
    # -----------------------------------------------------------------
    # Scheduler selection
    # -----------------------------------------------------------------
    # Students:
    # 1) Implement your scheduler class in scheduler/ (e.g., my_scheduler.py)
    # 2) Import it above, then instantiate it here.
    # 3) Your scheduler must inherit BaseScheduler and implement:
    #       def schedule(self, tasks, servers, current_time) -> list[(task, server)]
    #
    # Examples (uncomment exactly one):
    # scheduler = RuleBasedScheduler()
    # scheduler = DQNBasedScheduler()
    
    scheduler = PpoMEScheduler()  # default choice in this template

    # Optional training/deploy hooks (keep commented unless your scheduler uses them)
    # scheduler.train_ppo()
    # scheduler.deploy_ppo()

    print(f"Launching RegionalEdgeSimPy with {scheduler.__class__.__name__} ...\n")

    # -----------------------------------------------------------------
    # Create simulator and run all rounds
    # -----------------------------------------------------------------
    simulator = Simulator(scheduler=scheduler)
    simulator.run()


if __name__ == "__main__":
    main()
