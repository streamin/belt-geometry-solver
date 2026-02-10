# config file

# Pulley and belt constants
BELT_PITCH       = 11    # mm
BELT_TEETH       = 111
FRONT_TEETH      = 36
REAR_TEETH       = 21

# geometry
CHAINSTAY_LENGTH = 440   # mm
TENSIONER_RADIUS = 25    # mm
TENSIONER_ARM    = 75    # mm
HUB_X            = -50   # mm. The distance from the front pulley up to the spring hub.
HUB_Y            = -55   # mm. The distance from the front pulley forward to the spring hub.

# limits for calculating max belt length
BELT_ACCURACY   = 0.1  # mm. The length accuracy in the iterative max length calculator.
MAX_ITERATIONS  = 20    # count. The max number of loops in the iterative max length calculator.

# forces
# Torque units must match length and tension units. Example: (mm, N, N*mm) or (in, lb, in*lb)
TARGET_TENSION  = 12      # N. The target tesnion in the belt
PEDAL_TORQUE    = 75*1000 # Nmm in CW direction