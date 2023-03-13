
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
    Polls user to get input Kp value.
    """
    inp = input("Please input a value Kp (float): ")
    if( inp.strip() != "start"):
        wait_for_start()

def cam_stream():
    
    i2c_bus = I2C(1)

    print("MXL90640 Easy(ish) Driver Test")

    # Select MLX90640 camera I2C address, normally 0x33, and check the bus
    i2c_address = 0x33
    scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
    print(f"I2C Scan: {scanhex}")

    # Create the camera object and set it up in default mode
    camera = MLX_Cam(i2c_bus)
    wait_for_start()

    while True:
        try:
            # Get and image and see how long it takes to grab that image
            biggest ={}
            image = camera.get_image()
            arr = array('l')
            minny = min(image)
            scale = 255.0 / (max(image) - minny)
            for elm in image:
                arr.append(int((elm-minny)*scale))
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    img_index = WIDTH*y+x
                    blob = dfs(arr,x,y,scale,minny)
                    print(f"length of blob f{len(blob)}")
                    if(blob != None and len(blob) > len(biggest)):
                        biggest = blob
                    print()
            print(f"size is {len(biggest)}")
            camera.ascii_image(image,biggest)
            collect()

        except KeyboardInterrupt:
            break

    print ("Done.")
if __name__ == "__main__":
    cam_stream()