import time
from machine import PWM

p7 = PWM("P7", freq=1600, duty_u16=32768)
#should be 1600hz for p7, 100hz for p9

p9 = PWM("P9", freq=100, duty_u16=32768)

max = 65536

while True:
    for i in range(10, 90, 1):
        p7.duty_u16(0 + int((i*max)/100))
        p9.duty_ns(1000000 + (i*10000))
        time.sleep_ms(100)


    # INDIVIDUAL LOOPS:

    # for i in range(1, 9, 1):
    #     p7.duty_u16(0 + int((i*max)/10))
    #     time.sleep_ms(10)

    # for i in range(0, 800000, 10000):
    #     p9.duty_ns(1000000 + i)
    #     time.sleep_ms(10)
