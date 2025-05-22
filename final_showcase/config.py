# Control constants for ease of use


# Kill Switch: 1 = kill, 0 = no kill
KILL = 0


# speed ranges from 1,650 to 1,562. range of 87.
MAX_SPEED    = 1595 #5975 #1625 #15925
SPEED_SCALAR = 800  #900  #750    # how much the car should slow down while turning
MIN_SPEED    = 1562 # also offroad speed for now


TURN_STRENGTH = 11750 # default 10k feels pretty weak # 11850
MAX_SIGMA = 400000 #cant fix these because theyre calculated before the ns to us conversion
DEADZONE  = 50000
DEADZONE_ANGLE = 0
ANGLE = 5
ANGLE_OFFSET = [0, None, 0] # ANGLE_OFFSET[0] = left offset, ANGLE_OFFSET[2] = right offset
OFFROAD_ANGLE   = ANGLE+20
OFFCENTER_ANGLE = ANGLE+10
OFFCENTER_ZONE = 40


GREY_THRESH = 185

LEFT = True
RIGHT = False

# Camera Constants
GRAYSCALE_THRESHOLD = [(GREY_THRESH, 255)] # 200, 255 initially
ROIS = [  # [ROI, weight], ROI is (left, top, x from left, y from top)
    # 0 to 160 on x axis, 40 to 50 on y axis
    (0, 40, 160, 10, 0.7),  # ROI0, top/front
    # 0 to 160 on x axis, 110 to 120 on y axis
    (0, 110, 160, 10, 0.7)  # ROI1, bottom/back

    # for lanes, we want (0, y, 80, 10, 0.7) and (80, y, 80, 10, 0.7)
    # x0 and x1 are top, then x2 and x3 are bot. same with y0-y3 and flag0-flag3
]