# Control constants for ease of use

# speed ranges from 1,650 to 1,562. range of 87.
MAX_SPEED    = 1595 #5975 #1625 #15925
SPEED_SCALAR = 800  #900  #750    # how much the car should slow down while turning
MIN_SPEED    = 1562 # also offroad speed for now


TURN_STRENGTH = 11750 # default 10k feels pretty weak # 11850
MAX_SIGMA = 400000 #cant fix these because theyre calculated before the ns to us conversion
DEADZONE  = 50000
DEADZONE_ANGLE = 0
ANGLE = 5
ANGLE_OFFSET = 0
OFFROAD_ANGLE   = ANGLE+20
OFFCENTER_ANGLE = ANGLE+10
OFFCENTER_ZONE = 40


GREY_THRESH = 185

LEFT = True
RIGHT = False