import time, sensor
from pyb import Timer, Pin
from machine import LED
import config, steer, motor, speed

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

    # Speed detector
    tim = Timer(2, freq=1, callback=speed.timer_tick)
    pin = Pin("P4", Pin.IN) # pin.pull_up is an internal resistor
    rotations = 0
    pin.irq(trigger = Pin.IRQ_FALLING, handler=speed.isr) # activate on falling edge
    # pin.irq(trigger = Pin.IRQ_FALLING, handler=self.isr) # activate on falling edge
    velocity = 1      # update with a reasonable starting velocity
    max_velocity = 1  # update with a reasonable maximum  velocity

    # LED Definitions
    redled = LED("LED_RED") # RIGHT
    greenled = LED("LED_GREEN") # STRAIGHT
    blueled = LED("LED_BLUE") # LEFT

    # other variables
    clock = None
    img = None
    x_vals = [0, 0, 0, 0]
    y_vals = [0, 0, 0, 0]
    flags = [False, False, False, False]
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
        self.img = sensor.snapshot()  # Take a picture and return the image.

        self.find_blobs()

        if self.flags[0] and self.flags[1] and self.flags[2] and self.flags[3]:
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
        old_x_vals = self.x_vals
        old_y_vals = self.y_vals
        self.x_vals = []
        self.y_vals = []
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
                self.y_vals.append(largest_blob.cy())
                self.flags.append(True)
            else:
                self.x_vals.append(old_x_vals[len(self.flags)])
                self.y_vals.append(old_y_vals[len(self.flags)])
                self.flags.append(False)

        if self.flags[0] and self.flags[1]:
            self.img.draw_line((self.x_vals[0], self.y_vals[0], self.x_vals[1], self.y_vals[1]), color=0)
        if self.flags[2] and self.flags[3]:
            self.img.draw_line((self.x_vals[2], self.y_vals[2], self.x_vals[3], self.y_vals[3]), color=0)
