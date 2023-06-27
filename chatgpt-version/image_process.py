from PIL import Image
import os

def crop_image(input_image_path, output_image_path):
    """
    Crop the bottom 100 pixels off an image.
    """
    image = Image.open(input_image_path)
    width, height = image.size
    new_height = height - 100  # subtract 100 pixels from the original height
    image = image.crop((0, 0, width, new_height))  # parameters are left, upper, right, lower
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
            crop_image(input_image_path, output_image_path)
            print(f'Processed {filename}')
        else:
            continue


input_dir = "/nfs/scratch/geldenan/WellingtonCameraTraps/example_images"
output_dir = "/nfs/scratch/geldenan/WellingtonCameraTraps/cropped_images"

process_images(input_dir, output_dir)

