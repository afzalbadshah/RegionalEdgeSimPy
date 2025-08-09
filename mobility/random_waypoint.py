"""
RegionalEdgeSimPy — Educational Release

Author: Dr. Afzal Badshah
Department of Software Engineering, University of Sargodha
Website: https://afzalbadshah.com/index.php/afzal-badshah/
LinkedIn: https://www.linkedin.com/in/afzal-badshah-phd-305b03164/
Discussion Forum: resp.afzalbadshah.com

Notes:
- Functionality preserved; comments kept simple for student readability.
- Implements the Random Waypoint mobility model for 2D movement.
"""

import random
import math


class RandomWaypoint:
    """
    Moves a node in 2D space between random points, pausing between moves.

    Parameters:
        area        : dict with xmin, xmax, ymin, ymax (movement bounds)
        speed_range : (min_speed, max_speed) in meters/second
        pause_range : (min_pause, max_pause) in seconds

    Students:
    - Adjust area, speed_range, or pause_range to change mobility behavior.
    - This is just one model; you can implement your own movement logic here.
    """

    def __init__(self, area, speed_range, pause_range):
        self.area = area
        self.speed_range = speed_range
        self.pause_range = pause_range

        # State: "pause" or "move"
        self.state = "pause"

        # Pick initial random position and target
        self.pos = self._random_point()
        self.target = self._random_point()

        # Initial pause time and speed
        self.pause_time = random.uniform(*pause_range)
        self.speed = 0.0

    def _random_point(self):
        """
        Pick a random point within the defined area.
        """
        return (
            random.uniform(self.area["xmin"], self.area["xmax"]),
            random.uniform(self.area["ymin"], self.area["ymax"]),
        )

    def next_position(self, dt_ms):
        """
        Advance position by dt_ms milliseconds and return new position.
        """
        dt = dt_ms / 1000.0  # convert ms → seconds

        if self.state == "pause":
            # Count down pause time
            self.pause_time -= dt
            if self.pause_time <= 0:
                # Choose new target and start moving
                self.target = self._random_point()
                self.speed = random.uniform(*self.speed_range)
                self.state = "move"

                # Calculate unit velocity components toward target
                dx = self.target[0] - self.pos[0]
                dy = self.target[1] - self.pos[1]
                dist = math.hypot(dx, dy) or 1.0  # avoid divide-by-zero
                self.vel_x = self.speed * dx / dist
                self.vel_y = self.speed * dy / dist

        else:  # state == "move"
            # Move toward target
            self.pos = (
                self.pos[0] + self.vel_x * dt,
                self.pos[1] + self.vel_y * dt,
            )

            # Check if close enough to target to stop
            if math.hypot(self.pos[0] - self.target[0], self.pos[1] - self.target[1]) < 1e-3:
                self.state = "pause"
                self.pause_time = random.uniform(*self.pause_range)

        return self.pos
