"""!
@file TurretDriver.py
This file contains a class to a Turreted Nerf gun along
with functions for implementing 

@author Miloh Padgett, Tristan Cavarno, Jon Abraham
@date 1-Mar-2023 Original File
"""

import pyb 
import utime
import EncoderReader
import ClosedLoopController
import MotorDriver
import cotask
import task_share
import machine,neopixel
from image_processing import WIDTH,HEIGHT,IMG_SIZE,dfs,WIDTH_ST,WIDTH_END,HEIGHT_ST,HEIGHT_END,IMG_SIZE_N,WIDTH_N,HEIGHT_N
from mlx_cam import MLX_Cam
from array import array
from gc import collect
import math


DEGREES_TO_TICKS = 91.6666

def init_yaw(angle):
    '''!
    This function initializes a motor driver on pins B4,B5, and PA10
    and initializes an encoder on pins C6 and C7. 
    @param angle this is the target angle to go to
    @returns intialized encoder motor and controller objects
    '''
    #Set up pins and timer channel.
    in1 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
    in2 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
    en = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    timer = pyb.Timer(3,freq=20000)
    
    #Create motor driver object
    motorA = MotorDriver.MotorDriver(en,in1,in2,timer,False)

    #Set the GPIO pins and timer channel to pass into the encoder class
    ch1 = pyb.Pin (pyb.Pin.board.PC6, pyb.Pin.IN)
    ch2 = pyb.Pin (pyb.Pin.board.PC7, pyb.Pin.IN)
    tim8 = pyb.Timer(8,period=0xffff,prescaler = 0)
    
    #Create encoder driver object
    encoder = EncoderReader.EncoderReader(ch1,ch2,tim8)
    #run the contoller
    controller = ClosedLoopController.PController(.1,angle)
    
    
    return (encoder,motorA,controller)

def init_pitch():
    '''!
    This function initializes a motor driver on pins PA0,PA1, and PC1
    and initializes an encoder on pins PB6 and PB7. 
    @returns intialized encoder motor and controller objects
    '''
     #Set up pins and timer channel.
    in1 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    in2 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    en = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    timer = pyb.Timer(2,freq=20000)
    
    #Create motor driver object
    motorB = MotorDriver.MotorDriver(en,in1,in2,timer,True)

    #Set the GPIO pins and timer channel to pass into the encoder class
    ch1 = pyb.Pin (pyb.Pin.board.PB6, pyb.Pin.IN)
    ch2 = pyb.Pin (pyb.Pin.board.PB7, pyb.Pin.IN)
    tim8 = pyb.Timer(4,period=0xffff,prescaler = 0)
    
    #Create encoder driver object
    encoder = EncoderReader.EncoderReader(ch1,ch2,tim8)
    #run the contoller
    controller = ClosedLoopController.PController(.02,8000)
    return (encoder,motorB,controller)


def control_loop_one(encoder: EncoderReader.EncoderReader,
                    motorA: MotorDriver.MotorDriver,
                    controller: ClosedLoopController.PController,
                    yawAngle: task_share.Share):
    """!
    This function contains a motor control loop which reads encoder ticks,
    calculates the desired duty cycle, and runs the motor at that duty cycle.
    @param encoder an encoder for tracking distance traveled in the yaw direction
    @param motorA a motor driver for controlling yaw
    @param controller a p controller for motor control in the yaw direction
    @param yawAngle a share containing the target angle from the camera
    """
    controller.target = yawAngle.get()
    #Read encoder value
    encoder.read()
    actual = encoder.ticks
    #Calculate new duty cycle
    output = controller.run(actual)
    #Set new duty cyctle
    motorA.set_duty_cycle(output)
    #Stop motor after step response test

def control_loop_two(encoder: EncoderReader.EncoderReader,
                    motorA: MotorDriver.MotorDriver,
                    controller: ClosedLoopController.PController):
    """!
    This function contains a motor contrl loop which reads encoder ticks,
    claculates the desired duty cycle for pitch control
    @param encoder an encoder for tracking distance traveled in the yaw direction
    @param motorA a motor driver for controlling yaw
    @param controller a p controller for motor control in the yaw direction
    """
    #Read encoder value
    encoder.read()
    actual = encoder.ticks
    #Calculate new duty cycle
    output = controller.run(actual)
    #Set new duty cyctle
    motorA.set_duty_cycle(output)
    #Stop motor after step response test        

def yaw_control(shares):
    """!
    Task which initializes encoder, motor, and controller objects,
    and then feeds those to the close loop function.for yaw control
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    (yaw,yawlock) = shares
    n = int(yaw.get())
    (encoder,motorA,controller) = init_yaw(n)
    prev = [0]
    while True:
        cur =yawlock.get()
        while(cur == 4):
            yield 0
        if prev == 0 and cur == 1:
            print("steady state")
        control_loop_one(encoder,motorA,controller,yaw,prev)
        if(abs(controller.target - encoder.ticks) < 300):
            if(cur != 2):
                yawlock.put(1)
            else:
                yawlock.put(3)
        else:
            yawlock.put(0)
        prev = cur
        yield 0

def pitch_control():
    """!
    Task which initializes encoder, motor, and controller objects,
    and then feeds those to the close loop function for pitch control.
    """
    # Get references to the share and queue which have been passed to this task
    (encoderB,motorB,controller) = init_pitch()

    while True:
        control_loop_two(encoderB,motorB,controller)
        yield 0

def real_camera(shares):
    """!
    A function for performing computation on an
    image and determining a target angle to shoot at
    @param shares  a tuple of shares to set target yaw angles and state to determine when to run the camera code
    """
    (yaw,yawlock) = shares

    #start the i2c connection
    i2c_bus = machine.I2C(1)
    print("MXL90640 Easy(ish) Driver Test")


    # Create the camera object and set it up in default mode
    camera = MLX_Cam(i2c_bus)
    while(True):
        #if the gun isn't at a stable state dont do anything
        while yawlock.get() != 1 :
            print("not ready for cam")
            yield 0 
        #start on a new frame
        biggest = None
        image = camera.get_image()
        collect()
        arr = array('l')
        #get a scale for collapsing img data down to 0-255
        minny = min(image)
        scale = 255.0 / (max(image) - minny)
        #create a editable array to do computation on
        for row in range(HEIGHT_ST,HEIGHT_END):
            for col in range(WIDTH_ST,WIDTH_END):
                i = WIDTH*row+col
                arr.append(int((image[i]-minny)*scale))
        image = None
        collect()
        #find the largest blob above 175 in the image
        for x in range(WIDTH_N):
            for y in range(HEIGHT_N):
                blob = dfs(arr,x,y)
                if biggest == None:
                    biggest = blob
                elif(blob != None and len(blob) > len(biggest)):
                    biggest = blob
        #if we found the blob then get the avg x distance and give a new yaw angle
        #to the yaw controller
        if biggest != None and len(biggest) != 0:
            avg = 0
            for key in biggest:
                avg += biggest[key].x
            angle = 180 - 360*((math.pi*2)**-1)*math.atan((10-(avg//len(biggest)))/40)
            print(f"{avg//len(biggest)},angle{angle}")
            yaw.put(int(angle*DEGREES_TO_TICKS))
            #camera.ascii_image_dfs(arr,biggest)
            
            print("\n")
        biggest = None
        blob = None
        collect()
        yield 0

def shoot_fun(yawlock):
    '''!
    function for determining when to shoot and turn the correct motors on
    @param yawlock the current state of the turret
    '''
    #init the needed gun pins
    in1 = pyb.Pin(pyb.Pin.board.PB3,pyb.Pin.OUT_PP)
    in3 = pyb.Pin(pyb.Pin.board.PA6,pyb.Pin.OUT_PP)
    #turn the tigger off and the flywheels on
    in3.low()
    in1.high()
    #capture the start time
    start_time = utime.ticks_ms()
    cur_time = start_time

    #wait for 6 seconds
    while(cur_time-start_time < 6000):
        cur_time = utime.ticks_ms()
        print(cur_time-start_time)
        yield 0
    #wait for the turret to reach stread state and turn off
    #additional camera images
    while(yawlock.get() != 3):
        yawlock.put(2)
        print("wainting to take the sh")
        yield 0
    yawlock.put(1)  
    #shoot the gun!
    print("taking the shot")
    in3.high()
    pyb.delay(500)
    in3.low()
    pyb.delay(750)
    in3.high()
    pyb.delay(500)
    in3.low()
    in1.low()
    print("DONE")
    #stop doing anything selse.
    while(True):
        yawlock.put(4)
        yield 0 

class TurretDriver:
    """! 
    This class is an object allowing tasksharing implementation
    of a two axist turreted nerf gun
    """
    def __init__(self):
        """!
        init all the needed variable for the future like tasklists and shares
        """
        self.task_list = cotask.TaskList()
        self.yaw_task = None
        self.pitch_task = None
        self.yaw_angle = task_share.Share('i', thread_protect=False, name="yaw_angle")
        self.targ = task_share.Share('B', thread_protect=False, name="reached_target")

        self.fake_task = None


    def yaw_to(self,angle):
        """!
        add the yaw task to the scheduler
        @param a target starting angle.
        """
        if self.yaw_task == None:
            self.yaw_task = cotask.Task(yaw_control, name="Yaw", priority=3, period=20,
                        profile=True, trace=False, shares=[self.yaw_angle,self.targ])
            self.yaw_angle.put(int(angle*DEGREES_TO_TICKS))           
            self.task_list.append(self.yaw_task)
        else:
            print("Tried to yaw while current yaw in action") 
    def pitch(self):
        """!
        add a pitch task to the scheduler defaults to a set pitch height
        """
        if self.pitch_task == None:
            self.pitch_task = cotask.Task(pitch_control,name = "pitch",priority=3, period=50,
                        profile=True, trace=False, shares=None)
            self.task_list.append(self.pitch_task)
            
        else:
            print("Tried to yaw while current yaw in action")    

    def cam(self):
        """!
        Add the camera processing task to the scheduler
        """
        if self.fake_task == None:
            self.fake_task = cotask.Task(real_camera,name = "real",priority=1, period=250,
                        profile=True, trace=False, shares=[self.yaw_angle,self.targ])
            self.task_list.append(self.fake_task)
        else:
            print("something dumb haopened")
    def shoot(self):
        """!
        Add the shoot task to the scheduler
        """

        self.shoot = cotask.Task(shoot_fun,name = "shoot",priority=2, period=100,
                        profile=True, trace=False, shares=self.targ)
        self.task_list.append(self.shoot)

    def run_action(self):
        """!
        Infinitly run the task scheduler until a keyboard
        interrupt is triggered.
        """
        while True:
            try:
                self.task_list.pri_sched()
            except KeyboardInterrupt:
                break
        

    