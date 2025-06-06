import time, sensor
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
    # img = None
    x_vals = []
    last_seen = config.LEFT
    brake_counter=100 #start off braked
    angle_turn = 0.0 #start off at no angle

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
        self.motor_ch.pulse_width(motor.convert_speed(0))
        # wait 5 seconds then turn off LED to show that initialization is over
        time.sleep_ms(10000)
        # Set direction FORWARD for H-Bridge
        self.ina.low()
        self.inb.high()
        self.led_off()

    # main loop of car
    def tick(self):
        self.clock.tick()  # Track elapsed milliseconds between snapshots().
        self.img = sensor.snapshot()  # Take a picture and return the image.

        self.find_blobs()

        if self.flags[0] and self.flags[1]:
            self.brake_counter = 0 # reset brake counter

            # takes the blobs and turns them into a proper turn angle
            steer.get_turn_angle(self)

            # executes changes
            steer.turn(self)
            motor.go(self)

        else: # OFFROAD
            self.led_off()
            # print(f"brake counter is {self.brake_counter}")
            self.brake_counter+=1

            # executes offroad plan
            steer.offroad(self)
            motor.offroad(self)


    # take the image and find the blobs
    def find_blobs(self):
        # reset values
        self.x_vals = []
        self.flags = []

        for r in config.ROIS:
            blobs = self.img.find_blobs(
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
                self.img.draw_rectangle(center_blob.rect(), color=0)
                self.img.draw_cross(center_blob.cx(), center_blob.cy(), color=0)

                self.x_vals.append(largest_blob.cx())
                self.flags.append(True)
            else:
                self.flags.append(False)