import config

def convert_speed(input_speed):
    speed = max(1500, min(config.MAX_SPEED, input_speed)) # clip speed
    return int(speed*(19200/10000)) #scale speed and return

def go(car):
    # brake if kill
    if config.KILL==1:
        car.motor_ch.pulse_width(convert_speed(1500))

    # lower speed if angle is outside the deadzone
    elif abs(car.angle_turn)>config.DEADZONE_ANGLE:
        speed = max(config.MIN_SPEED, config.MAX_SPEED - int((abs(car.angle_turn)*config.SPEED_SCALAR)))

    # if not turning, go max speed
    else: speed = config.MAX_SPEED

    car.motor_ch.pulse_width(convert_speed(speed_detect(car, speed)))
    # print(f"angle is {angle}, sigma is {turn_angle_us}, speed is {speed}")

def offroad(car):
    # brake if kill
    if config.KILL==1:
        car.motor_ch.pulse_width(convert_speed(1500))

    elif car.brake_counter>=100: # if nothing spotted for a while, then brake
        car.motor_ch.pulse_width(convert_speed(1500))

    else: # offroad but still alive, so slow down but dont stop.
        car.motor_ch.pulse_width(convert_speed(config.MIN_SPEED)) # slow down a lot

def speed_detect(car, speed):
    # basically just multiply speed by max_velocity / velocity to always keep it at basically max
    speed_ratio = max(1, min(1.5, float(config.max_velocity / config.velocity))) # take the ratio and ensure its between 1 and 1.5 for safety (so it doesnt randomly go like 5x speed and burn the H Bridge)
    return int(speed_ratio * speed)
