import time
from machine import PWM

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

while True:
    # Straight and Brake for 10 seconds
    p7.duty_ns(1500000)
    p9.duty_ns(1500000)
    time.sleep_ms(10000)

    # Right and Forward for 2 seconds
    p7.duty_ns(1900000)
    p9.duty_ns(1650000)
    time.sleep_ms(2000)

    # Straight and Forward for 2 seconds
    p7.duty_ns(1500000)
    p9.duty_ns(1650000)
    time.sleep_ms(2000)


    # Left and Forward for 2 seconds
    p7.duty_ns(1100000)
    p9.duty_ns(1650000)
    time.sleep_ms(2000)


    # Straight and Brake for 2 seconds
    p7.duty_ns(1500000)
    p9.duty_ns(1500000)
    time.sleep_ms(2000)


    # Straight and Reverse for 1 second
    p7.duty_ns(1500000)
    p9.duty_ns(1300000)
    time.sleep_ms(1000)


    # Straight and Brake for 1 second
    p7.duty_ns(1500000)
    p9.duty_ns(1500000)
    time.sleep_ms(1000)


    # Straight and Reverse for 2 seconds
    p7.duty_ns(1500000)
    p9.duty_ns(1300000)
    time.sleep_ms(2000)


