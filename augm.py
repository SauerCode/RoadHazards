from PIL import Image, ImageDraw, ImageFilter
import os, random
from os import path
from pathlib import Path

# Add obstacle in road region.
# Note that rotate func adds alpha channel
# Point of insertion, for now, is the left bottom corner of the perimter box
# Reference size (natural size), for now, is the bottom placement in image
# Our working space is 1280px by 720px
# Cartesian space starting (0,0) on top left corner.
# The size is given by a 2-tuple (w,h).

sourceFolder = "data/source"
sourceMasksFolder = "data/source masks"
destinationFolder = "data/destination"
destinationMasksFolder = "data/destination masks"

scores = {
    "milk_crate_black.png": 39.38, 
    'car_bumper.png': 45.87,
    'car_mufler.png': 22.33,
    "wood_pallet.png": 59.96,
    "black_steel_pipe.png": 27.72,
    "galvanized_steel_pipe.png": 12.63
}


# Crop boundary (transparent channel)
def cropAlpha(img):
    if (img.mode != "RGBA"):
        return img
    alpha = img.getchannel("A")
    return img.crop(alpha.getbbox())


def rotateSource(source, angle):
    img = source.rotate(angle, expand=True)
    img = cropAlpha(img)
    return img

def openSource(filename):
    pathfile = path.join(sourceFolder, filename)
    src = Image.open(pathfile)
    return src


def openDestination(filename):
    filepath = path.join(destinationFolder, filename)
    dst = Image.open(filepath)
    return dst

def attemptSourceToDestination(sourceFilename, destinationFilename):

    source = openSource(sourceFilename)
    destination = openDestination(destinationFilename)

    rotation = generateRotation()
    originPoint = generateOriginPoint()

    relSizeOffBase = relativeSizeInBackgroundPercent(originPoint[1])

    relSizePerc = (sourceRelativeSizeBase(sourceFilename)*relSizeOffBase)/100
    print("Relative Size Final:", relSizePerc)

    # Apply transformaton on source
    source = transformSource(source, rotation, relSizePerc)

    # Determine the final insertion point, after performing transformation
    insertPt = convertOriginToInsertionPoint(originPoint, source)

    validInsert = isValidInsert(sourceFilename, source, rotation, relSizePerc, insertPt, destinationFilename)

    # if validInsert:
    final = insertSourceIntodestination(source, insertPt, destination)
    #     return final
    # else:
    return validInsert, final

def insertSourceIntodestination(source, point, destination):
    res = destination.copy()
    res.paste(source, point, source)
    return res

def replaceSuffixToPNG(filename):
    p = Path(filename)
    filename = p.with_suffix(".png")
    return filename

def isValidInsert(sourceFilename, source, rotation, relativeSize, insertPt, destinationFilename):
    sourceMask = getSourceMask(sourceFilename)
    sourceMask = transformSource(sourceMask, rotation, relativeSize)

    destinationMask = getDestinationMask(replaceSuffixToPNG(destinationFilename))


    x1,y1 = insertPt[0],insertPt[1]
    x2,y2 = insertPt[0]+sourceMask.width, insertPt[1]+sourceMask.height

    destinationMaskCropped = destinationMask.crop((x1,y1,x2,y2))

    percentInsideRoadRegion = sourceProportionInRegion(sourceMask, destinationMaskCropped)
    print(percentInsideRoadRegion)

    return (percentInsideRoadRegion>=50)

def sourceProportionInRegion(sourceMask, destinationMask):
    totPxObj =  totPxInters = 0
    blackTreshold = 2


    for y in range(sourceMask.height):
        for x in range(sourceMask.width):
            greyscale = sourceMask.getpixel((x, y))
            # print("Greyscale:", greyscalePx)
            rgb = destinationMask.getpixel((x, y))

            isObjectPx = greyscale>blackTreshold
            # print(destinationMask.mode)
            isRoadPx = sum(rgb)>0

            print(rgb)
            
            if isObjectPx:
                totPxObj+=1
            if isObjectPx and isRoadPx:
                totPxInters+=1
    

    print("Inter:", totPxInters)
    print("Inter:", totPxInters)
    return (totPxInters/totPxObj)*100

def getDestinationMask(filename):
    path = os.path.join(destinationMasksFolder,filename) 
    dst = Image.open(path)
    # We use image as RGB
    dst = dst.convert('RGB')
    return dst

def getSourceMask(filename):
    fp = path.join(sourceMasksFolder,filename)
    return Image.open(fp)


def sourceRelativeSizeBase(filename):

    return scores.get(filename)

def convertOriginToInsertionPoint(originPoint, source):
    x = originPoint[0]-int(source.width/2)
    y = originPoint[1]-source.height
    return (x,y)

def transformSource(source, rotation, sizePercent):
    source = rotateSource(source, rotation)
    sourceFin = resizeSource(source, sizePercent)
    return sourceFin

def resizeSource(source, sizePercent):

    newHeight = int (source.height*sizePercent/100) + 1
    newWidth = int(source.width*sizePercent/100) + 1
    print("Width and Height: ", newWidth, newHeight)
    return source.resize((newWidth, newHeight))

def generateRotation():
    # return random.randint(0, 360)
    return 0

def generateOriginPoint():
    # x = random.randrange(1280)
    # y = random.randrange(720)

    x,y = 400,300
    return (x,y)

def relativeSizeInBackgroundPercent(h):
    h1, h2 = 300, 596
    p1, p2 = 5, 100
    p = 100
    if h < h1:
        p = 1
    elif h1 <= h <= h2:
        p = translate(h, h1, h2, p1, p2)
    else:
        p = 100

    # print("p:",p)
    return p

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)



def insertSourceToDesination(sourceFilename, desinationFilename, number):
   
    for i in range(number):
        # n is excluded
        print(i, end=" ")



valid,res = attemptSourceToDestination("black_steel_pipe.png","bb9f498e-5ea84006.jpg")

res.save('data/edit/bb9f498e-5ea84006.jpg')
print("Valid: ", valid)









