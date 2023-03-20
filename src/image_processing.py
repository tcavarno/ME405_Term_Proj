"""!
@file image_processing.py
This file contains any visual proccessing alorithms needed 

@author Miloh Padgett, Tristan Cavarno, Jon Abraham
@date 5-Mar-2023 Original File
"""
from array import array
import random
from gc import collect

"""!
a 2d gaussian kernel in a 1d array.
"""
gaus_kern_5x5 = array('f',[0,.01,.01,.01,0,.01,.05,.11,.05,.01,.01,.11,.25,.11,.01,.01,.05,.11,.05,.01,0,.01,.01,.01,0])

"""!
Defualt Width of an image frame
"""
WIDTH = 32

"""!
Default Heght of an image frame
"""
HEIGHT = 24

"""!
Start width index of a downsized image for 
faster processing
"""
WIDTH_ST = 6

"""!
End width index of a downsized image for 
faster processing
"""
WIDTH_END = 32-6

"""!
Total width of a downsized image for 
faster processing
"""
WIDTH_N = WIDTH_END -WIDTH_ST

"""!
Start heigh index of a downsized image for 
faster processing
"""
HEIGHT_ST = 0

"""!
End height index of a downsized image for 
faster processing
"""
HEIGHT_END = 24-8

"""!
Total Height of a downsized image for 
faster processing
"""
HEIGHT_N = HEIGHT_END-HEIGHT_ST

"""!
Length of a 1d image array after downsizing
"""
IMG_SIZE_N = (WIDTH_N)*(HEIGHT_N)

"""!
Default 1d array size for an image
"""
IMG_SIZE = WIDTH*HEIGHT

"""!
Cut off threshhold for pixel intensity 
"""
THRESHHOLD = 175

class img_pnt:
    """!
    Simple point class for saving a location in the
    image plane.
    """
    def __init__(self,x,y):
        """!
        @param x 		position in the x direction of a pixel
        @param y		position in the y direction of a pixel
        """
        self.x = x
        self.y = y

    def __eq__(self, other):
        """!
        Defines equivilence for a point
        @param self one point for comparison
        @param other a second point for comparision
        """
        return self.x == other.x and self.y == other.y
    def __repr__(self) -> str:
        return f"({self.x},{self.y})"

    

def ascii_image(array,biggest, pixel="██", textcolor="0;180;0"):
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
        @param   biggest a dictionary of all the pixels in the biggest blob in an image
        @param   pixel Text which is shown for each pixel, default being a pair
                 of extended-ASCII blocks (code 219)
        @param   textcolor The color to which printed text is reset when the
                 image has been finished, as a string "<r>;<g>;<b>" with each
                 letter representing the intensity of red, green, and blue from
                 0 to 255
        """
        minny = min(array)
        s = []
        for row in range(HEIGHT):
            for col in range(WIDTH):
                pix = int((array[row * WIDTH + (col)]))
                hashval = str(col)+","+str(row)
                if(not hashval in biggest):
                    pix = 0
                print(f"\033[38;2;{pix};{pix};{pix}m{pixel}", end='')

            print(f"\033[38;2;{textcolor}m")

def apply_kernel_avg(img,middle):
    """!
    apply a gaussian kernel to a given pixel

    @param img an array of WIDTH and HEIGH
    @param middle a pixel that will be corrisond to the center of the kernel
    """
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
    return int(avg)
        



def gaus_blur(img):
    """!
    Iterate across and and 'img' applying the gaussuan kernelto blur the image
    @param img the image to blur in a 1d array
    """
    collect()
    a = array('Q')
    for i in range(IMG_SIZE):
        a.append(apply_kernel_avg(img,i))
    return a

def can_visit(img,x,y):
    """!
    A helper function to determine if a point is able to be visited
    @param img a 1d array of size IMAGE_SIZE_N
    @param x the x value of a pixel to check visitation 
    @param y the y value of a pixel to check visitation 
    """
    #convert to 1d array index
    img_index = (WIDTH_N)*y+x

    #make sure we can actually index on the array
    if img_index < IMG_SIZE_N:
        #check for previous visitation
        value = img[img_index] != -1
        #check for pixel intensity
        threshval = img[img_index] >= THRESHHOLD
    else:
        value = False
        threshval = False
    #check to make sure the point is within the image
    ret =  (threshval and x >= WIDTH_ST and y >= HEIGHT_ST and x < WIDTH_END and y < WIDTH_END and value)
    return ret
    


def dfs(img,x,y):
    """!
    Perform a singular depth first explore on an image starting at
    x and y
    @param img a 1d array corrisponding to an image of size IMAGE_SIZE_N
    @param x the x value in the image to start at
    @param y the y value in the image to start at
    """

    #init some vars
    current_blob = {}
    stack = []
    #start on the current value
    stack.append(img_pnt(x,y))
            
    #iterate across elements in fifo order
    while len(stack) != 0:
        #get the next point to try and visit

        current = stack.pop()
        #get a key to check for in the dictionary
        hashval = str(current.x)+","+str(current.y)

        #convert a two dimentional point into a single 1d index
        img_index = (WIDTH_N)*current.y+current.x
        
        #check the validity of the point
        if(can_visit(img,current.x,current.y)):

            #to prevent crashes we will stop on a blob >50 and shoot at it.
            if(len(current_blob) >=50):
                return current_blob 
            #add this blob to a visit dict
            current_blob[hashval] = img_pnt(current.x,current.y)
            
            #check to see if we can traverse + or - in the x and y directions
            pt = img_pnt(current.x-1,current.y)
            if can_visit(img,pt.x,pt.y) :
                stack.append(pt)

            pt = img_pnt(current.x+1,current.y)
            if can_visit(img,pt.x,pt.y) :
                stack.append(pt)
            pt = img_pnt(current.x,current.y-1)
            if can_visit(img,pt.x,pt.y):
                stack.append(pt)

            pt = img_pnt(current.x,current.y+1)
            if can_visit(img,pt.x,pt.y):
                stack.append(pt)
        #visit the index
        img[img_index] = -1
    return current_blob

if __name__ == "__main__":
    b = [255 if i//WIDTH != 5 and i %WIDTH !=5 else 0 for i in range(IMG_SIZE)]
    s = {}
    for x in range(WIDTH):
        for y in range(HEIGHT):
            hashval = str(x)+","+str(y)
            s[hashval] = True

    ascii_image(b,s)
    print("_-------------__")
    c = b.copy()
    biggest = {}
    for x in range(WIDTH):
        for y in range(HEIGHT):
            img_index = WIDTH*y+x
            blob = dfs(b,x,y)
            if(len(blob) > 0):
                print(f"length of blob {len(blob)}")

                ascii_image(c,blob)

            if(blob != None and len(blob) > len(biggest)):
                biggest = blob
        
        #print(f"size is {len(biggest)}")
    ascii_image(c,biggest)
        
    
