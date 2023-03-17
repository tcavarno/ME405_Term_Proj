import pyb
import TurretDriver
from gc import collect
import neopixel
import machine


if __name__ == "__main__":
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
    print("starting")
    but = None
    collect()
    turret.run_action()
    