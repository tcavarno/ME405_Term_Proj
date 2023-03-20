"""!
@file turrettest.py
file the contains the code to init and run the turret for
a match

@author Miloh Padgett, Tristan Cavarno, Jon Abraham
@date 1-Mar-2023 Original File
"""
import pyb
import TurretDriver
from gc import collect
import neopixel
import machine



def main():
   """!
   Init a turret and start a match after a button press
   @param NA
   """
   #init the turret and turn off some pins
   turret = TurretDriver.TurretDriver()
   in1 = pyb.Pin(pyb.Pin.board.PA8,pyb.Pin.OUT_PP)
   in3 = pyb.Pin(pyb.Pin.board.PA6,pyb.Pin.OUT_PP)
   in3.low()
   in1.low()

   #button press code
   but = pyb.Pin(pyb.Pin.board.PC13,pyb.Pin.IN,pull=pyb.Pin.PULL_UP)
   turret.yaw_to(180)
   turret.pitch()
   turret.cam()
   turret.shoot()
   while(but.value() == 1):
      pass

   #start!
   print("starting")
   but = None
   collect()
   turret.run_action()
    

if __name__ == "__main__":
   main()