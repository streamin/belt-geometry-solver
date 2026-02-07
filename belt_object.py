import math
import matplotlib.pyplot as plt
import numpy as np
import colorsys

MIN_SPACE = 1.01   # pulleys must be at least this * (r1 + r2) apart. This number must be > 1
CIRCLE_RESOLUTION = 40 # number of straight segments to draw a full circle
LINE_WIDTH = 2 # for plotting the belt
CIRCLE_VALUE = 0.8 # 0 is black, 1 is white

class BeltObject:
    """
    Computes tangent lengths, wrap angles, and total belt length
    around any number of pulley objects.
    Pulley objects must have radius, x_position, y_position, direction.
    """

    def __init__(self, *pulleys):
        if len(pulleys) < 2:
            raise ValueError("At least two pulleys are required.")
        self.pulleys = pulleys
        self.num = len(pulleys)

        # geometry results (filled by compute())
        self.total_length = None
        self.C2C_angle = [None] * self.num
        self.C2C_length = [None] * self.num
        self.tangent_length = [None] * self.num
        self.local_tangent_angle = [None] * self.num
        self.global_tangent_angle = [None] * self.num
        self.wrap_angle = [None] * self.num
        self.wrap_length = [None] * self.num
        self.x_in = [None] * self.num
        self.y_in = [None] * self.num
        self.x_out = [None] * self.num
        self.y_out = [None] * self.num

    # -------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------
    @staticmethod
    def angle_0_to_2pi(angle: float) -> float:
        """Converts angle to 0 → 2π range."""
        return angle % (2*math.pi)
    
    @staticmethod
    def line_colour(i, n):
        hue = (i + 0.5)/n
        return colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    
    @staticmethod
    def arc_colour(i, n):
        hue = i/n
        return colorsys.hsv_to_rgb(hue, 1.0, 1.0)

    # -------------------------------------------------------------
    # Main computation
    # -------------------------------------------------------------
    def compute(self):
        """Compute all tangent lengths, wrap angles, and total belt length."""
        n = self.num
        pulleys = self.pulleys

        # ---------- First pass: C2C geometry + tangents ----------
        for i in range(n):
            j = (i + 1) % n

            p_i = pulleys[i]
            p_j = pulleys[j]

            dx = p_j.x_position - p_i.x_position
            dy = p_j.y_position - p_i.y_position

            r1 = p_i.radius
            r2 = p_j.radius

            d1 = p_i.direction
            d2 = p_j.direction

            # Center-to-center distance from pulley i to j
            centre_delta = math.hypot(dx, dy)
            self.C2C_length[i] = centre_delta

            # Minimum spacing check
            min_space = (r1 + r2) * MIN_SPACE
            if centre_delta < min_space:
                raise ValueError(f"Pulleys {i+1} and {j+1} are too close together.")

            # Angle from pulley i to j
            self.C2C_angle[i] = self.angle_0_to_2pi(math.atan2(dy, dx))

            # Tangent length from pulley i to j
            radius_delta = (r2 * d2) - (r1 * d1) # Absolute value guaranteed to be less than centre_delta because MIN_SPACE > 1
            self.tangent_length[i] = math.sqrt(centre_delta*centre_delta - radius_delta*radius_delta)

            # Local tangent angle from pulley i to j
            self.local_tangent_angle[i] = math.asin(radius_delta / centre_delta)

            # Global tangent angle from pulley i to j
            self.global_tangent_angle[i] = self.angle_0_to_2pi(self.local_tangent_angle[i] + self.C2C_angle[i])

        # ---------- Second pass: wrap angles, contact points ----------
        for i in range(n):
            k = (i - 1) % n

            p_i = pulleys[i]

            # k-angle minus i-angle for CW pulleys, opposite for CCW pulleys
            self.wrap_angle[i] = self.angle_0_to_2pi(p_i.direction * (self.global_tangent_angle[k] - self.global_tangent_angle[i]))

            self.wrap_length[i] = self.wrap_angle[i] * p_i.radius

            # ---------------- Contact points ----------------
            cx = p_i.x_position
            cy = p_i.y_position
            r  = p_i.radius
            d  = p_i.direction

            theta_in = self.global_tangent_angle[k] + d*(math.pi/2) # angle from the centre of pulley to where the incoming belt contacts it
            self.x_in[i]  = cx + r * math.cos(theta_in)
            self.y_in[i]  = cy + r * math.sin(theta_in)

            theta_out = self.global_tangent_angle[i] + d*(math.pi/2) # angle from the centre of pulley to where the outgoing belt contacts it
            self.x_out[i] = cx + r * math.cos(theta_out)
            self.y_out[i] = cy + r * math.sin(theta_out)

        # ---------- Total belt length ----------
        self.total_length = sum(self.wrap_length) + sum(self.tangent_length)

        return self.total_length

    # -------------------------------------------------------------
    # Convenience getters
    # -------------------------------------------------------------
    def get_total_length(self):
        if self.total_length is None:
            self.compute()
        return self.total_length

    def get_segments(self):
        if self.total_length is None:
            self.compute()
        return {
            "total_length": self.total_length,
            "C2C_angle": self.C2C_angle,
            "C2C_length": self.C2C_length,
            "tangent_length": self.tangent_length,
            "local_tangent_angle": self.local_tangent_angle,
            "global_tangent_angle": self.global_tangent_angle,
            "wrap_angle": self.wrap_angle,
            "wrap_length": self.wrap_length,
            "x_in": self.x_in,
            "y_in": self.y_in,
            "x_out": self.x_out,
            "y_out": self.y_out
        }
    
    def get_segment(self, i):
        if self.total_length is None:
            self.compute()
        return {
            "C2C_angle": self.C2C_angle[i],
            "C2C_length": self.C2C_length[i],
            "tangent_length": self.tangent_length[i],
            "local_tangent_angle": self.local_tangent_angle[i],
            "global_tangent_angle": self.global_tangent_angle[i],
            "wrap_angle": self.wrap_angle[i],
            "wrap_length": self.wrap_length[i],
            "x_in": self.x_in[i],
            "y_in": self.y_in[i],
            "x_out": self.x_out[i],
            "y_out": self.y_out[i]
        }

    def draw_belt(self, show_pulleys=True):
        """
        Draws the belt path: each arc and tangent segment in a different color.
        Requires compute() to have been run.
        """

        if self.total_length is None:
            self.compute()

        n = self.num
        pulleys = self.pulleys

        fig, ax = plt.subplots()
        ax.set_aspect("equal", adjustable="datalim")

        # --------------------------------------------
        # 1. Draw pulleys (optional)
        # --------------------------------------------
        if show_pulleys:
            for i in range(n):

                p_i = pulleys[i]

                cx = p_i.x_position
                cy = p_i.y_position
                r  = p_i.radius
                
                circ_color = colorsys.hsv_to_rgb(0, 0, CIRCLE_VALUE)
                circle = plt.Circle((cx, cy), r, fill=True, color=circ_color, linewidth=0)
                circle.set_zorder(1)
                ax.add_patch(circle)
                ax.text(cx, cy, str(i+1), ha='center', va='center', color="black", zorder=3)

        # --------------------------------------------
        # 2. Draw arcs (wrap segments)
        # --------------------------------------------
        for i in range(n):
            p_i = pulleys[i]

            cx = p_i.x_position
            cy = p_i.y_position
            r  = p_i.radius
            d  = p_i.direction

            theta_in = self.global_tangent_angle[i] + d*(math.pi/2) # angle from the centre of pulley to where the outgoing belt contacts it
            theta_wrap = self.wrap_angle[i] # Will always be positive since it is 0 to 2*Pi

            # build arc
            arc_steps = int(theta_wrap * CIRCLE_RESOLUTION / (2*math.pi)) + 1 # number of straight line segments to draw arc. Adding one for including the endpoint
            arc_t = np.linspace(theta_in, theta_in + d*theta_wrap, arc_steps, endpoint=True) # not using theta_out becasue of angle wrap errors

            x_arc = cx + r * np.cos(arc_t)
            y_arc = cy + r * np.sin(arc_t)

            rand_color = self.arc_colour(i, n)
            ax.plot(x_arc, y_arc, color=rand_color, linewidth=LINE_WIDTH, zorder=2)

        # --------------------------------------------
        # 3. Draw straight tangent segments
        # --------------------------------------------
        for i in range(n):
            j = (i + 1) % n

            x1, y1 = self.x_out[i], self.y_out[i]
            x2, y2 = self.x_in[j],  self.y_in[j]

            rand_color = rand_color = self.line_colour(i, n)
            ax.plot([x1, x2], [y1, y2], color=rand_color, linewidth=LINE_WIDTH, zorder=2)

        plt.title("Belt Path Visualization")
        plt.xlabel("X")
        plt.ylabel("Y")
        ax.set_axisbelow(True) # force gridlines below circles
        plt.grid(True, zorder=0)
        plt.show()