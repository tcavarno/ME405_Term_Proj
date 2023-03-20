# ME405 Term Project 
## ME 405 
#### **Authors: Tristan Cavarno, Miloh Padgett, Jon Abraham**

The following documentation describes our design for the ME405 Term Project: Learn by Dueling. The objective of this project was to create 
a system that autonomously aims and fires a foam dart gun at a target from an opposing team. Infrared (IR) cameras and DC Motors were provided 
by the lab instructor. The rest of the system was purchased and/or manufactured.


## Hardware Design
Per the project guidelines, the dart gun was required to face 180&deg; away from the opponent in its starting position. Two axes of motion were needed,
so a yaw axis (for horizontal motion) and pitching axis (vertical positioning of the gun) were chosen. From a previous assignment and preliminary
testing, it was determined that gearing ratios of 1:2 and 1:6 respectively would provide adequate torque to move the approximate mass of the gun and 
pitching carriage assembly. These ratios are directly proportional to the encoder ticks required for an angular setpoint, so increasing the ratio
provides greater precision at slower speeds. Spur gears mounted with press fits on the D-slotted motor shafts were chosen due to ease of iteration with 3D printing, and slots 
were included in each motor mount to provide adjustable mating surfaces. The pitching axis rested on two PLA hinges with a machined aluminum drive shaft and 8mm flanged ball
bearings. These hinges were then bolted on top of a geared lazy susan bearing to enable the yaw motion. See Figures 1 and 2 below for labeled diagrams with the two axes of 
motion and a picture of the fully assembled system. 

![Figure 1. CAD Model](CAD.png)

**Figure 1.** Isometric SolidWorks Assembly view with the two axes of motion labeled. 

![Figure 2. Picture of Entire Assembly](turret_pic.png)

**Figure 2.** Photo of assembled system during testing. 

The code in this repository was writted to interface with two Ametek/Pittman PG6712A077-R3 6665 motors. The dart gun that we selected was a Snowcinda Automatic Machine Gun Toy Gun
purchased from Amazon. 

## Circuit Schematics 
The following components were used electrically for the operation of this project. Their interconnection is shown below in Figure 3. 
* 1x STM32 NUCELO L476RG.  
* 1x Shoe of Brian.  
* 1x IHM04A1 Motor Driver.  
* 1x L298N Motor Driver.  
* 2x Variable Power Supply.  
* 2x 12V Ametek/Pittman DC Motors with Encoders.  
* 1x MLX90640 Thermal Infrared Camera.   
* 1x 3.7V Snowcinda Toy Gun Firing Pin Mechanism/Motor.  
* 1x 3.7V Snowcinda Toy Gun Flywheel Mechanism/Motor.  


![Figure 3. Wiring Diagram](ME405_WiringDiagram.jpeg)

**Figure 3.** Wiring diagram of all of the connections to the STM32 and various motors and motor controllers necesaary for controlling the gun. 

The STM32 is central to the entire electrical design as it is the microcontroller that drives the whole system. Attached the the STM is the Shoe of Brian, and the IHM04A1 Motor Driver. The Shoe of Brian is used for control of the two 12V DC motor encoders and the Thermal Camera. The 3.3v and ground terminals of the shoe are used for powering these three components. Encoder A and B data channels on the pitch encoder are attached to GPIO pins PB6 and PB7 respectively. Encoder A and B data channels on the yaw encoder are attached to GPIO pins PC6 and PC7 respectively. GPIO pins PB8 and PB9 are connected to the SCL and SDA pins respectively on the Thermal Camera. The IHM04A1 Motor Driver is used for powering the 12V DC motors. It's VDD and GND are connected to a bench power supply outputting 12V at a current limit of 2A. B+ and B-, connected to PA0 and PA1 on the STM, are used to power the pitch axis motor and determine it's direction by adjusting the outputs from the aforementioned pins. The same is done for the yaw axis DC motors using A+ and A- on the motor driver, which are connected to GPIO pins PB4 and PB5 respectively. Finally, the L298N Motor Driver is used for control of the flywheel and firing pin on the snowcinda blaster. The first thing to note about this motor driver is that there is an approximate 2V-2.5V drop across the H-bridge, thus the necessity for providing it with 6.2V at 2A to reach the goal of 3.7V for these motors. The second thing to note is that this motor controller, in addition to the pins shown in the schematic, has an enable pin for each of the 2 channels which were bridged to VDD to allow for simpler control. With the enable pins pulled high, setting in1 to high and in2 to low would correspondingly set out1 high and out2 low, and likewise with in3, in4, out3, and out4. Since we only ever wanted to spin the connected motors one direction, we chose to tie in2 and in4 to ground so thet when in1 is set high by the STM, the motor connected to out1 and out2 will spin, and when in3 is set high by the STM, the motor connected to out3 and out4 will spin. The flywheel motor is connected to out1 and out2 which is controlled by the in1 pin connected to GPIO pin PB3 on the STM. The firing pin motor is connected to out3 and out4 which is controlled by the in3 pin connected to GPIO pin PA6 on the STM. All of the components and connections described allow for receipt of data from the Thermal camera and motor encoders, as well as control of the two axis of movement and firing of the blaster. An emergency stop button was also added to the system to allow a user to stop the pitch and yaw movement at the press of a button.

## Software Design
The dueling functionalities of this system begin with the press of the on-board STM32 blue user button. Upon this button being pressed, the flywheel motors begin spinning, the yaw motor spins the gun 180 degrees to be oriented looking at an opponent, and the camera begins capturing images. The camera processing task captures images, cuts them down only to the pixels in the frame of the far end of the table, filters out pixels below a certain intensity, and then performs a depth-first search algorithm to categorize blobs of pixels most likely to be the opponent. Upon finding an oponent, the location in the image frame is translated to an angle for the gun to point to and then passes that target angle to the yaw task. The yaw task recieves the target angle and uses a closed loop controller to move to the target. This continues until 5 seconds has elapsed, upon which time the camera task is given one more opportunity to ensure the target is correct and pass that information to the yaw task to move the gun angle to that target. The firing task then runs the firing pin to take two shots with enough time in between to allow the flywheels to get back up to speed. After the two shots have been taken, the flywheels turn off and the control loop is finished. Exactl file descriptions and task diagrams are provided in the main page Doxygen documentation.

## Results
To ensure the system properly aimed and fired, we performed separate camera and calibration tests. To derive the relationship between target position and yaw angle, we emulated duels by placing the camera 8 feet from a target. This test allowed us to verify that the camera had a high enough resolution to make out a human target accurately and reliably at distance. Additionally, we calculated the pixel to distance ratio and worked out the necessary yaw angle with trigonometry. This requires that the camera and turret are placed in consistent locations, so a jig was created to align the camera with the center of the table. 

Though we derived an empirical relationship between the horizontal target position and yaw angle, gun firing, measurement, and motor control inaccuracies made it necessary to fine tune our algorithm. This was done through continuous duel testing and tweaking the distance ratio. Additionally, we changed the period of each task such that the aiming and shooting sequence ran as fast as possible with our hardware. Overall, we were able to consistently take two shots in under 10 seconds and win the duel tournament in our lab section. 

## Future Recommendations

Here is a list of some lessons that we have learned while working on this project and recommendations for work on similar systems in the future:
- Properly tensioned timing belts reduce backlash and would allow for more accurate and reliable positional control.
- A more universal hinge design (i.e. mounting the bearings on a block of wood or thinner triangular mounts) allows for faster iteration/saving material.
- Make a separate control box assembly to simplify the construction of the gun base and reduce clearance issues 
- More lightweight camera processing code would allow for faster tracking an target picking.
- Documenting all GPIO pins that are tied timers and channels being used by various peripherals as you go is helpful and avoids tricky bugs.
