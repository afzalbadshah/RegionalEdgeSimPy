"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
- Represents a moving device (IoT, vehicle, etc.) that can attach to servers
  and perform handovers based on signal strength.
"""

import math
from config.config import MOBILITY_CONFIG


class MobileEntity:
    """
    Represents a mobile node in the simulation.
    It can be placed in 1D (float position) or 2D ([x, y]) space.
    """

    def __init__(self, entity_id, init_pos, speed):
        self.id = entity_id
        self.position = init_pos  # starting position (1D float or 2D list/tuple)
        self.speed = speed        # meters per second
        self.attached_server = None
        self.ho_latency = MOBILITY_CONFIG["handover_latency_ms"]
        self.ho_threshold_db = MOBILITY_CONFIG["handover_threshold_db"]

    def move(self, dt_ms):
        """
        Update position over time interval dt_ms.
        - In 1D: simply shift position by speed * time.
        - In 2D: leave movement to an external mobility model like RandomWaypoint.
        """
        if isinstance(self.position, (int, float)):
            self.position += self.speed * (dt_ms / 1000)
        # If position is a list/tuple, movement is handled externally.

    def signal_strength(self, server):
        """
        Compute a basic signal strength value using a path-loss model.
        - If position is 2D: use Euclidean distance to server.x/server.y.
        - If 1D: use absolute difference to server.location.
        Formula: RSS ≈ -20 * log10(distance)
        """
        # Determine distance
        if isinstance(self.position, (list, tuple)):
            sx = getattr(server, "x", getattr(server, "location", 0))
            sy = getattr(server, "y", 0)
            dx = self.position[0] - sx
            dy = self.position[1] - sy
            dist = math.hypot(dx, dy)
        else:
            dist = abs(self.position - getattr(server, "location", 0))

        # Path-loss model (avoid log10(0) by using max(dist, 1))
        return -20 * math.log10(max(dist, 1))

    def pick_best_bs(self, servers):
        """
        Select the server with the highest signal strength.
        Only switch (handover) if improvement ≥ threshold.
        """
        best_server = max(servers, key=self.signal_strength)
        if (
            self.attached_server is None
            or self.signal_strength(best_server) - self.signal_strength(self.attached_server)
            >= self.ho_threshold_db
        ):
            return best_server
        return self.attached_server

    def handover(self, new_server):
        """
        Attach to a new server and return the handover latency.
        """
        self.attached_server = new_server
        return self.ho_latency
