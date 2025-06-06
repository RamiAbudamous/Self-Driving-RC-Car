# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Robust Linear Regression Example
#
# This example shows off how to use the get_regression() method on your OpenMV Cam
# to get the linear regression of a ROI. Using this method you can easily build
# a robot which can track lines which all point in the same general direction
# but are not actually connected. Use find_blobs() on lines that are nicely
# connected for better filtering options and control.
#
# We're using the robust=True argument for get_regression() in this script which
# computes the linear regression using a much more robust algorithm... but potentially
# much slower. The robust algorithm runs in O(N^2) time on the image. So, YOU NEED
# TO LIMIT THE NUMBER OF PIXELS the robust algorithm works on or it can actually
# take seconds for the algorithm to give you a result... THRESHOLD VERY CAREFULLY!


import sensor
import time
from machine import LED
redled = LED("LED_RED")
blueled = LED("LED_BLUE")
greenled = LED("LED_GREEN")
def led_off():
    redled.off()
    blueled.off()
    greenled.off()

ENABLE_LENS_CORR = True  # turn on for straighter lines...

THRESHOLD = (208, 255)  # Grayscale threshold for dark things.
BINARY_VISIBLE = True  # Binary pass first to see what linear regression is running on.

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQQVGA)  # 80x60 (4,800 pixels) - O(N^2) max = 23,040,000.
sensor.skip_frames(time=2000)  # WARNING: If you use QQVGA it may take seconds
clock = time.clock()  # to process a frame sometimes.

MIN_DEGREE = 0 # 45
MAX_DEGREE = 179 # 135

while True:
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD]) if BINARY_VISIBLE else sensor.snapshot()
    if ENABLE_LENS_CORR:
        img.lens_corr(1.8)  # for 2.8mm lens...

    led_off()

    # Returns a line object similar to line objects returned by find_lines() and
    # find_line_segments(). You have x1(), y1(), x2(), y2(), length(),
    # theta() (rotation in degrees), rho(), and magnitude().
    #
    # magnitude() represents how well the linear regression worked. It means something
    # different for the robust linear regression. In general, the larger the value the
    # better...
    line = img.get_regression(
        [(255, 255) if BINARY_VISIBLE else THRESHOLD], robust=True
    )

    # if line:
    #     img.draw_line(line.line(), color=127)
    # print("FPS %f, mag = %s" % (clock.fps(), str(line.magnitude()) if (line) else "N/A"))

    # lines = img.find_lines(threshold=1000, theta_margin=0, rho_margin=15)
    if line:
        img.draw_line(line.line(), color=127)
        led_off()

        theta = line.theta()
        rho = line.rho()

        # fix theta
        if theta>90 and theta<135:
            theta = 135
        if theta>=135:
            theta -= 180
        if theta>45 and theta<90:
            theta = 45
        theta *= (-1)

        # now check if car is in one third of the frame
        if (abs(theta)-45)>-25: # if at an extreme then theyre in different thirds
            print(f"defnection angle: {theta}. Rho: {rho}. None")
            led_off()
        elif (rho<=25):
            print(f"defnection angle: {theta}. Rho: {rho}. Left")
            blueled.on()
        elif (rho>=55):
            print(f"defnection angle: {theta}. Rho: {rho}. Right")
            redled.on()
        elif (rho>25 and rho<55):
            print(f"defnection angle: {theta}. Rho: {rho}. Center")
            greenled.on()
        else:
            print(f"defnection angle: {theta}. Rho: {rho}. None")
            led_off()

    # print("end of frame\n")
# About negative rho values:
#
# A [theta+0:-rho] tuple is the same as [theta+180:+rho].
