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

    # Torque units must match length and force units. Example: mm, N, Nmm
    pulleyA = po.PulleyObject(pulley_teeth_to_radius(19), 0, 0, "CW")
    pulleyB = po.PulleyObject(pulley_teeth_to_radius(36), 440, 0, "CW", 75*1000)
    pulleyC = po.PulleyObject(25, 340, -25, "CCW", 10)
    belt1 = bo.BeltObject(pulleyA, pulleyB, pulleyC, unknown_torque_index=0, tensioner_index=2, tensioner_tension=12)
    belt1.set_force_scale(0.1)
    belt1.set_torque_scale(0.001)
    belt1.draw_belt()
    
    pulley1 = po.PulleyObject(pulley_teeth_to_radius(19), 0, 0, "CW")
    pulley2 = po.PulleyObject(pulley_teeth_to_radius(36), 440, 0, "CCW")
    pulley3 = po.PulleyObject(pulley_teeth_to_radius(18), 440, -440, "CW")
    pulley4 = po.PulleyObject(pulley_teeth_to_radius(11), 0, -440, "CW")
    pulley5 = po.PulleyObject(pulley_teeth_to_radius(18), 220, -220, "CCW")
    pulley6 = po.PulleyObject(pulley_teeth_to_radius(24), 200, 50, "CW")
    pulley7 = po.PulleyObject(pulley_teeth_to_radius(18), 100, -300, "CCW")
    pulley8 = po.PulleyObject(pulley_teeth_to_radius(36), -40, -620, "CW")
    belt2 = bo.BeltObject(pulley1, pulley2, pulley3, pulley4, pulley5, pulley6, pulley7, pulley8, min_tension=100)
    belt2.set_force_scale(1)
    belt2.set_torque_scale(0.01)
    belt2.draw_belt()

    print(f"belt2 Length: {belt2.get_total_length()}")
    print()
    print(f"belt2: Pulley 0 and tangent from pulley 0 to pulley 1: {belt2.get_segment_geometry(0)}")

if __name__ == "__main__":

    main()



