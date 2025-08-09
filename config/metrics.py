"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: https://www.resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
"""

import math
import statistics
from config.config import SERVER_CONFIG, WORKLOAD  # WORKLOAD kept for callers that rely on this import side-effect.

# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

def extract_base_layer(layer_name):
    """
    Turn labels like 'Edge_1' into 'Edge' so we can read SERVER_CONFIG.
    If there is no underscore, return the name as-is.
    """
    return layer_name.split("_")[0] if "_" in layer_name else layer_name


# ------------------------------------------------------------------
# Cost Metrics
# ------------------------------------------------------------------

def calculate_transmission_cost(data_kb, tx_rate):
    """
    Cost = data (KB) * rate (per KB)
    """
    cost = data_kb * tx_rate
    return round(cost, 4)


def calculate_processing_cost(cpu_demand, processing_rate):
    """
    Processing cost = cpu_demand * processing_rate
    """
    cost = cpu_demand * processing_rate
    return round(cost, 6)


def calculate_total_cost(data_kb, cpu_demand, tx_rate, proc_rate):
    """
    Total cost = transmission cost + processing cost
    """
    tx_cost = calculate_transmission_cost(data_kb, tx_rate)
    proc_cost = calculate_processing_cost(cpu_demand, proc_rate)
    total = tx_cost + proc_cost
    return round(total, 4)


# ------------------------------------------------------------------
# Delay Metrics
# ------------------------------------------------------------------

def calculate_transmission_delay(data_kb, layer_name):
    """
    Transmission delay in milliseconds.
    Formula:
      seconds = (data_kb * 8) / bandwidth_kbps
      ms      = seconds * 1000
    """
    base = extract_base_layer(layer_name)
    bandwidth_kbps = SERVER_CONFIG[base]["bandwidth"]
    seconds = (data_kb * 8) / bandwidth_kbps
    ms = seconds * 1000
    return ms


def calculate_propagation_delay(layer_name):
    """
    One-way propagation delay in milliseconds using a fixed speed.
    """
    base = extract_base_layer(layer_name)
    distance_m = SERVER_CONFIG[base]["distance"]
    propagation_speed_mps = 2 * 10**8  # meters/second
    ms = (distance_m / propagation_speed_mps) * 1000
    return round(ms, 4)


def calculate_total_delay(data_kb, layer_name):
    """
    Total delay = transmission + propagation (ms)
    """
    tx_delay = calculate_transmission_delay(data_kb, layer_name)
    prop_delay = calculate_propagation_delay(layer_name)
    total = tx_delay + prop_delay
    return round(total, 4)


# ------------------------------------------------------------------
# Energy Metrics
# ------------------------------------------------------------------

def calculate_energy_consumption(data_kb, base_energy_rate, distance_m, minor_distance_rate):
    """
    Simple energy model:
      energy_per_kb = base_energy_rate + distance_m * minor_distance_rate
      total_energy  = data_kb * energy_per_kb
    """
    energy_per_kb = base_energy_rate + (distance_m * minor_distance_rate)
    total = data_kb * energy_per_kb
    return round(total, 6)


def calculate_edge_energy(data_kb):
    distance = SERVER_CONFIG["Edge"]["distance"]
    return calculate_energy_consumption(data_kb, 0.0000015, distance, 0.000000001)


def calculate_regional_energy(data_kb):
    distance = SERVER_CONFIG["Regional"]["distance"]
    return calculate_energy_consumption(data_kb, 0.000003, distance, 0.000000001)


def calculate_cloud_energy(data_kb):
    distance = SERVER_CONFIG["Cloud"]["distance"]
    return calculate_energy_consumption(data_kb, 0.000005, distance, 0.000000001)


# ------------------------------------------------------------------
# Other Metrics
# ------------------------------------------------------------------

def calculate_response_time(latency, processing_time):
    """
    Response time (ms) = latency + processing_time
    """
    total = latency + processing_time
    return round(total, 2)


def calculate_bandwidth_utilization(used_bandwidth_kb, total_bandwidth_kb):
    """
    Utilization (%) = used / total * 100
    """
    if not total_bandwidth_kb:
        return 0.0
    value = (used_bandwidth_kb / total_bandwidth_kb) * 100
    return round(value, 2)


def calculate_task_failure_rate(total_tasks, failed_tasks):
    """
    Failure rate (%) over a period.
    """
    if not total_tasks:
        return 0.0
    value = (failed_tasks / total_tasks) * 100
    return round(value, 2)


# ------------------------------------------------------------------
# Resource Utilization
# ------------------------------------------------------------------

def calculate_cpu_utilization(available_cpu, total_cpu):
    """
    CPU utilization (%) from available vs total.
    """
    value = 100 * (1 - available_cpu / total_cpu)
    return round(value, 2)


def calculate_memory_utilization(available_memory, total_memory):
    """
    Memory utilization (%).
    """
    value = 100 * (1 - available_memory / total_memory)
    return round(value, 2)


def calculate_storage_utilization(available_storage, total_storage):
    """
    Storage utilization (%).
    """
    value = 100 * (1 - available_storage / total_storage)
    return round(value, 2)


def calculate_congestion(total_data_kb, bandwidth_kbps):
    """
    Simple congestion proxy (%).
    """
    value = (total_data_kb / bandwidth_kbps) * 100
    return round(value, 2)


# ------------------------------------------------------------------
# Mobility Metrics (aggregated by the simulator/mobility manager)
# ------------------------------------------------------------------

def calculate_handover_count(metrics):
    return metrics.total_handovers


def calculate_handover_success_ratio(metrics):
    if metrics.handover_attempts == 0:
        return 0.0
    return metrics.total_handovers / metrics.handover_attempts


def calculate_extra_handover_delay(metrics):
    return metrics.total_handover_delay_ms


def calculate_task_delay_increase(baseline_delays, ho_task_delays):
    """
    Mean(ho - base) across paired delays.
    """
    diffs = [ho - base for ho, base in zip(ho_task_delays, baseline_delays)]
    return statistics.mean(diffs) if diffs else 0.0


def calculate_avg_rss(metrics):
    """
    Average RSS; returns -inf if no samples.
    """
    return sum(metrics.rss_samples) / len(metrics.rss_samples) if metrics.rss_samples else -math.inf


def calculate_coverage_outage_time(metrics):
    return metrics.total_outage_time_ms


def calculate_task_drop_rate(metrics):
    if metrics.total_tasks == 0:
        return 0.0
    return metrics.dropped_tasks / metrics.total_tasks


def calculate_throughput_variation(metrics):
    if not metrics.throughputs:
        return 0.0
    return max(metrics.throughputs) - min(metrics.throughputs)
