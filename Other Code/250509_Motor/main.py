import sensor
import time
import math
from pyb import Timer, Pin
from machine import LED
import config

# Kill Switch: 1 = kill, 0 = no kill
KILL = 0

last_seen = config.LEFT
brake_counter=100 #start off braked

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
    sigma = int(theta * config.TURN_STRENGTH)
    if sigma > -1*config.DEADZONE and sigma < config.DEADZONE:
        sigma = 0

    # floor and ceiling, and convert from ns to us
    sigma = int(max((-1*config.MAX_SIGMA), min(config.MAX_SIGMA, sigma))/1000)

    # why do we subtract the deadzone amount when we already have a floor/ceiling? commented out.
    # elif sigma < 0:
    #     sigma += DEADZONE
    # elif sigma > 0:
    #     sigma -= DEADZONE

    # print(f"sigma is {sigma}, angle is {sigma+1500}")
    return int((sigma + 1500)*(19200/10000))  # microseconds

def convert_speed(input_speed):
    speed = max(1500, min(config.MAX_SPEED, input_speed)) # clip speed
    return int(speed*(19200/10000)) #scale speed and return

# SERVO - using Timer for P7
servo_timer = Timer(4, freq=100)
servo_ch = servo_timer.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width=1500)
# 1.1 = Left
# 1.5 = Straight
# 1.9 = Right

# MOTOR PWM - using Timer for P9
motor_timer = Timer(4, freq=100)
motor_ch = motor_timer.channel(3, Timer.PWM, pin=Pin("P9"), pulse_width=1500)
# 1.3 = Full speed reverse
# 1.5 = Brake
# 1.65 = Full speed forward

# H-Bridge Direction Control Pins
ina = Pin("P6", Pin.OUT)
inb = Pin("P5", Pin.OUT)

# Camera Constants
GRAYSCALE_THRESHOLD = [(config.GREY_THRESH, 255)] # 200, 255 initially
ROIS = [  # [ROI, weight]
    (0, 40, 160, 10, 0.7),  # ROI0, top/front
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
servo_ch.pulse_width(convert_angle(0))
motor_ch.pulse_width(convert_speed(1500))
# Set direction FORWARD for H-Bridge
ina.high()
inb.low()
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
        brake_counter = 0 # reset brake counter
        print(f"brake counter is {brake_counter}")

        angle = -math.atan((x_vals[0]-x_vals[1])/(y_vals[0]-y_vals[1]))
        angle = math.degrees(angle) * (-1) #convert to degrees and flip because servo seems to be the other way around

        angle += config.ANGLE_OFFSET

        if angle>45: #ensure that the angle is within the -45 to 45 range
            angle = 45.00000
        elif angle<-45:
            angle = -45.00000

        # deadass idk what this does lol
        # if the front x value is greater than 100 then make a slight right turn?
        # gonna comment it out for now.

        back = x_vals[1]
        front = x_vals[0]
        if back>(160-config.OFFCENTER_ZONE) and front>(160-config.OFFCENTER_ZONE): # right of lane so turn left
            # angle = (-1*OFFCENTER_ANGLE)
            angle = (config.OFFCENTER_ANGLE)
            last_seen = config.LEFT
        elif back<config.OFFCENTER_ZONE and front<config.OFFCENTER_ZONE: # left of lane so turn right
            # angle = OFFCENTER_ANGLE
            angle = (-1*config.OFFCENTER_ANGLE)
            last_seen = config.RIGHT
        # # else: angle = 0

        '''
        MAKE ADJUSTMENTS
        '''
        # enable led based on angle and get sigma
        if angle<(-1*config.ANGLE): # left
            led_off()
            blueled.on()
            last_seen = config.LEFT
        elif angle>config.ANGLE: # right
            led_off()
            redled.on()
            last_seen = config.RIGHT
        else: #straight
            led_off()
            greenled.on()

        turn_angle_us = convert_angle(angle)

        # brake if kill
        if KILL==1:
            motor_ch.pulse_width(convert_speed(1500))
        # lower speed if angle is outside the deadzone
        elif abs(angle)>config.DEADZONE_ANGLE:
            speed = max(config.MIN_SPEED, config.MAX_SPEED - int((abs(angle)*config.SPEED_SCALAR)))
        else: speed = config.MAX_SPEED

        motor_ch.pulse_width(convert_speed(speed))
        # print(f"angle is {angle}, sigma is {turn_angle_us}, speed is {speed}")
        servo_ch.pulse_width(turn_angle_us)

    else: # OFFROAD
        led_off()

        print(f"brake counter is {brake_counter}")

        if KILL==1:
            motor_ch.pulse_width(convert_speed(1500))
        elif brake_counter>=100: # if nothing spotted for a while, then brake
            motor_ch.pulse_width(convert_speed(1500))
        else:
            motor_ch.pulse_width(convert_speed(config.MIN_SPEED)) # slow down a lot

        if last_seen==config.RIGHT:
            turn_angle_us = convert_angle(config.OFFROAD_ANGLE)
            servo_ch.pulse_width(turn_angle_us) # turn right
            print(f"offroad right, angle is {config.OFFROAD_ANGLE}, sigma is {turn_angle_us}")
        else: # if LEFT
            turn_angle_us = convert_angle(-1*config.OFFROAD_ANGLE)
            servo_ch.pulse_width(turn_angle_us) # turn left
            print(f"offroad left, angle is {config.OFFROAD_ANGLE}, sigma is {turn_angle_us}")

        brake_counter+=1
