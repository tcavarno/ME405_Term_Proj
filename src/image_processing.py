from array import array
import random
gaus_kern_5x5 = array('f',[0,.01,.01,.01,0,.01,.05,.11,.05,.01,.01,.11,.25,.11,.01,.01,.05,.11,.05,.01,0,.01,.01,.01,0])
WIDTH = 32
HEIGHT = 24
SIZE = WIDTH*HEIGHT

def ascii_image(array, pixel="██", textcolor="0;180;0"):
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
        @param   array An array of (self._width * HEIGHT) pixel values
        @param   pixel Text which is shown for each pixel, default being a pair
                 of extended-ASCII blocks (code 219)
        @param   textcolor The color to which printed text is reset when the
                 image has been finished, as a string "<r>;<g>;<b>" with each
                 letter representing the intensity of red, green, and blue from
                 0 to 255
        """
        minny = min(array)
        for row in range(HEIGHT):
            for col in range(WIDTH):
                pix = int((array[row * WIDTH + (WIDTH - col - 1)]
                           - minny))
                print(f"\033[38;2;{pix};{pix};{pix}m{pixel}", end='')
            print(f"\033[38;2;{textcolor}m")

def apply_kernel_avg(img,middle):
    avg = 0
    for i in range(25):
        kern_row  = i // 5
        kern_col = i % 5
        img_row = middle // WIDTH
        img_col = middle % WIDTH
        translated_row = img_row + (kern_row - 2)
        translated_col = img_col + (kern_col - 2)
        img_index = WIDTH*translated_row + translated_col
        if((translated_row >=0 and translated_row <= HEIGHT) and (translated_col >= 0 and translated_col <= WIDTH) ):
            avg += gaus_kern_5x5[i]*img[24]
    return avg
        



def gaus_blur(img):
    a = []
    for i in range(SIZE):
        a.append(apply_kernel_avg(img,i))
    return a


if __name__ == "__main__":
    b = [random.randrange(0,255,1) for i in range(SIZE)]
    ascii_image(b)
    print()
    new = gaus_blur(b)
    ascii_image(new)
