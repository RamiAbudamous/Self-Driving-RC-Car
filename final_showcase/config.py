# Control constants for ease of use

# Kill Switch: 1 = kill, 0 = no kill
KILL = 0
# Brake counter: 1 = count, 0 = no count. if counting, will break after 100 frames of no road
COUNT_BRAKES = 0
# Lane Following: 1 = Lane, 0 = Line
FOLLOW_LANE = 1


# speed ranges from 1,650 to 1,562. range of 87.
MAX_SPEED    = 1550 #5975 #1625 #15925
SPEED_SCALAR = 1050  #900 #750 # how much the car should slow down while turning
MIN_SPEED    = 1530 #1562 # also offroad speed for now

# change how strong the turning is
TURN_STRENGTH = 11750 # default 10k feels pretty weak # 11850
# change how large the turn angle is
ANGLE_DIFF_OFFSET = .87
# these effectively do the same thing, but there is some nuance

VELOCITY_CONSTANT_MULT = 31
rotations = 0
velocity = 1
max_velocity = 1

MAX_SIGMA = 400000 #cant fix these because theyre calculated before the ns to us conversion
DEADZONE  = 50000
DEADZONE_ANGLE = 0
STRAIGHT_WIDTH = 5
ANGLE = 5
ANGLE_OFFSET = [0, None, 0] # ANGLE_OFFSET[0] = left offset, ANGLE_OFFSET[2] = right offset
OFFROAD_ANGLE   = ANGLE+25
OFFCENTER_ANGLE = ANGLE+10
OFFCENTER_ZONE = 30

LEFT = True
RIGHT = False

GREY_THRESH = 190
# Camera Constants
GRAYSCALE_THRESHOLD = [(GREY_THRESH, 255)] # 200, 255 initially
ROIS = [  # [ROI, weight], ROI is (left, top, x from left, y from top)
    # 0 to 80 on x axis, 40 to 50 on y axis
    (0, 40, 80, 10, 0.7),  # ROI0, top left/front left

    # 0 to 80 on x axis, 110 to 120 on y axis
    # (0, 110, 80, 10, 0.7),  # ROI1, bottom left/back left

    # 80 to 160 on x axis, 40 to 50 on y axis
    (80, 40, 80, 10, 0.7),  # ROI2, top right/front right

    # 80 to 160 on x axis, 110 to 120 on y axis
    # (80, 110, 80, 10, 0.7)  # ROI3, bottom right/back right
]
