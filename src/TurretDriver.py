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
    
    in1 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    in2 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    en = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    timer = pyb.Timer(2,freq=20000)
    
    #Create motor driver object
    motorB = MotorDriver.MotorDriver(en,in1,in2,timer,True)
    motorB.set_duty_cycle(0)
    
    #Create encoder driver object
    encoder = EncoderReader.EncoderReader(ch1,ch2,tim8)
    
    return (encoder,motorA,controller)

def init_pitch(angle):
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


def control_loop_one(encoder: EncoderReader.EncoderReader,
                    motorA: MotorDriver.MotorDriver,
                    controller: ClosedLoopController.PController):
    """!
    This function contains a motor control loop which reads encoder ticks,
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

def yaw_control(shares: task_share.Share):
    """!
    Task which initializes encoder, motor, and controller objects,
    and then feeds those to the close loop function.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    my_share = shares
    n = int(my_share.get())
    (encoder,motorA,controller) = init_yaw(n)

    while True:
        control_loop_one(encoder,motorA,controller)
        yield 0
    

class TurretDriver:
    """! 
    This class implments X, Y Axis Control an ME405 kit. 
    """
    def __init__(self):
        self.task_list = cotask.TaskList()
        self.yaw_task = None
        self.yaw_angle = task_share.Share('i', thread_protect=False, name="yaw_angle")


    def yaw_to(self,angle):
        if self.yaw_task == None:
            self.yaw_task = cotask.Task(yaw_control, name="Task_1", priority=1, period=10,
                        profile=True, trace=False, shares=self.yaw_angle)
            self.yaw_angle.put(int(angle*DEGREES_TO_TICKS))           
            self.task_list.append(self.yaw_task)
            
        else:
            print("Tried to yaw while current yaw in action")    
    
    def run_action(self):
        while True:
            try:
                self.task_list.pri_sched()
            except KeyboardInterrupt:
                break
        

    