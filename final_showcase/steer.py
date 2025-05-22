import config

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

def turn(car):
    # enable led based on angle and get sigma
    if car.angle_turn<(-1*config.ANGLE): # left
        car.led_off()
        car.blueled.on()
        car.last_seen = config.LEFT
    elif car.angle_turn>config.ANGLE: # right
        car.led_off()
        car.redled.on()
        car.last_seen = config.RIGHT
    else: #straight
        car.led_off()
        car.greenled.on()

    turn_angle_us = convert_angle(car.angle_turn)
    car.servo_ch.pulse_width(turn_angle_us)

def offroad(car):
    if car.last_seen==config.RIGHT:
        turn_angle_us = convert_angle(config.OFFROAD_ANGLE)
        car.servo_ch.pulse_width(turn_angle_us) # turn right
        print(f"offroad right, angle is {config.OFFROAD_ANGLE}, sigma is {turn_angle_us}")
    else: # if LEFT
        turn_angle_us = convert_angle(-1*config.OFFROAD_ANGLE)
        car.servo_ch.pulse_width(turn_angle_us) # turn left
        print(f"offroad left, angle is {config.OFFROAD_ANGLE}, sigma is {turn_angle_us}")