import car

# create car object and initialize
car = car.openMV() # create the microcontroller object
car.initialize()

while True:
    car.tick()
