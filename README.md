# RegionalEdgeSimPy

**RegionalEdgeSimPy** is a small teaching-friendly simulator for scheduling IoT/edge workloads across **Edge**, **Regional**, and **Cloud** servers with optional mobility. It is designed so students can easily plug in their **own scheduler** and visualize results.

---

## Author
**Dr. Afzal Badshah**  
Department of Software Engineering, University of Sargodha  
Website: https://afzalbadshah.com/index.php/afzal-badshah/  
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/  
**Discussion Forum:** https://resp.afzalbadshah.com


![RegionalEdgSimPy](https://github.com/user-attachments/assets/e9ee8ae6-3288-46ae-b681-7ef32363a25f)

---

## What’s included (from this simulator)
- Tiered servers (Edge / Regional / Cloud) with capacities, cost, and 2D positions — see `config/config.py`.
- Metrics helpers for cost, delay, energy, and utilization — see `config/metrics.py`.
- Simple mobility (Random Waypoint) for devices and (optionally) servers — see `mobility/`.
- A clear **Simulator** that calls your scheduler each round — see `core/simulator.py`.
- Console + CSV reporting (`results/task_metrics_log.csv`) — see `core/reporter.py`.
- A minimal workload generator that ramps devices each round — see `workload/generator.py`.
- Student-facing guides:
  - **scheduler/index.html** – how to write your own scheduler.
  - **visualization_instructions.html** – how to plot your CSV results.

---

## Quickstart

### 1) Clone
```bash
git clone https://github.com/<your-username>/RegionalEdgeSimPy.git
cd RegionalEdgeSimPy
```

### 2) (Optional) Create a virtual environment
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3) Install requirements
Core simulator uses only the Python standard library. For plotting (optional):
```bash
pip install -r requirements.txt
```

### 4) Run the simulator
```bash
python applications/MainApplication.py
```
This prints a table to the console and appends rows to `results/task_metrics_log.csv`.

> If you see import issues, ensure you run from the project root so `applications/MainApplication.py` can add the root to `sys.path`.

---

## Pick / implement a scheduler

The entry point (`applications/MainApplication.py`) looks like this:
```python
from scheduler.rule_scheduler import RuleBasedScheduler
from scheduler.ppo_me_scheduler import PpoMEScheduler
from core.simulator import Simulator

def main():
    # Choose ONE
    # scheduler = RuleBasedScheduler()
    # scheduler = DQNBasedScheduler()
    scheduler = PpoMEScheduler()  # default in template

    simulator = Simulator(scheduler=scheduler)
    simulator.run()
```

### Write your own
Open **`scheduler/index.html`** in your browser for a short, hands-on guide.  
**Contract:** implement a class inheriting `BaseScheduler` with:
```python
def schedule(self, tasks, servers, current_time) -> list[tuple[Task, Server]]
```
Return a list of `(task, server)` assignments. The simulator:

1. Calls `schedule()` each round.
2. Marks assigned tasks complete and updates server resources.
3. Collects metrics and writes CSV.

> **Tip:** Do not modify server resources inside `schedule()`. Use `srv.can_allocate(...)` to check feasibility, then return the pair. The simulator will apply the changes.

---

## Visualize your results

Open **`visualization_instructions.html`** for ready-to-run examples using **pandas** and **matplotlib**.  
Typical workflow:
1. Run simulator to generate `results/task_metrics_log.csv`.
2. Use the sample scripts in the HTML to plot metrics such as **CPU (%)**, **Energy**, **Avg_Tx(ms)**, etc.

---

## Project structure

```
RegionalEdgeSimPy/
├─ applications/
│  └─ MainApplication.py
├─ config/
│  ├─ config.py
│  └─ metrics.py
├─ core/
│  ├─ simulator.py
│  └─ reporter.py
├─ entities/
│  ├─ server.py
│  └─ task.py
├─ mobility/
│  ├─ manager.py
│  ├─ mobile_entity.py
│  └─ random_waypoint.py
├─ scheduler/
│  ├─ base_scheduler.py
│  └─ index.html              # how to write your scheduler
├─ visualization/
│  └─ visualization_instructions.html
├─ workload/
│  └─ generator.py
├─ results/
│  └─ task_metrics_log.csv    # created at runtime
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## Configuration knobs (where students should look)

- **Workload:** device ramp & data-per-device — `config/config.py` (`WORKLOAD`).
- **Servers:** capacities/positions by tier — `config/config.py` (`SERVER_CONFIG`).
- **Mobility:** area, speed, pauses, handover thresholds — `config/config.py` (`MOBILITY_CONFIG`).
- **Metrics:** cost, delay, energy helpers — `config/metrics.py`.
- **Reporting columns:** add/remove fields — `core/reporter.py` (`TASK_FIELDS`).

---

## Contributing (short version)
1. Fork the repo and create a feature branch: `git checkout -b feature/my-scheduler`  
2. Run simulator + tests, commit your changes.
3. Open a Pull Request with a brief description and sample output/plots.

For help, use the **discussion forum:** https://resp.afzalbadshah.com

---

## Citation
If you use this simulator for research or teaching, please cite:  
**RegionalEdgeSimPy — Educational Release** by Dr. Afzal Badshah, University of Sargodha.
