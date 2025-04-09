import sensor
import time
import math
from machine import PWM, LED

# Control constants for ease of use. will probably remove these later and replace with a mathematical system to get exact values.
SPEED = 1600000
ANGLE = 15
MAX_SIGMA = 375000
OFFCENTER_ANGLE = ANGLE+5
OFFROAD_ANGLE = ANGLE+10
OFFROAD_SPEED = 1565000

last_seen = False # false = left, true = right

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
    sigma = int(theta * 10000)
    if sigma > -50000 and sigma < 50000:
        sigma = 0
    elif sigma < 0:
        sigma += 50000
    elif sigma > 0:
        sigma -= 50000

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
GRAYSCALE_THRESHOLD = [(200, 255)]
ROIS = [  # [ROI, weight]
    (0, 20, 160, 10, 0.7),  # ROI0, top/front
    (0, 80, 160, 10, 0.7)  # ROI1, bottom/back
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
        if angle>45: #ensure that the angle is within the -45 to 45 range
            angle = 45.00000
        elif angle<-45:
            angle = -45.00000



        # deadass idk what this does lol
        # if the front x value is greater than 100 then make a slight right turn?
        # gonna comment it out for now.
        back = x_vals[1]
        front = x_vals[0]
        if back>100 and front>100: # if back > 120, turn left
            angle = (-1*OFFCENTER_ANGLE)
            last_seen = False
        elif back<60 and front < 60: # if back < 40, turn right
            angle = OFFCENTER_ANGLE
            last_seen = True
        # else: angle = 0


        '''
        MAKE ADJUSTMENTS
        '''
        # enable led based on angle and get sigma
        if angle<(-1*ANGLE): # left
            led_off()
            blueled.on()
            last_seen = False
        elif angle>ANGLE: # right
            led_off()
            redled.on()
            last_seen = True
        else: #straight
            led_off()
            greenled.on()

        turn_angle = convert_angle(angle)
        # print(f"angle is {angle}, sigma is {turn_angle}")
        p7.duty_ns(turn_angle)
        p9.duty_ns(SPEED)

    else:
        # print("track not detected, braking")
        if last_seen: # if right
            turn_angle = convert_angle(OFFROAD_ANGLE)
            p7.duty_ns(turn_angle) # turn right
        else:
            turn_angle = convert_angle(-1*OFFROAD_ANGLE)
            p7.duty_ns(turn_angle) # turn left

        p9.duty_ns(OFFROAD_SPEED) # slow down a lot
        led_off()
