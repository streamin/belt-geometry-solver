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
import math

BELT_PITCH = 11

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def pulley_teeth_to_radius(i):
    return i*BELT_PITCH/(2*math.pi)

# -----------------------------
# Main Funtion
# -----------------------------
def main():
    clear_console()
    pulley1 = po.PulleyObject(pulley_teeth_to_radius(19), 0, 0, "CW")
    pulley2 = po.PulleyObject(pulley_teeth_to_radius(36), 440, 0, "CCW")
    pulley3 = po.PulleyObject(pulley_teeth_to_radius(18), 440, -440, "CW")
    pulley4 = po.PulleyObject(pulley_teeth_to_radius(11), 0, -440, "CW")
    pulley5 = po.PulleyObject(pulley_teeth_to_radius(18), 220, -220, "CCW")
    pulley6 = po.PulleyObject(pulley_teeth_to_radius(24), 200, 50, "CW")
    pulley7 = po.PulleyObject(pulley_teeth_to_radius(18), 100, -300, "CCW")
    pulley8 = po.PulleyObject(pulley_teeth_to_radius(36), -40, -620, "CW")
    belt = bo.BeltObject(pulley1, pulley2, pulley3, pulley4, pulley5, pulley6, pulley7, pulley8, unknown_torque_index=0, min_tension=100)
    
    print(f"Belt Length: {belt.get_total_length()}")
    print()
    print(f"Pulley 0 and tangent from pulley 0 to pulley 1: {belt.get_segment_geometry(0)}")

    belt.set_force_scale(1)
    belt.set_torque_scale(0.01)
    belt.draw_belt()

if __name__ == "__main__":

    main()

