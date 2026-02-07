🟦 Belt Geometry Solver & Visualizer
A Python library for computing and visualizing belt paths across any number of pulleys.
The solver computes center‑to‑center geometry, tangent points, wrap angles, belt length, and produces clear matplotlib diagrams showing arcs and straight belt runs.
This project models both open and crossed belts and supports CW/CCW pulleys in arbitrary 2D layouts.

✨ Features
• Accurate tangent geometry between multiple pulleys
• Supports clockwise (+1) and counter‑clockwise (‑1) pulley directions
• Computes wrap angle and wrap length for each pulley
• Calculates incoming and outgoing belt contact points
• Computes total belt length (arcs + tangent segments)
• Visualizes the belt with color‑coded arcs and straight lines
• Pulleys drawn as filled circles
• Uses bright, fully saturated HSV colors
• Clean object‑oriented design

📦 Installation
pip install matplotlib numpy
Copy BeltObject.py and PullyObject.py into your project directory.

🧱 Basic Usage
• Create pulleys
from pully_object import PullyObject
from belt_object import BeltObject
p1 = PullyObject(radius=20, x_position=0,   y_position=0,   direction="CW")
p2 = PullyObject(radius=40, x_position=150, y_position=50,  direction="CCW")
p3 = PullyObject(radius=30, x_position=80,  y_position=140, direction="CW")
• Build the belt
belt = BeltObject(p1, p2, p3)
• Compute geometry
length = belt.compute()
print("Total belt length:", length)
• Draw the belt
belt.draw_belt()

🧠 How It Works
The solver calculates:
• Center‑to‑center distances and angles
• Tangent geometry using signed pulley radii
• Local and global tangent angles
• Wrap angle based on how the belt enters and exits each pulley
• Exact contact points on each pulley
• Total belt length by summing arc lengths and straight segments
• A complete belt path suitable for plotting or CAD export
All math is designed so:
• Tangent points lie exactly on the pulley circumference
• Wrap angles are always correct for CW/CCW pulleys
• Both open and crossed belt paths work automatically
• Tangent segments meet arcs perfectly
• Zero‑wrap cases behave correctly (straight‑through tangent)

📚 Class Overview
PullyObject
Represents a single pulley with radius, 2D position, and rotation direction.
Accepts directions: 1, -1, "CW", "CCW".
Validates numeric inputs and normalizes direction internally.
BeltObject
Given multiple pulleys, computes tangent lengths, wrap angles, contact points, and total belt length.
Provides helper functions for retrieving geometry and producing color‑coded belt visualizations.

🖼 Preview
<img width="640" height="480" alt="Example" src="https://github.com/user-attachments/assets/d6b42530-930d-4814-9adb-a85a3ca7af6f" />

🛠 Advanced Features
• Evenly spaced vivid HSV colors for arcs and tangents
• Adjustable circle resolution for smooth arcs
• Pulley numbering
• Grid behind graphics
• Robust error handling
• Supports any number of pulleys

🤝 Contributing
Pull requests and suggestions are welcome.
Potential additions: DXF/SVG export, animation mode, tension diagrams, direction arrows, pulley labels, blueprint‑style visuals.

📜 License
Free to do whatever you want with it.
