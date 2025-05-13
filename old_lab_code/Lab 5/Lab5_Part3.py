import time
from machine import PWM, LED

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

ledblue = LED("LED_BLUE")
ledblue.on()

# STARTUP: In neutral for at least 5 seconds
p7.duty_ns(1500000)
p9.duty_ns(1500000)
time.sleep_ms(10000)

ledblue.off()

p9.duty_ns(1650000)
time.sleep_ms(1000)
p9.duty_ns(1500000)
time.sleep_ms(1000)
p9.duty_ns(1650000)

# # slowly increase speed to 1.65
# for i in range(1, 10):
#     p9.duty_ns(1500000+int(15000*i))
#     # need to increase by 150k, increase by 15k every .75 seconds, reaches max speed in 7.5 sec
#     time.sleep_ms(750)


# # Slow down to a very slow speed (1.55)
# for i in range(1, 10):
#     p9.duty_ns(1650000-int(1000*i))
#     # need to decrease to 1.55, decresae by 10k every .25 seconds, reaches speed in 2.5 sec
#     time.sleep_ms(250)

# p9.duty_ns(1650000-int(1000*i))
led = LED("LED_RED")
led.on()

while True:
    # Turn to the right
    for i in range(1, 10):
        p7.duty_ns(1500000+(40000*i))
        # need to increase to by 400k in 2 sec, increase by 40k every .2 sec
        time.sleep_ms(200)


    # Turn to the left
    for i in range(1, 20):
        p7.duty_ns(1900000-(40000*i))
        # need to decrease to by 800k in 4 sec, decrease by 40k every .2 sec
        time.sleep_ms(200)


    # Return to neutral
    for i in range(1, 10):
        p7.duty_ns(1100000+(40000*i))
        # need to increase to by 400k in 2 sec, increase by 40k every .2 sec
        time.sleep_ms(200)
