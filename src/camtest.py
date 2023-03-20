"""!
@file camtest.py
Test working with the camera outside the main control code 

@author Miloh Padgett, Tristan Cavarno, Jon Abraham
@date 5-Mar-2023 Original File
"""
import utime as time
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern
from mlx_cam import MLX_Cam
from image_processing import gaus_blur
from array import array
from gc import collect
from image_processing import HEIGHT,WIDTH,IMG_SIZE,dfs
import sys



def wait_for_start():
    """!
    Recursivly waits for the user to type start
    """
    inp = input("Please input start to continue: ")
    if( inp.strip() != "start"):
        wait_for_start()

def cam_stream():
    """!
    Open an i2c camera device and either
    1) Serve frames via print
    2) Test the dfs camera alrorithm and serve those
    frames for validation

    """
    
    i2c_bus = I2C(1)

    print("MXL90640 Easy(ish) Driver Test")

    # Select MLX90640 camera I2C address, normally 0x33, and check the bus
    i2c_address = 0x33
    scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
    print(f"I2C Scan: {scanhex}")

    # Create the camera object and set it up in default mode
    camera = MLX_Cam(i2c_bus)
    wait_for_start()
    collect()

    while True:
        try:    
            #Get a single frame and print it
            image = camera.get_image()
            camera.ascii_image_og(image)
            # Get and image and preform a dfs on blobs in the image.
            """biggest ={}
            image = camera.get_image()
            collect()
            arr = array('l')
            minny = min(image)
            scale = 255.0 / (max(image) - minny)
            for elm in image:
                arr.append(int((elm-minny)*scale))
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    blob = dfs(arr,x,y)
                    if(blob != None and len(blob) > len(biggest)):
                        biggest = blob
                    
            camera.ascii_image_dfs(image,biggest)
            avg = 0
            for key in biggest:
                avg += biggest[key].x
            print(avg//len(biggest))
            biggest = None
            blob = None
            collect()"""
            

        except KeyboardInterrupt:
            break

    print ("Done.")
if __name__ == "__main__":
    cam_stream()