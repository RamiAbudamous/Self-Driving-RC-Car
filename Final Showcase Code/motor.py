import config

def brake(car):
    car.motor_ch.pulse_width(convert_speed(0))

def convert_speed(input_speed):
    speed = max(config.MIN_SPEED, min(config.MAX_SPEED, input_speed)) # clip speed
    # return int(speed*(19200/10000)) #scale speed and return
    return int(speed*(config.SPEED_CONVERT_SCALAR/100)) #scale speed and return

def go(car):
    # brake if kill
    if config.KILL==1:
        brake(car)
    # lower speed if angle is outside the deadzone
    elif abs(car.angle_turn)>config.DEADZONE_ANGLE:
        speed = max(config.MIN_SPEED, config.MAX_SPEED - int((abs(car.angle_turn)*config.SPEED_SCALAR)/1000))
    # if not turning, go max speed
    else: speed = config.MAX_SPEED

    # new_speed = convert_speed(speed_detect(speed))
    new_speed = convert_speed(speed)
    car.motor_ch.pulse_width(new_speed)
    # print(f"angle is {angle}, sigma is {turn_angle_us}, speed is {speed}")

def offroad(car):
    # brake if kill
    if config.KILL==1:
        brake(car)
    elif car.brake_counter>=100 and config.COUNT_BRAKES==True: # if nothing spotted for a while, then brake
        brake(car)
    else: # offroad but still alive, so slow down but dont stop.
        car.motor_ch.pulse_width(convert_speed(config.MIN_SPEED)) # slow down a lot