from array import array
import serial
from os import system

"""!
@file camera_viewer.py
This file handles receiving ascii_image() print statements. It also allows to 
lunix terminal clearing for easier visualization of camera data.

@author Miloh Padgett, Tristan Cavarno, Jon Abraham
@date 30-Jan-2023 Original File
"""

'''!
Width of a camera image
'''
WIDTH = 32

'''!
Height of a camera image
'''
HEIGHT = 24

'''!
Length of a one dimentional camera image array.
'''
SIZE = WIDTH*HEIGHT

#Send characters through USB and read output
def steptest():
    """!
    Send a start condition tothe board through serial, and print the recieved image string.
    @returns None
    """
    data = []
    #Open serial port
    with serial.Serial ('/dev/ttyACM0', 115200,timeout=6) as s_port:
           print(f"Starting")
           #Send Kp using UTF-8 encoding
           s_port.write("start\r".encode())
           byte_ = 1
           msg = ""
           byte_ = s_port.readline()
           # Read the data sent from the controller while valid data is buffered and split into lists
           while(byte_): 
                byte_ = s_port.readline()
                #Decode data into a string and print
                msg = byte_.decode()
                if(msg.strip() == "clear"):
                    system("clear")
                else:
                    print(byte_.decode(),end='')
                 



def main():
    steptest()

if __name__ == "__main__":
    main()
