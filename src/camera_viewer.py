from array import array
import serial
from os import system

"""!
@file camera_viewer.py


TODO: Create a function to set up serial communication with the board

TODO: Plot the step responses with properly labeled axes and a title

@author Miloh Padgett, Tristan Cavarno, Jon Abraham
@date 30-Jan-2023 Original File
"""
WIDTH = 32
HEIGHT = 24
SIZE = WIDTH*HEIGHT

def ascii_image( array, pixel="██", textcolor="0;180;0"):
    """!
    @brief   Show low-resolution camera data as shaded pixels on a text
                screen.
    @details The data is printed as a set of characters in columns for the
                number of rows in the camera's image size. This function is
                intended for testing an MLX90640 thermal infrared sensor.

                A pair of extended ACSII filled rectangles is used by default
                to show each pixel so that the aspect ratio of the display on
                screens isn't too smushed. Each pixel is colored using ANSI
                terminal escape codes which work in only some programs such as
                PuTTY.  If shown in simpler terminal programs such as the one
                used in Thonny, the display just shows a bunch of pixel
                symbols with no difference in shading (boring).

                A simple auto-brightness scaling is done, setting the lowest
                brightness of a filled block to 0 and the highest to 255. If
                there are bad pixels, this can reduce contrast in the rest of
                the image.

                After the printing is done, character color is reset to a
                default of medium-brightness green, or something else if
                chosen.
    @param   array An array of (self._width * self._height) pixel values
    @param   pixel Text which is shown for each pixel, default being a pair
                of extended-ASCII blocks (code 219)
    @param   textcolor The color to which printed text is reset when the
                image has been finished, as a string "<r>;<g>;<b>" with each
                letter representing the intensity of red, green, and blue from
                0 to 255
    """
    minny = min(array)
    scale = 255.0 / (max(array) - minny)
    for row in range(HEIGHT):
        for col in range(WIDTH):
            pix = int((array[row * WIDTH + (WIDTH - col - 1)]
                        - minny) * scale)
            if(pix <150):
                pix = 0
            print(f"\033[38;2;{pix};{pix};{pix}m{pixel}", end='')
                
        print(f"\033[38;2;{textcolor}m")


#Send characters through USB and read output
def steptest():
    """!
    Input a Kp value, send to the board through serial, and return the encoder data.
    @param Kp	String containing the desired Kp value and a carriage return
    @returns A list of lists for each encoder reading, each containing a Time and Position
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
