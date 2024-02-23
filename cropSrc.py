from PIL import Image, ImageDraw, ImageFilter
import os

Alpha = "A"
horizon_pixel_height = 300
ground_pixel_height = 596
nat_size = [345,144]

# Crop boundary (transparent channel)
def cropAlpha(img):
    alpha = img.getchannel(Alpha)
    return img.crop(alpha.getbbox())

for filename in os.listdir('data/obstacle'):
    filepath = 'data/obstacle'+ '/' +filename
    img = Image.open(filepath)
    img = cropAlpha(img)
    img.save(filepath)

    














