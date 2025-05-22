import time, math, sensor
from pyb import Timer, Pin
from machine import LED
import config, steer, motor

class openMV:
    '''VARIABLES'''
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

    # LED Definitions
    redled = LED("LED_RED") # RIGHT
    greenled = LED("LED_GREEN") # STRAIGHT
    blueled = LED("LED_BLUE") # LEFT

    # other variables
    clock = None
    last_seen = config.LEFT
    brake_counter=100 #start off braked
    angle_turn = 0 #start off at no angle

    '''FUNCTIONS'''
    # turn off all LEDs
    def led_off(self):
        self.redled.off()
        self.blueled.off()
        self.greenled.off()

    # set the car up
    def initialize(self):
        # Camera Setup
        sensor.reset()  # Initialize the camera sensor.
        sensor.set_pixformat(sensor.GRAYSCALE)  # use grayscale.
        sensor.set_framesize(sensor.QQVGA)  # use QQVGA for speed.
        sensor.skip_frames(time=2000)  # Let new settings take affect.
        sensor.set_auto_gain(False)  # must be turned off for color tracking
        sensor.set_auto_whitebal(False)  # must be turned off for color tracking
        self.clock = time.clock()  # Tracks FPS.

        # Enable blue LED to show that the system is on
        self.led_off()
        self.blueled.on()
        # STARTUP: In neutral for at least 5 seconds
        self.servo_ch.pulse_width(steer.convert_angle(0))
        self.motor_ch.pulse_width(motor.convert_speed(1500))
        # Set direction FORWARD for H-Bridge
        self.ina.high()
        self.inb.low()
        # wait 5 seconds then turn off LED to show that initialization is over
        time.sleep_ms(5000)
        self.led_off()
    
    # main loop of car
    def tick(self):
        self.clock.tick()  # Track elapsed milliseconds between snapshots().
        img = sensor.snapshot()  # Take a picture and return the image.

        self.blobs(img)

        if self.flags[0] and self.flags[1] and self.flags[2] and self.flags[3]:
            self.brake_counter = 0 # reset brake counter
            
            # takes the blobs and turns them into a proper turn angle
            self.get_turn_angle()

            # executes changes
            steer.turn(self)
            motor.go(self)

        else: # OFFROAD
            self.led_off()
            print(f"brake counter is {self.brake_counter}")
            self.brake_counter+=1

            # executes offroad plan
            steer.offroad(self)
            motor.offroad(self)


    # take the image and find the blobs
    def blobs(self, img):
        # reset values
        self.x_vals = []
        self.y_vals = []
        self.flags = []

        for r in config.ROIS:
            blobs = img.find_blobs(
                config.GRAYSCALE_THRESHOLD,
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

                self.x_vals.append(largest_blob.cx())
                self.y_vals.append(largest_blob.cy())
                self.flags.append(True)
            else: self.flags.append(False)

    def get_turn_angle(self):
        angle_left = self.find_blob_angle(0) # 0 for left
        angle_right = self.find_blob_angle(2) # 2 for right

        # TODO: LOGIC HERE TO CONVERT THE LEFT AND RIGHT ANGLES TO ONE UNIFIED TURN ANGLE

        self.angle_turn = "turn angle goes here" # set the turn angle

    # take the blobs and find the angles
    def find_blob_angle(self, i): # i will be 0 or 2, 0 for left, 2 for right
        angle = -math.atan((self.x_vals[0+i]-self.x_vals[1+i])/(self.y_vals[0+i]-self.y_vals[1+i]))
        angle = math.degrees(angle) * (-1) #convert to degrees and flip because servo seems to be the other way around

        angle += config.ANGLE_OFFSET[i]

        if angle>45: #ensure that the angle is within the -45 to 45 range
            angle = 45.00000
        elif angle<-45:
            angle = -45.00000

        back = self.x_vals[1+i]
        front = self.x_vals[0+i]
        # TODO: this code might be flawed because it runs once for left and once for right. fix that
        if back>(160-config.OFFCENTER_ZONE) and front>(160-config.OFFCENTER_ZONE): # right of lane so turn left
            # angle = (-1*OFFCENTER_ANGLE)
            angle = (config.OFFCENTER_ANGLE)
            self.last_seen = config.LEFT
        elif back<config.OFFCENTER_ZONE and front<config.OFFCENTER_ZONE: # left of lane so turn right
            # angle = OFFCENTER_ANGLE
            angle = (-1*config.OFFCENTER_ANGLE)
            self.last_seen = config.RIGHT
        # # else: angle = 0

        return angle



