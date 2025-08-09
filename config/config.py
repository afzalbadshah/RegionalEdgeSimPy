"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: https://www.resp.afzalbadshah.com

Notes:
- Functionality preserved; comments added for clarity and extensibility.
- This file provides centralized configuration used across the simulator.
"""

# ---------------------------------------------------------------------------
# Capacity references (for context/documentation only; not enforced in code)
# 1) HPE Edgeline EL8000 Converged Edge System QuickSpecs
# 2) AWS EC2 m5.16xlarge – 64 vCPUs, 256 GiB memory, ~20 Gbps network
# 3) AWS EC2 c5d.24xlarge – 96 vCPUs, 192 GiB memory, ~25 Gbps network
# ---------------------------------------------------------------------------

# SERVER_CONFIG
# -------------
# Centralized resource/cost/position settings for each tier.
# Students: You typically won't change code in schedulers when experimenting
# with capacities—adjusting values here will propagate throughout the sim.
SERVER_CONFIG = {
    "Edge": {
        "num_datacenters": 3,
        "cpu": 280_000,
        "memory": 3000_00,
        "storage": 8_000_00,
        "bandwidth": 164_000,
        "latency": 5,
        "cost": 0.00005,
        "tx_cost": 0.00002,
        "distance": 2_000,
        # Positions are simple 2D coordinates (arbitrary plane) used by mobility/propagation.
        "positions": [
            [100.0, 200.0],   # Edge_1
            [400.0, 800.0],   # Edge_2
            [900.0, 100.0],   # Edge_3
        ],
    },
    "Regional": {
        "num_datacenters": 2,
        "cpu": 6_400_000,
        "memory": 10_240_000,
        "storage": 40_000_000,
        "bandwidth": 800_000,
        "latency": 50,
        "cost": 0.0001,
        "tx_cost": 0.000005,
        "distance": 200_000,
        "positions": [
            [250.0, 250.0],   # Regional_1
            [750.0, 750.0],   # Regional_2
        ],
    },
    "Cloud": {
        "num_datacenters": 1,
        "cpu": 10_080_0000,
        "memory": 8_064_0000,
        "storage": 151_200_0000,
        "bandwidth": 1_050_000,
        "latency": 300,
        "cost": 0.0002,
        "tx_cost": 0.000005,
        "distance": 2_000_000,
        "positions": [
            [500.0, 500.0],   # Cloud_1
        ],
    },
}

# WORKLOAD
# --------
# Controls the synthetic device count ramp and per-device data size.
# Students: To stress-test schedulers, adjust max_devices or data_per_device_kb.
WORKLOAD = {
    "start_devices": 100,
    "max_devices": 6000,
    "increment": 10,
    "data_per_device_kb": 10,  # NOTE: Many metrics scale with this central knob.
    "profile": "default",
}

# SIMULATION
# ----------
# High-level toggles for what to print/log each round.
SIMULATION = {
    "rounds": 1,
    "print_cost": True,
    "print_congestion": True,
    "log_assignments": True,
}

# MOBILITY_CONFIG
# ---------------
# Unified 2D random-walk style mobility for devices (and optionally servers).
# Students: If your scheduler uses proximity/signal strength, mobility matters.
# You can disable mobility entirely or tweak movement/area parameters here.
MOBILITY_CONFIG = {
    "enabled": True,                 # Turn mobility on/off globally
    "apply_to_servers": True,        # Attach mobility to servers as well as devices
    "num_entities": 50,              # Number of moving entities/devices
    "time_step_ms": 100,             # Simulation time step (milliseconds)
    "handover_latency_ms": 20,       # Extra latency when switching serving node
    "handover_threshold_db": 3,      # Signal delta that triggers a handover
    "default_speed_m_s": 15,         # Used if speed_range not applied
    "init_position": [500.0, 500.0], # Default starting point when not randomized
    "area": {                        # Rectangle within which nodes wander
        "xmin": 0.0, "xmax": 1000.0,
        "ymin": 0.0, "ymax": 1000.0,
    },
    "speed_range": (1.0, 5.0),       # meters/sec
    "pause_time": (0.0, 2.0),        # sec between moves
}

# Extension notes for students:
# - You generally won't need to import this module directly in your scheduler.
#   The simulator passes already-instantiated server objects to the scheduler.
# - If you add a new tier (e.g., "MicroEdge"), follow the same structure
#   under SERVER_CONFIG and update any tier-ordering logic in the simulator.
# - Keep numeric literal underscores for readability; values are unchanged.
