from pathlib import Path
from PIL import Image, ImageDraw
from library.imagefunctions import imageprocess

test_path = 'test_data'
output_path = 'output'

#Set raw path to test data for now
raw_path = test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")

# Print filepath we're working on and process filename
for filepath in imfiles:
    print(filepath)
    imageprocess(filepath, output_path)

