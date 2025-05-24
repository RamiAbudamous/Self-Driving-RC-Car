import car
from pyb import Timer, Pin
from machine import LED
import config, motor, steer
import time, math, sensor

# create car object and initialize
car = car.openMV() # create the microcontroller object
car.initialize()

while True:
    car.tick()