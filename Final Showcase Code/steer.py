import config
import math

def convert_angle(theta):
    # make compatible with PWM
    sigma = int(theta * config.TURN_STRENGTH)
    if sigma > -1*config.DEADZONE and sigma < config.DEADZONE:
        sigma = 0

    # floor and ceiling, and convert from ns to us
    sigma = int(max((-1*config.MAX_SIGMA), min(config.MAX_SIGMA, sigma))/1000)

    # print(f"sigma is {sigma}, angle is {sigma+1500}")
    return int((sigma + 1500)*(19200/10000))  # microseconds

def get_turn_angle(car):
    left_distance = 80 - car.x_vals[0]
    right_distance = car.x_vals[1] - 80

    car.angle_turn = config.ANGLE_DIFF_OFFSET * (left_distance - right_distance) # set the turn angle
    # print(f"angle = {car.angle_turn}, left = {left_distance}, right = {right_distance}")

def turn(car):
    # execute changes before running a bunch of slow IO code
    car.servo_ch.pulse_width(convert_angle(car.angle_turn))

    if car.angle_turn>(config.ANGLE): # left
        car.led_off()
        car.blueled.on()
        car.last_seen = config.LEFT
        print(f"left, angle is {car.angle_turn}")
    elif car.angle_turn<(-1*config.ANGLE): # right
        car.led_off()
        car.redled.on()
        car.last_seen = config.RIGHT
        print(f"right, angle is {car.angle_turn}")
    else: #straight
        car.led_off()
        car.greenled.on()
        print(f"straight, angle is {car.angle_turn}")


def offroad(car):
    if car.last_seen==config.RIGHT:
        turn_angle_us = convert_angle(-1*config.OFFROAD_ANGLE)
        # print(f"offroad right, angle is {config.OFFROAD_ANGLE}, sigma is {turn_angle_us}")
    else: # if LEFT
        turn_angle_us = convert_angle(config.OFFROAD_ANGLE)
        # print(f"offroad left, angle is {config.OFFROAD_ANGLE}, sigma is {turn_angle_us}")

    car.servo_ch.pulse_width(turn_angle_us)
