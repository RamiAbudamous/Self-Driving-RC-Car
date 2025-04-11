import sensor
import time
import math
from machine import PWM, LED

# Control constants for ease of use
# speed ranges from 1,650,000 to 1,562,500. range of 87500
# could decrease by 1000 per degree
MAX_SPEED    = 1575000
SPEED_SCALAR = 750
MIN_SPEED    = 1562500 # also offroad speed for now

# Kill Switch: 1 = kill, 0 = no kill
KILL = 1

TURN_STRENGTH = 13000 # default 10k feels pretty weak
MAX_SIGMA = 400000
DEADZONE  = 50000
ANGLE = 15
ANGLE_OFFSET = 2.8
OFFROAD_ANGLE   = ANGLE+10
OFFCENTER_ANGLE = ANGLE+5
OFFCENTER_ZONE = 40

LEFT = True
RIGHT = False
last_seen = LEFT

# LED Definitions
redled = LED("LED_RED") # RIGHT
greenled = LED("LED_GREEN") # STRAIGHT
blueled = LED("LED_BLUE") # LEFT
def led_off():
    redled.off()
    blueled.off()
    greenled.off()

def convert_angle(theta):

    # make compatible with PWM
    sigma = int(theta * TURN_STRENGTH)
    if sigma > -1*DEADZONE and sigma < DEADZONE:
        sigma = 0

    # why do we subtract the deadzone amount when we already have a floor/ceiling? commented out.
    # elif sigma < 0:
    #     sigma += DEADZONE
    # elif sigma > 0:
    #     sigma -= DEADZONE

    # floor and ceiling
    if sigma > MAX_SIGMA:
        sigma = MAX_SIGMA
    elif sigma < -1*MAX_SIGMA:
        sigma = -1*MAX_SIGMA

    return int(sigma+1500000)

#SERVO
p7 = PWM("P7", freq=100, duty_u16=32768)
# 1.1 = Left
# 1.5 = Straight
# 1.9 = Right

#MOTOR
p9 = PWM("P9", freq=100, duty_u16=32768)
# 1.3 = Full speed reverse
# 1.5 = Brake
# 1.65 = Full speed forward

# Camera Constants
GRAYSCALE_THRESHOLD = [(200, 255)] # 200, 255 initially
ROIS = [  # [ROI, weight]
    (0, 50, 160, 10, 0.7),  # ROI0, top/front
    (0, 110, 160, 10, 0.7)  # ROI1, bottom/back
]

# Camera Setup
sensor.reset()  # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE)  # use grayscale.
sensor.set_framesize(sensor.QQVGA)  # use QQVGA for speed.
sensor.skip_frames(time=2000)  # Let new settings take affect.
sensor.set_auto_gain(False)  # must be turned off for color tracking
sensor.set_auto_whitebal(False)  # must be turned off for color tracking
clock = time.clock()  # Tracks FPS.

# Enable blue LED to show that the system is on
led_off()
blueled.on()
# STARTUP: In neutral for at least 5 seconds
p7.duty_ns(1500000)
p9.duty_ns(1500000)
time.sleep_ms(5000)
blueled.off()

while True:
    clock.tick()  # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot()  # Take a picture and return the image.

    # unused, remove? commented for now.
    # centroid_sum = 0

    # vals[0] tracks , and vals[1] tracks the
    x_vals = []
    y_vals = []
    flags = []

    for r in ROIS:
        blobs = img.find_blobs(
            GRAYSCALE_THRESHOLD,
            roi=r[0:4],
            merge=True,
            pixels_threshold=5,
            area_threshold=5
        )  # r[0:4] is roi tuple

        if blobs:
            # Find the blob with the most pixels.
            largest_blob = max(blobs, key=lambda b: b.pixels())
            center_blob = min(blobs, key=lambda a: abs(a.cx()-80))
            img.draw_rectangle(center_blob.rect(), color=0)
            img.draw_cross(center_blob.cx(), center_blob.cy(), color=0)

            x_vals.append(largest_blob.cx())
            y_vals.append(largest_blob.cy())
            flags.append(True)
        else: flags.append(False)

    if flags[0]==True and flags[1]==True:
        angle = -math.atan((x_vals[0]-x_vals[1])/(y_vals[0]-y_vals[1]))
        angle = math.degrees(angle) * (-1) #convert to degrees and flip because servo seems to be the other way around

        angle += ANGLE_OFFSET

        if angle>45: #ensure that the angle is within the -45 to 45 range
            angle = 45.00000
        elif angle<-45:
            angle = -45.00000



        # deadass idk what this does lol
        # if the front x value is greater than 100 then make a slight right turn?
        # gonna comment it out for now.

        back = x_vals[1]
        front = x_vals[0]
        if back>(160-OFFCENTER_ZONE) and front>(160-OFFCENTER_ZONE): # right of lane so turn left
            angle = (-1*OFFCENTER_ANGLE)
            last_seen = LEFT
        elif back<OFFCENTER_ZONE and front<OFFCENTER_ZONE: # left of lane so turn right
            angle = OFFCENTER_ANGLE
            last_seen = RIGHT
        # # else: angle = 0


        '''
        MAKE ADJUSTMENTS
        '''
        # enable led based on angle and get sigma
        if angle<(-1*ANGLE): # left
            led_off()
            blueled.on()
            last_seen = LEFT
        elif angle>ANGLE: # right
            led_off()
            redled.on()
            last_seen = RIGHT
        else: #straight
            led_off()
            greenled.on()

        turn_angle = convert_angle(angle)
        speed = MAX_SPEED - int((abs(angle)*SPEED_SCALAR))
        if speed < MIN_SPEED:
            speed = MIN_SPEED
        if KILL==1:
            p9.duty_ns(1500000)
        else:
            p9.duty_ns(speed)
        print(f"angle is {angle}, sigma is {turn_angle}, speed is {speed}")
        p7.duty_ns(turn_angle)

    else:
        # print("track not detected, braking")
        led_off()
        p9.duty_ns(MIN_SPEED) # slow down a lot
        if last_seen==RIGHT:
            turn_angle = convert_angle(OFFROAD_ANGLE)
            p7.duty_ns(turn_angle) # turn right
            print(f"offroad right, angle is {OFFROAD_ANGLE}, sigma is {turn_angle}")
        else: # if LEFT
            turn_angle = convert_angle(-1*OFFROAD_ANGLE)
            p7.duty_ns(turn_angle) # turn left
            print(f"offroad left, angle is {OFFROAD_ANGLE}, sigma is {turn_angle}")
