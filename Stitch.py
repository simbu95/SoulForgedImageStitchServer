import PIL
from PIL import Image, ImageOps
import numpy as np
import sys, os
import shutil
import timeit
from numpy.lib.stride_tricks import as_strided

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

#Taken from https://stackoverflow.com/questions/17881489/faster-way-to-calculate-sum-of-squared-difference-between-an-image-m-n-and-a
def sumsqdiff3(input_image, template):
    window_size = template.shape
    y = as_strided(input_image,
                    shape=(input_image.shape[0] - window_size[0] + 1,
                           input_image.shape[1] - window_size[1] + 1,) +
                          window_size,
                    strides=input_image.strides * 2)
    ssd = np.einsum('ijkl,kl->ij', y, template)
    ssd *= - 2
    ssd += np.einsum('ijkl, ijkl->ij', y, y)
    ssd += np.einsum('ij, ij', template, template)

    return ssd

def checkOffset(input_image, baseImage, Offsetx, Offsety):
    pixelCount = 0
    differenceSum = 0
    for x in range(baseImage.shape[1]):
        for y in range(baseImage.shape[0]):
            if (x + Offsetx < baseImage.shape[1]) and (y + Offsety < baseImage.shape[0]) and (x + Offsetx > 0) and (y + Offsety > 0) and (x < input_image.shape[1]) and (y < input_image.shape[0]):
                if(input_image[y][x] != 0) and (input_image[y][x] != 255) and (baseImage[y + Offsety][x + Offsetx] != 0) and (baseImage[y + Offsety][x + Offsetx] != 255):
                    differenceSum += abs(input_image[y][x] - baseImage[y + Offsety][x + Offsetx])
                    pixelCount += 1
    if pixelCount < 100:
        return False
    averageDiff = differenceSum / pixelCount
    print(averageDiff)
    return averageDiff < 7

def resizeImage(orginalImage):
    grayImage = orginalImage.convert('L')
    npim = np.array(grayImage)
    if(npim[192,100] > 12  or npim[192,903] > 12):
        print("250x250")
        return orginalImage
    elif(npim[196,100] > 12  or npim[196,903] > 12):
        print("500x500")
        return orginalImage.resize((2000,2000),PIL.Image.BICUBIC)
    elif(npim[198,99] > 12 or npim[198,902] > 12):
        print("750x750")
        return orginalImage.resize((3000,3000),PIL.Image.BICUBIC)
    else:
        print("1000x1000")
        return orginalImage.resize((4000,4000),PIL.Image.BICUBIC)

def ImageOffset(inputFile, baseFile):
    offsets = [(.5,.5, 76),(.15,.5, 100),(.85,.5, 100),(.5,.15, 100),(.5,.85, 100),(.8,.8, 100),(.8,.2, 100),(.2,.8, 100),(.2,.2, 100)]
    baseIM = Image.open('jpgs/' + baseFile)
    baseGray = baseIM.convert('L')
    baseGray = resizeImage(baseGray)

    addIM = Image.open('jpgs/' + inputFile)
    addGray = addIM.convert('L')
    addGray = resizeImage(addGray)

    swap = False
    if(addGray.size[0] > baseGray.size[0]):
        swap = True
        hold = baseGray
        baseGray = addGray
        addGray = hold
        print("add image larger then base image, swapping")
    #Get image sizes
    widthAdd, heightAdd = addGray.size

    for offset in offsets:
        #Make a crop of the image to add, which will be used for the scan
        size = offset[2]
        left = int(widthAdd * offset[0] - size / 2)
        top = int(heightAdd * offset[1] - size / 2)
        convIM = addGray.crop((left, top, left + size, top + size))
        
        #Convert images to numpy arrays
        npCanvas = np.array(baseGray, np.intc)
        npim = np.array(convIM, np.intc)
        
        #And calculate sum of squared differences (SSD)
        start_time = timeit.default_timer()
        convResult = sumsqdiff3(npCanvas, npim)
        elapsed = timeit.default_timer() - start_time
        print(elapsed)

        #Find out the location where the minimum difference in pixel color was found.
        loc = np.unravel_index(convResult.argmin(), convResult.shape)
        
        print(convResult[loc[0],loc[1]])
        diffx = loc[1] - left
        diffy = loc[0] - top
        print(str(diffx) + "," + str(diffy))
        
        if(convResult[loc[0],loc[1]] < (12*12*size*size)):
            if(checkOffset(np.array(addGray, np.intc), npCanvas, diffx, diffy)):
                if(swap):
                    diffx = - diffx
                    diffy = - diffy
                return (True,(diffx.item(),diffy.item()))
    return (False,(0,0))