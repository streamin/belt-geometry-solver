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

class PulleyObject:
    """
    Represents a pulley in a 2D belt system.

    Torque units must match length and tension units. Example: (mm, N, N*mm) or (in, lb, in*lb)
    Units of belt and pulley objects must be the same.

    Positive torque is in the CW direction.

    direction indicating whether the belt wraps in a clockwise (+1) or counter-clockwise (-1) orientation.
    """

    def __init__(self, radius, x_position, y_position, direction, torque=0):
        # Validate numeric inputs (except direction)
        for name, value in [
            ("radius", radius),
            ("x_position", x_position),
            ("y_position", y_position),
            ("torque", torque)
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number.")

        # Validate radius
        if radius <= 0:
            raise ValueError("Pulley radius must be greater than 0.")

        # Normalize direction
        self.direction = self._parse_direction(direction)

        self.radius = radius
        self.x_position = x_position
        self.y_position = y_position
        self.torque = torque

    def update_position(self, x_position, y_position):
        # Validate numeric inputs (except direction)
        for name, value in [
            ("x_position", x_position),
            ("y_position", y_position)
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number.")

        self.x_position = x_position
        self.y_position = y_position

    def update_torque(self, torque):
        # Validate numeric inputs (except direction)
        if not isinstance(torque, (int, float)):
            raise TypeError("Torque must be a number.")

        self.torque = torque

    def _parse_direction(self, direction):
        # Acceptable forms
        if direction == 1 or direction == "CW":
            return 1
        elif direction == -1 or direction == "CCW":
            return -1
        else:
            raise ValueError("Direction must be 1, -1, 'CW', or 'CCW'.")

    def __repr__(self):
        return (f"PulleyObject(radius={self.radius}, "
                f"x_position={self.x_position}, "
                f"y_position={self.y_position}, "
                f"direction={self.direction}, "
                f"torque={self.torque}")
