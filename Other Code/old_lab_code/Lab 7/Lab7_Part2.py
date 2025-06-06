import time
from machine import LED, Timer, Pin

# GLOBALS:
blueled = LED("LED_BLUE")
rotations = 0
constant_mult = 31

def tick(timer):
    # blueled.toggle()
    global rotations
    print(f"The velocity was {constant_mult*rotations}cm/s ({rotations} rotations) ")
    rotations=0

def isr(p):
    # print("interrupted")
    global rotations
    blueled.toggle()
    rotations+=1
    # time.sleep_ms(100)

tim = Timer(-1, freq=1, callback=tick)
pin = Pin("P4", Pin.IN) # pin.pull_up is an internal resistor

pin.irq(trigger = Pin.IRQ_FALLING, handler=isr) # activate on falling edge
while True:
  # print(f"pin value is {pin.value()}")
  time.sleep_ms(100)
