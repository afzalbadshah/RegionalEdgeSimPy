"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
- Manages positions of devices/servers, handovers, and mobility-related metrics.
"""

import math
from config.config import MOBILITY_CONFIG
from mobility.mobile_entity import MobileEntity


class MobilityMetrics:
    """
    Container for mobility statistics collected over time.
    """
    def __init__(self):
        self.total_handovers = 0
        self.handover_attempts = 0
        self.total_handover_delay_ms = 0
        self.rss_samples = []
        self.total_outage_time_ms = 0
        self.dropped_tasks = 0
        self.total_tasks = 0
        self.throughputs = []


class MobilityManager:
    """
    Updates positions of servers and devices, applies handover rules,
    and exposes simple aggregate mobility metrics.

    Students:
    - If you want a different mobility model, you can modify how positions
      are updated here (e.g., replace RandomWaypoint at construction time).
    - Handover policy is threshold-based; tweak handover_threshold_db / latency
      in MOBILITY_CONFIG to see different behaviors.
    """

    def __init__(self, servers, devices=None):
        self.servers = servers
        self.entities = devices if devices is not None else []  # list[MobileEntity]
        self.ho_count = 0
        self.ho_delay = 0
        self.time_step_ms = MOBILITY_CONFIG.get("time_step_ms", 100)

    def update_all(self):
        """
        Advance all server and device positions by one time step
        and apply handovers when a better base station is strong enough.

        Returns:
            (handover_count, total_handover_delay_ms)
        """
        # Update server mobility (if enabled per server)
        for srv in self.servers:
            if hasattr(srv, "mobility") and srv.mobility:
                srv.x, srv.y = srv.mobility.next_position(self.time_step_ms)
                srv.location = srv.x  # keep legacy 1D location updated

        # Update device mobility and evaluate handovers
        for ent in self.entities:
            # Move device
            if hasattr(ent, "mobility") and ent.mobility:
                ent.position = ent.mobility.next_position(self.time_step_ms)
            else:
                ent.move(self.time_step_ms)

            # Attach to best server; possibly hand over
            new_bs = ent.pick_best_bs(self.servers)
            if ent.attached_server is None:
                ent.attached_server = new_bs
            elif new_bs != ent.attached_server:
                # Handover only if signal improvement meets threshold
                old_sig = ent.signal_strength(ent.attached_server)
                new_sig = ent.signal_strength(new_bs)
                delta = new_sig - old_sig
                if delta >= MOBILITY_CONFIG.get("handover_threshold_db", 3):
                    ent.attached_server = new_bs
                    self.ho_count += 1
                    self.ho_delay += MOBILITY_CONFIG.get("handover_latency_ms", 20)

        return self.ho_count, self.ho_delay

    def get_metrics(self):
        """
        Compute a simple dispersion metric (average distance from centroid)
        and return it together with current handover counts/delay.

        Returns:
            dict with keys: avg_pos, ho_count, ho_delay
        """
        positions = []
        for ent in self.entities:
            pos = ent.position
            # Normalize to 2D [x, y]
            if isinstance(pos, (list, tuple)):
                positions.append(pos)
            else:
                positions.append([pos, 0.0])

        n = len(positions)
        if n == 0:
            return {"avg_pos": 0.0, "ho_count": self.ho_count, "ho_delay": self.ho_delay}

        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        x_bar = sum(xs) / n
        y_bar = sum(ys) / n

        # Average Euclidean distance from centroid
        avg_disp = sum(math.hypot(x - x_bar, y - y_bar) for x, y in zip(xs, ys)) / n

        return {
            "avg_pos": round(avg_disp, 2),
            "ho_count": self.ho_count,
            "ho_delay": self.ho_delay,
        }
