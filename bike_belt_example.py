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

import os
import platform
import belt_object as bo
import pulley_object as po
import bike_tensioner_config as cfg
import math

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def pulley_teeth_to_radius(i):
    return i*cfg.BELT_PITCH/(2*math.pi)

# -----------------------------
# Main Funtion
# -----------------------------
def main():
    clear_console()

    """
    This example is for a bike belt tensioner that sits down and behind the bottom bracket.
    Units are mm, N, and N*mm
    The bottom bracket is at coordiantes (0,0) and the rear hub is at (-440,0).
    The tensioner pulley (radius 25mm) is on an arm (75mm) that pivots about a point 'HUB' (-50,-55).
    The tensioner creates 12N of tension in the belt (If the the tensioner imparts a torque the tension is the average of the in and out belt tension)
    The pedal torque is 75*1000 N*mm in the clockwise direction.
    """
    # define pulleys
    target_belt_length = cfg.BELT_PITCH * cfg.BELT_TEETH
    front_radius = pulley_teeth_to_radius(cfg.FRONT_TEETH)
    rear_radius = pulley_teeth_to_radius(cfg.REAR_TEETH)

    rear_pulley = po.PulleyObject(rear_radius, -cfg.CHAINSTAY_LENGTH, 0, "CW", -100*1000) # leave torque as zero. Will overwrite in calculation
    front_pulley = po.PulleyObject(front_radius, 0, 0, "CW", cfg.PEDAL_TORQUE)
    tensioner = po.PulleyObject(25, 0, -200, "CCW", 0.1) # 0.1 Nmm resistive torque in CW direction. arbitrary position. will update later
    
    """
    This section calculates the angle of the tensioner arm when the tensioner pulley is tangent with the minimum length belt (when there are only the two pulleys).
    When we iterativle solve the position of the swinging tensioner arm this is the first limit. 
    """
    # get geometry for determining max angle of belt tensioner
    min_belt = bo.BeltObject(rear_pulley, front_pulley)
    front_rear_angle = min_belt.global_tangent_angle[1]
    front_out_x = min_belt.x_out[1]
    front_out_y = min_belt.y_out[1]
    #print(front_rear_angle)
    #print(front_out_x)
    #print(front_out_y)
    #min_belt.draw_belt(show_reaction=False, show_tension=False, show_torque=False)

    # calculate perpendicular distance from belt to tensioner pulley centre
    hub_dx = cfg.HUB_X - front_out_x
    hub_dy = cfg.HUB_Y - front_out_y
    out_to_hub_angle = math.atan2(hub_dy, hub_dx) - front_rear_angle
    out_to_hub_hypot = math.hypot(hub_dx, hub_dy)
    perp_distance = math.sin(out_to_hub_angle)*out_to_hub_hypot # positive when hub is below belt, negative when above
    #print(f"perp_distance: {perp_distance}")

    tensioner_local_max_dy = cfg.TENSIONER_RADIUS - perp_distance
    tensioner_local_max_angle = math.asin(tensioner_local_max_dy/cfg.TENSIONER_ARM)
    tensioner_max_angle = front_rear_angle + tensioner_local_max_angle
    tensioner_max_angle = tensioner_max_angle % (2*math.pi)
    #print(f"tensioner_max_angle: {math.degrees(tensioner_max_angle)}")

    """
    This section calculates the other tensioner arm angle limit (when the tensioner pulley is 1.1*(r_front + r_tensioner) away from front pulley).
    """
    side_a = math.hypot(cfg.HUB_X, cfg.HUB_Y)
    side_b = 1.1*(front_radius + cfg.TENSIONER_RADIUS)
    side_c = cfg.TENSIONER_ARM
    b_cos_theta = (side_a*side_a + side_c*side_c - side_b*side_b) / (2 * side_a * side_c)
    if abs(b_cos_theta) > 1:
        raise ValueError("Can't calculate min tensioner arm angle.")
    front_to_hub_angle = math.atan2(cfg.HUB_Y, cfg.HUB_X)
    tensioner_min_angle = front_to_hub_angle - (math.pi - math.acos(b_cos_theta))
    tensioner_min_angle = tensioner_min_angle % (2*math.pi)
    #print(f"tensioner_min_angle: {math.degrees(tensioner_min_angle)}")

    """
    In this section we create the belt.
    We then iteratively find the tensioner arm angle (between our two limits) that satisfies our length target.
    If the target cannot be reached after a few loop iterations throw an error.
    """
    # create the belt
    belt = bo.BeltObject(rear_pulley, front_pulley, tensioner, unknown_torque_index=0, tensioner_index=2, tension=cfg.TARGET_TENSION)

    # iterative length solver
    count = 0
    belt_delta = 2*cfg.BELT_ACCURACY
    while belt_delta > cfg.BELT_ACCURACY:
        # loop limit
        count += 1
        if count >= cfg.MAX_ITERATIONS:
            if belt_length < target_belt_length:
                raise ValueError("Try a shorter belt length.")
            else:
                raise ValueError("Try a longer belt length.")

        # test the belt angle
        avg_tensioner_angle = (tensioner_min_angle + tensioner_max_angle)/2
        tensioner_x = cfg.HUB_X + cfg.TENSIONER_ARM*math.cos(avg_tensioner_angle)
        tensioner_y = cfg.HUB_Y + cfg.TENSIONER_ARM*math.sin(avg_tensioner_angle)

        tensioner.update_position(tensioner_x, tensioner_y)
        belt.replace_pulley(tensioner, 2)
        belt_length = belt.total_length
        #print(f"belt length: {belt_length}")

        belt_delta = abs(belt_length-target_belt_length)
        #print(f"belt delta: {belt_delta}")

        if belt_length > target_belt_length: # belt is too long, increase tensioner angle
            tensioner_min_angle = avg_tensioner_angle
            #print("too long")
        else: # belt is too short
            tensioner_max_angle = avg_tensioner_angle
            #print("too short")

    # draw the belt
    belt.set_force_scale(0.05)
    belt.set_torque_scale(0.001)
    belt.draw_belt(show_pulleys=True, show_labels=True, show_reaction=True, show_tension=True, show_torque=True)
    
    print(f"Belt length: {belt.total_length} mm")
    print(f"Top tension: {belt.local_tension[0]} N")
    print(f"Rear reaction torque: {belt.unknown_torque} N*mm")

if __name__ == "__main__":
    main()
