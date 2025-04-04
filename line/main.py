import sensor
import time
import math
from machine import PWM, LED

# Control constants for ease of use. will probably remove these later and replace with a mathematical system to get exact values.
SPEED = 1570000
LEFT = 1250000
MIDDLE = 1500000
RIGHT = 1750000
ANGLE = 20
OFFCENTER_ANGLE = ANGLE+5

# LED Definitions
redled = LED("LED_RED") # RIGHT
greenled = LED("LED_GREEN") # STRAIGHT
blueled = LED("LED_BLUE") # LEFT
def led_off():
    redled.off()
    blueled.off()
    greenled.off()

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
    (0, 20, 160, 10, 0.7),  # ROI1, top
    (0, 80, 160, 10, 0.7)  # ROI2, bottom
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
        angle = math.degrees(angle)
        if angle>45: #ensure that the angle is within the -45 to 45 range
            angle = 45.00000
        elif angle<-45:
            angle = -45.00000



        # deadass idk what this does lol
        # if the front x value is greater than 100 then make a slight right turn?
        # gonna comment it out for now.
        front = x_vals[0]
        if front>100:
            angle = (-1*OFFCENTER_ANGLE)
        elif front<60:
            angle = OFFCENTER_ANGLE
        else: angle = 0


        '''
        MAKE ADJUSTMENTS
        '''
        if angle<(-1*ANGLE): # left
            p7.duty_ns(LEFT)
            p9.duty_ns(SPEED)
            led_off()
            blueled.on()
            # print(f"angle is {angle}, turning left, servo: 1100, motor: crawl")
            # print(f"servo: 1100, motor: 1575\n")

        elif angle>ANGLE: # right
            p7.duty_ns(RIGHT)
            p9.duty_ns(SPEED)
            led_off()
            redled.on()
            # print(f"angle is {angle}, turning right, servo: 1900, motor: crawl")
            # print(f"servo: 1900, motor: 1575\n")

        else: #straight
            p7.duty_ns(MIDDLE)
            p9.duty_ns(SPEED)
            led_off()
            greenled.on()
            # print(f"angle is {angle}, no turn, servo: 1500, motor: slow")
            # print(f"servo: 1500, motor: 1650\n")

    else:
        # print("track not detected, braking")
        p7.duty_ns(1500000) # straighten wheels
        p9.duty_ns(1500000) # brake
        led_off()
