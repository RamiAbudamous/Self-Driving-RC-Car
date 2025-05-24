import config
import math

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

def get_turn_angle(car):
    angle_left = car.find_blob_angle(0) # 0 for left
    angle_right = car.find_blob_angle(2) # 2 for right

    # TODO: LOGIC HERE TO CONVERT THE LEFT AND RIGHT ANGLES TO ONE UNIFIED TURN ANGLE
    
    # first thing to test is just averaging them out
    angle = (angle_left+angle_right)/2


    car.angle_turn = angle # set the turn angle

# take the blobs and find the angles
def find_blob_angle(car, i): # i will be 0 or 2, 0 for left, 2 for right
    angle = -math.atan((car.x_vals[0+i]-car.x_vals[1+i])/(car.y_vals[0+i]-car.y_vals[1+i]))
    angle = math.degrees(angle) * (-1) #convert to degrees and flip because servo seems to be the other way around

    angle += config.ANGLE_OFFSET[i]

    if angle>45: #ensure that the angle is within the -45 to 45 range
        angle = 45.00000
    elif angle<-45:
        angle = -45.00000

    back = car.x_vals[1+i]
    front = car.x_vals[0+i]
    # TODO: this code might be flawed because it runs once for left and once for right. fix that
    if back>(160-config.OFFCENTER_ZONE) and front>(160-config.OFFCENTER_ZONE): # right of lane so turn left
        # angle = (-1*OFFCENTER_ANGLE)
        angle = (config.OFFCENTER_ANGLE)
        car.last_seen = config.LEFT
    elif back<config.OFFCENTER_ZONE and front<config.OFFCENTER_ZONE: # left of lane so turn right
        # angle = OFFCENTER_ANGLE
        angle = (-1*config.OFFCENTER_ANGLE)
        car.last_seen = config.RIGHT
    # # else: angle = 0

    return angle

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