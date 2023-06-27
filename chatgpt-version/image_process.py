from PIL import Image, ImageOps
import os

def crop_and_equalize_image(input_image_path, output_image_path):
    """
    Crop the bottom 100 pixels off an image and equalize its histogram.
    """
    image = Image.open(input_image_path)
    width, height = image.size
    new_height = height - 100  # subtract 100 pixels from the original height
    image = image.crop((0, 0, width, new_height))  # parameters are left, upper, right, lower
    
    # equalize the histogram
    image = ImageOps.equalize(image)
    
    image.save(output_image_path)


def process_images(input_dir, output_dir):
    """
    Process all images in a directory.
    """
    # Make the output directory if it doesn't already exist
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".jpg", ".png")): 
            input_image_path = os.path.join(input_dir, filename)
            output_image_path = os.path.join(output_dir, filename)
            crop_and_equalize_image(input_image_path, output_image_path)
            print(f'Processed {filename}')
        else:
            continue

input_dir = "../example_images"
output_dir = "../cropped_images"

process_images(input_dir, output_dir)

