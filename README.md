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

The STM32 is central to the entire electrical design as it is the microcontroller that drives the whole system. Attached the the STM is the Shoe of Brian, and the IHM04A1 Motor Driver. The Shoe of Brian is used for control of the two 12V DC motor encoders and the Thermal Camera. The 3.3v and ground terminals of the shoe are used for powering these three components. Encoder A and B data channels on the pitch encoder are attached to GPIO pins PB6 and PB7 respectively. Encoder A and B data channels on the yaw encoder are attached to GPIO pins PC6 and PC7 respectively. GPIO pins PB8 and PB9 are connected to the SCL and SDA pins respectively on the Thermal Camera. The IHM04A1 Motor Driver is used for powering the 12V DC motors. It's VDD and GND are connected to a bench power supply outputting 12V at a current limit of 2A. B+ and B-, connected to PA0 and PA1 on the STM, are used to power the pitch axis motor and determine it's direction by adjusting the outputs from the aforementioned pins. The same is done for the yaw axis DC motors using A+ and A- on the motor driver, which are connected to GPIO pins PB4 and PB5 respectively. Finally, the L298N Motor Driver is used for control of the flywheel and firing pin on the snowcinda blaster.

## Software Design


## Future Recommendations

Here is a list of some lessons that we have learned while working on this project and recommendations for work on similar systems in the future:
- Properly tensioned timing belts reduce backlash and would allow for more accurate and reliable positional control.
- A more universal hinge design (i.e. mounting the bearings on a block of wood or thinner triangular mounts) allows for faster iteration/saving material.
- Make a separate control box assembly to simplify the construction of the gun base and reduce clearance issues 
