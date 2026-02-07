class PulleyObject:
    """
    Represents a pulley in a 2D belt system.

    Each pulley has:
      - a positive radius,
      - an (x, y) position in Cartesian space,
      - a rotation direction indicating whether the belt contacts it
        in a clockwise (+1) or counter-clockwise (-1) orientation.

    The class validates numeric inputs and normalizes direction values,
    accepting 1, -1, "CW", or "CCW" for convenience.
    """

    def __init__(self, radius, x_position, y_position, direction):
        # Validate numeric inputs (except direction)
        for name, value in [
            ("radius", radius),
            ("x_position", x_position),
            ("y_position", y_position)
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
                f"direction={self.direction})")