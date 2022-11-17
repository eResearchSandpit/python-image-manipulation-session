from pathlib import Path
from PIL import Image, ImageDraw

def imageprocess(filepath, output_path):
    """Prepare image to be suitable for MachineLearning

    Takes image at filepath and crops the vendor info bar off 
    the bottom. It also blocks out the vendor logo in the lower
    left corner.

    Keyword arguments:
    filepath -- the path to the image
    output_path -- the path the modified image is saved to
    """
    im = Image.open(filepath)

    #Store the width and height
    width, height = im.size

    # Setting the points for cropped image
    left = 0
    top = 0
    right = width
    bottom = height-100

    #crop the bottom off the image
    im_cropped = im.crop((left, top, right, bottom))

    #get new image width and height, this'll make the math easier
    width, height = im_cropped.size

    #Prepare rectangle
    draw = ImageDraw.Draw(im_cropped)

    #Size of rectangle
    w, h = 200, 100

    x0 = 0
    y0 = height - h
    x1 = w
    y1 = height    

    shape = [(x0, y0), (x1, y1)]
    draw.rectangle(shape, fill ="black",outline ="black")

    #how will we save without overwriting?
    # current filepath is
    # PosixPath('/home/andre/Documents/talks/python_image_manip/test_data/images/010116060142029a3301.JPG')
    #im1.save(filename)

    outpath = Path.cwd().joinpath(output_path,filepath.name)

    im_cropped.save(outpath)