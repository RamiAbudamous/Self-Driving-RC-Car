import time, math, sensor
from pyb import Timer, Pin
from machine import LED
import config
import motor
import steer
import car

# create car object and initialize
car = car.openMV() # create the microcontroller object
car.initialize()

while True:
    car.tick()