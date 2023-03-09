
import utime as time
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern
from mlx_cam import MLX_Cam

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
            begintime = time.ticks_ms()
            image = camera.get_image().buf
            # Can show image.v_ir, image.alpha, or image.buf; image.v_ir best?
            # Display pixellated grayscale or numbers in CSV format; the CSV
            # could also be written to a file. Spreadsheets, Matlab(tm), or
            # CPython can read CSV and make a decent false-color heat plot.
            camera.ascii_image(image)
            print("clear")

        except KeyboardInterrupt:
            break

    print ("Done.")
if __name__ == "__main__":
    cam_stream()