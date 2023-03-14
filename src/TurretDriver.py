"""!
@file TurretDriver.py
This file contains a class to a Turreted Nerf gun

@author Miloh Padgett, Tristan Cavarno, Jon Abraham
@date 30-Jan-2023 Original File
"""

import pyb 
import utime
import EncoderReader
import ClosedLoopController
import MotorDriver
import cotask
import task_share
import machine,neopixel
from image_processing import WIDTH,HEIGHT,IMG_SIZE,dfs
from mlx_cam import MLX_Cam
from array import array
from gc import collect
import math


DEGREES_TO_TICKS = 91.6666

def init_yaw(angle):
    '''!
    This function initializes a motor driver on pins B4,B5, and PA10
    and initializes an encoder on pins C6 and C7. 
    @param NA
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
    This function initializes a motor driver on pins B4,B5, and PA10
    and initializes an encoder on pins C6 and C7. 
    @param NA
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
    controller = ClosedLoopController.PController(.02,7000)
    return (encoder,motorB,controller)


def control_loop_one(encoder: EncoderReader.EncoderReader,
                    motorA: MotorDriver.MotorDriver,
                    controller: ClosedLoopController.PController,
                    yawAngle: task_share.Share,
                    prev):
    """!
    This function contains a motor copintrol loop which reads encoder ticks,
    claculates the desired duty cycle, and runs the motor at that duty cycle.
    @param encoder motor and controller class objects
    @returns NAt
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
    This function contains a motor copintrol loop which reads encoder ticks,
    claculates the desired duty cycle, and runs the motor at that duty cycle.
    @param encoder motor and controller class objects
    @returns NAt
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
    and then feeds those to the close loop function.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    (yaw,steady_state) = shares
    n = int(yaw.get())
    (encoder,motorA,controller) = init_yaw(n)
    prev = [0]
    while True:
        while(steady_state.get() == 4):
            print("DONE")
            yield 0
        control_loop_one(encoder,motorA,controller,yaw,prev)
        if(abs(controller.target - encoder.ticks) < 300):
            if(steady_state.get() != 2):
                steady_state.put(1)
            else:
                steady_state.put(3)
        else:
            steady_state.put(0)
        yield 0

def pitch_control():
    """!
    Task which initializes encoder, motor, and controller objects,
    and then feeds those to the close loop function.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    (encoderB,motorB,controller) = init_pitch()

    while True:
        control_loop_two(encoderB,motorB,controller)
        yield 0

def real_camera(shares):
    (yaw,steady_state) = shares
    i2c_bus = machine.I2C(1)
    scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]

    print("MXL90640 Easy(ish) Driver Test")


    # Create the camera object and set it up in default mode
    camera = MLX_Cam(i2c_bus)
    while(True):
        while steady_state.get() != 1 :
            yield 0 
        biggest = None
        image = camera.get_image()
        collect()
        arr = array('l')
        minny = min(image)
        scale = 255.0 / (max(image) - minny)
        for elm in image:
            arr.append(int((elm-minny)*scale))
        image = None
        collect()
        for x in range(WIDTH):
            for y in range(HEIGHT):
                blob = dfs(arr,x,y)
                if biggest == None:
                    biggest = blob
                elif(blob != None and len(blob) > len(biggest)):
                    biggest = blob
        if biggest != None:
            avg = 0
            for key in biggest:
                avg += biggest[key].x
            angle = 180 - 360*((math.pi*2)**-1)*math.atan((14.5-(avg//len(biggest)))/60)
            print(f"angle{angle}")
            yaw.put(int(angle*DEGREES_TO_TICKS))
        biggest = None
        blob = None
        collect()
        yield 0

def shoot_fun(share):
    in1 = pyb.Pin(pyb.Pin.board.PA5,pyb.Pin.OUT_PP)
    in3 = pyb.Pin(pyb.Pin.board.PA6,pyb.Pin.OUT_PP)
    in3.low()
    in1.high()
    start_time = utime.ticks_ms()
    cur_time = start_time
    while(cur_time-start_time < 6000):
        cur_time = utime.ticks_ms()
        yield 0
    while(share.get() != 3):
        share.put(2)
        print("wainting to take the sh")
        yield 0
    share.put(1)

    print("taking the shot")
    in3.high()
    pyb.delay(500)
    in3.low()
    pyb.delay(500)
    in3.high()
    pyb.delay(500)
    in3.low()
    while(True):
        share.put(4)
        yield 0 

class TurretDriver:
    """! 
    This class implments X, Y Axis Control an ME405 kit. 
    """
    def __init__(self):
        self.task_list = cotask.TaskList()
        self.yaw_task = None
        self.pitch_task = None
        self.yaw_angle = task_share.Share('i', thread_protect=False, name="yaw_angle")
        self.targ = task_share.Share('B', thread_protect=False, name="reached_target")

        self.fake_task = None


    def yaw_to(self,angle):
        if self.yaw_task == None:
            self.yaw_task = cotask.Task(yaw_control, name="Yaw", priority=3, period=10,
                        profile=True, trace=False, shares=[self.yaw_angle,self.targ])
            self.yaw_angle.put(int(angle*DEGREES_TO_TICKS))           
            self.task_list.append(self.yaw_task)
        else:
            print("Tried to yaw while current yaw in action") 
    def pitch(self):
        if self.pitch_task == None:
            self.pitch_task = cotask.Task(pitch_control,name = "pitch",priority=3, period=10,
                        profile=True, trace=False, shares=None)
            self.task_list.append(self.pitch_task)
            
        else:
            print("Tried to yaw while current yaw in action")    

    def cam(self):
        if self.fake_task == None:
            self.fake_task = cotask.Task(real_camera,name = "real",priority=1, period=250,
                        profile=True, trace=False, shares=[self.yaw_angle,self.targ])
            self.task_list.append(self.fake_task)
        else:
            print("something dumb haopened")
    def shoot(self):
        self.shoot = cotask.Task(shoot_fun,name = "shoot",priority=2, period=50,
                        profile=True, trace=False, shares=self.targ)
        self.task_list.append(self.shoot)

    def run_action(self):
        while True:
            try:
                self.task_list.pri_sched()
            except KeyboardInterrupt:
                break
        

    