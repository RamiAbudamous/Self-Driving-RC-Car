# Autonomous Vehicle - EEC 195
## By Rami Abudamous, Sumi Alem, Sean Cohen, and Avery Schneider

This project takes a TRAXXAS Rustler car and enables it to follow a track using an OpenMV Can H7 R2 microcontroller to adjust steering in real time. The OpenMV's camera feed is processed by a set of python scripts to determine the angle and speed to move at.
The PCB is a custom design built around a VNH5019 H-Bridge to drive the Rustler's brushed DC motor. Steering is handled via PWM signals that are sent from the OpenMV to the car's servo. The OpenMV camera was mounted on a custom 3D printed support system. Overall, computer vision, embedded logic, and hardware design were used in tandem to create a fast and accurate autonomous vehicle.

[This video](https://youtu.be/4q3OOZRYBcs) goes in depth on the design process, specifications, and a demonstration of the car.
