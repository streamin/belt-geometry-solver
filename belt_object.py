"""
Copyright (c) 2026 Simon Cooke

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math
import matplotlib.pyplot as plt
import numpy as np
import colorsys
import pulley_object as po

# physical constants
MIN_SPACE = 1.01   # pulley centres must be at least MIN_SPACE*(r1 + r2) apart. MIN_SPACE must be > 1

# drawing constants
CIRCLE_RESOLUTION = 50 # number of straight segments to draw a full circle
LINE_WIDTH = 2 # for plotting the belt

class BeltObject:
    """
    ** Pulley object length units must be the same as belt object length units. **
    ** Pulley object torque units must be in belt object tension units * length units. **

    Computes tangent lengths, wrap angles, static reaction forces, and total belt length
    around any number of pulley objects.
    Pulley objects must have radius, x_position, y_position, direction, torque.
    """

    def __init__(self, *pulleys, unknown_torque_index=0, min_tension=0, tensioner_index=None, tensioner_tension=0):
        # validate number of pulleys
        if len(pulleys) < 2:
            raise ValueError("At least two pulleys are required.")
        self.num = len(pulleys)
        
        # Validate pulley types
        for i in range(self.num):
            self.validate_pulley(i, pulleys[i])
        self.pulleys = list(pulleys) # make a list so it can be modified

        # ----- Validate tension inputs -----
        self.validate_pos_num("Minimum", min_tension)
        self.min_tension = min_tension

        self.validate_pos_num("Tensioner", tensioner_tension)
        self.tensioner_tension = tensioner_tension

        # ----- Validate index inputs -----
        self.__validate_index("unknown_torque", unknown_torque_index)
        self.unknown_torque_index = unknown_torque_index

        if tensioner_index is not None:
            self.__validate_index("tensioner", tensioner_index)
        self.tensioner_index = tensioner_index
        
        # results filled by __compute_geometry()
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
        self.reaction_angle = [None] * self.num
        self.reaction_force = [None] * self.num
        self.local_tension = [None] * self.num

        self.force_scale = 1
        self.torque_scale = 1
        self.recompute_forces = True

        # compute geometry
        self.__compute_geometry()

    # -------------------------------------------------------------
    # Modify Inputs
    # -------------------------------------------------------------
    def change_min_tension(self, min_tension):
        self.validate_pos_num("Minimum tension", min_tension)
        self.min_tension = min_tension

        self.__compute_forces()
    
    def change_tensioner_tension(self, tensioner_tension):
        self.validate_pos_num("Tensioner tension", tensioner_tension)
        self.tensioner_tension = tensioner_tension

        self.__compute_forces()

    def replace_pulley(self, pulley, position):
        self.__validate_index("Pulley", position)
        self.validate_pulley(position, pulley)        
        self.pulleys[position] = pulley

        self.__compute_geometry()

    def set_torque_scale(self, scale):
        self.validate_pos_num("Torque scale", scale)
        self.torque_scale = scale

    def set_force_scale(self, scale):
        self.validate_pos_num("Force scale", scale)
        self.force_scale = scale

    # -------------------------------------------------------------
    # Convenience getters
    # -------------------------------------------------------------
    def get_total_length(self):
        return self.total_length
    
    def get_pulley(self, i):
        return self.pulleys[i]
    
    def get_wrap_length(self, i): # typically used to check minimum tooth engagment
        return self.wrap_length[i]
    
    def get_global_tangent_angle(self, i): # typically used to check minimum position for tensioner pulley
        return self.global_tangent_angle[i]

    def get_all_geometry(self):
        return {
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
    
    def get_segment_geometry(self, i):
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
            "y_out": self.y_out[i],
        }
    
    def get_all_forces(self):
        if self.recompute_forces:
            self.__compute_forces()
        return {
            "reaction_angle": self.reaction_angle,
            "reaction_force": self.reaction_force,
            "local_tension": self.local_tension
        }
    
    def get_segment_forces(self, i):
        if self.recompute_forces:
            self.__compute_forces()
        return {
            "reaction_angle": self.reaction_angle[i],
            "reaction_force": self.reaction_force[i],
            "local_tension": self.local_tension[i]
        }
    
    # -------------------------------------------------------------
    # Draw function
    # -------------------------------------------------------------
    def draw_belt(self, show_pulleys=True, show_labels=True, show_reaction=True, show_torque=True):
        """
        Draws the belt path, pulleys, pulley labels, reaction forces, and pulley torques.
        """
        if self.recompute_forces:
            self.__compute_forces()
        
        n = self.num
        pulleys = self.pulleys

        fig, ax = plt.subplots()
        ax.set_aspect("equal", adjustable="datalim")

        for i in range(n):

            p_i = pulleys[i]

            cx = p_i.x_position
            cy = p_i.y_position
            r  = p_i.radius
            d  = p_i.direction
            t  = p_i.torque

            # --------- 1. Draw torques (optional)
            if show_torque:
                tr = abs(t)*self.torque_scale
                if show_pulleys:
                    tr += r
                
                circ_color = (1, 0.85, 0.85)
                if t >= 0:
                    circ_color = (0.85, 0.85, 1)
                circle = plt.Circle((cx, cy), tr, fill=True, color=circ_color, linewidth=0)
                circle.set_zorder(1)
                ax.add_patch(circle)

            # --------- 2. Draw pulleys (optional)
            if show_pulleys:
                circ_color = colorsys.hsv_to_rgb(0, 0, 0.8)
                circle = plt.Circle((cx, cy), r, fill=True, color=circ_color, linewidth=0)
                circle.set_zorder(2)
                ax.add_patch(circle)

            # --------- 3. Draw arcs (wrap segments)
            theta_in = self.global_tangent_angle[i] + d*(math.pi/2) # angle from the centre of pulley to where the outgoing belt contacts it
            theta_wrap = self.wrap_angle[i] # Will always be positive since it is 0 to 2*Pi

            # build arc
            arc_steps = int(theta_wrap * CIRCLE_RESOLUTION / (2*math.pi)) + 1 # number of straight line segments to draw arc. Adding one for including the endpoint
            arc_t = np.linspace(theta_in, theta_in + d*theta_wrap, arc_steps, endpoint=True) # not using theta_out becasue of angle wrap errors

            x_arc = cx + r * np.cos(arc_t)
            y_arc = cy + r * np.sin(arc_t)

            arc_color = self.__arc_colour(i)
            ax.plot(x_arc, y_arc, color=arc_color, linewidth=LINE_WIDTH, zorder=3)

            # --------- 4. Draw straight tangent segments
            j = (i + 1) % n

            x1, y1 = self.x_out[i], self.y_out[i]
            x2, y2 = self.x_in[j],  self.y_in[j]

            line_color = self.__line_colour(i)
            ax.plot([x1, x2], [y1, y2], color=line_color, linewidth=LINE_WIDTH, zorder=3)

            # --------- 5. Draw reaction (optional)
            if show_reaction:
                f  = self.reaction_force[i]
                a  = self.reaction_angle[i]

                # arrow starts from the radius of the pulley so the arrows appear have the right proportions
                x1 = cx + r*math.cos(a)
                y1 = cy + r*math.sin(a)

                x2 = x1 + self.force_scale * f * math.cos(a)
                y2 = y1 + self.force_scale * f * math.sin(a)

                ax.plot([x1, x2], [y1, y2], color="black", linewidth=LINE_WIDTH, zorder=4)

            # --------- 6. Draw labels (optional)
            if show_labels:
                ax.text(cx, cy, str(i), ha='center', va='center', color="black", zorder=5)

        plt.title("Belt Path Visualization")
        plt.xlabel("X")
        plt.ylabel("Y")
        ax.set_axisbelow(True) # force gridlines below circles
        plt.grid(True, zorder=0)
        plt.show()

    # -------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------
    @staticmethod
    def angle_0_to_2pi(angle: float) -> float:
        """Converts angle to 0 → 2π range."""
        return angle % (2*math.pi)
    
    def __line_colour(self, i):
        hue = (i + 0.5)/self.num
        return colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    
    def __arc_colour(self, i):
        hue = i/self.num
        return colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    
    def __validate_index(self, name, i):
        n = self.num
        if not isinstance(i, int):
            raise TypeError(f"{name} index must be an integer.")
        if i < 0 or i >= n:
            raise IndexError(f"{name} index must be between 0 and {n - 1}, got {i}.")
        
    @staticmethod
    def validate_pos_num(name, num):
        if not isinstance(num, (int, float)):
            raise TypeError(f"{name} must be a number.")
        if num < 0:
            raise ValueError(f"{name} cannot be a negative number.")
    
    @staticmethod
    def validate_pulley(i, pulley):
        if not isinstance(pulley, po.PulleyObject):
            raise TypeError(f"Position {i} is not a valid pulley object")
    
    # -------------------------------------------------------------
    # Compute reaction forces
    # -------------------------------------------------------------
    def __compute_forces(self):
        # must always compute geometry first

        n = self.num
        pulleys = self.pulleys
        ut = self.unknown_torque_index
        ti = self.tensioner_index
        mt = self.min_tension
        tt = self.tensioner_tension

        # ---------- First pass: balance the pulley torques ----------
        sum_of_forces = 0

        for i in range(1, n):
            m = (i + ut) % n # all indecies except the one we are trying to solve for
            sum_of_forces += pulleys[m].direction * pulleys[m].torque / pulleys[m].radius # add up all the forces casued by pulleys with known torques
            
        pulleys[ut].torque = -(pulleys[ut].direction * sum_of_forces * pulleys[ut].radius) # solve for the unknown pulley torque and overwrite the value there

        # ---------- Second pass: calculate the relative tension in each segment ----------
        rel_ten = np.zeros(n)

        for i in range(1, n):
            k = i - 1
            rel_ten[i] = rel_ten[k] - pulleys[i].direction * pulleys[i].torque / pulleys[i].radius
        
        # ---------- Adjust the tensions ----------
        offset = 0

        if ti is None: # if no tensioner index
            offset = mt - np.min(rel_ten)
        
        else: # if there is a tensioner
            offset = tt - rel_ten[ti]
            offset -= pulleys[ti].direction * (pulleys[ti].torque / pulleys[ti].radius) / 2 # so (tension_in + tension_out)/2 = tensioner_tension

        # add in the offset
        rel_ten += offset

        # check for negative tensions
        if np.min(rel_ten) < 0:
            raise ValueError(f"You can't push on a rope. Tension at {np.argmin(rel_ten)} is {np.min(rel_ten)}")
        
        self.local_tension = rel_ten

        # ----------------- Third pass: Reaction forces ----------------
        for i in range(n):
            k = (i - 1) % n

            tangent_in = self.global_tangent_angle[k]
            tangent_out = self.global_tangent_angle[i]
            
            reaction_x = self.local_tension[k]*math.cos(tangent_in) + self.local_tension[i]*math.cos(tangent_out + math.pi)
            reaction_y = self.local_tension[k]*math.sin(tangent_in) + self.local_tension[i]*math.sin(tangent_out + math.pi)

            self.reaction_angle[i] = self.angle_0_to_2pi(math.atan2(reaction_y, reaction_x))
            self.reaction_force[i] = math.hypot(reaction_y, reaction_x)
        
        # ---------- clear flag to recompute forces ----------
        self.recompute_forces = False

    # -------------------------------------------------------------
    # Geometry computation
    # -------------------------------------------------------------
    def __compute_geometry(self):
        """Compute all tangent lengths, wrap angles, and total belt length."""

        n = self.num
        pulleys = self.pulleys

        # ---------- First pass: C2C geometry, tangents ----------
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
                raise ValueError(f"Pulleys {i} and {j} are too close together.")

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

            tangent_in = self.global_tangent_angle[k]
            tangent_out = self.global_tangent_angle[i]

            # ---------------- pulley wrap ----------------
            # k-angle minus i-angle for CW pulleys, opposite for CCW pulleys
            self.wrap_angle[i] = self.angle_0_to_2pi(p_i.direction * (tangent_in - tangent_out))
            self.wrap_length[i] = self.wrap_angle[i] * p_i.radius

            # ---------------- Wrap Contact points ----------------
            cx = p_i.x_position
            cy = p_i.y_position
            r  = p_i.radius
            d  = p_i.direction

            normal_in = tangent_in + d*(math.pi/2) # angle from the centre of pulley to where the incoming belt contacts it
            self.x_in[i]  = cx + r * math.cos(normal_in)
            self.y_in[i]  = cy + r * math.sin(normal_in)

            normal_out = tangent_out + d*(math.pi/2) # angle from the centre of pulley to where the outgoing belt contacts it
            self.x_out[i] = cx + r * math.cos(normal_out)
            self.y_out[i] = cy + r * math.sin(normal_out)

        # ---------- Total belt length ----------
        self.total_length = sum(self.wrap_length) + sum(self.tangent_length)

        # ---------- set flag to recompute forces ----------
        self.recompute_forces = True # Do not do imediatly because user may be itereating through geometry

