
# Python Image Manipulation with thousands of files
## Or, How to Get Computers to Do Tedious Things for You

## The Dataset

We will be utilizing images from camera traps to experiment with manipulating images on a small scale - hundreds of images, and on a grand scale (on your own time!) - hundreds of thousands of images. Here are the data and instructions for accessing it: https://lila.science/datasets/wellingtoncameratraps

### Downloading Metadata

To acquire a subset of the data, we'll use azcopy, which you can get from this link: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10

Azcopy allows us to download the files, which are stored in a single, massive directory. To list the files (it will take a while), use the command:

```
./azcopy list https://lilablobssc.blob.core.windows.net/wellington-unzipped/images > metadata/filelist.txt
```

This command takes about 5 minutes to execute, so I've already uploaded it to GitHub for us.

To access a subset of the metadata, use the following command:

```bash
cd metadata
cat filelist.txt | head -n 100 | cut -d ' ' -f 2 | cut -d ';' -f 1 > filesubset.txt
```

To download the data, let's attempt to download a single file. We'll choose the first one:

```bash
cd ..
head metadata/filesubset.txt
```
This will return:

```
010116002950005as381.JPG
010116002950005as382.JPG
010116002952005as383.JPG
010116004822024b7481.JPG
010116004822024b7482.JPG
010116004824024b7483.JPG
010116005220041as531.JPG
010116005222041as532.JPG
010116005222041as533.JPG
010116013338033a5751.JPG
```

Let's download a couple of files to examine:

```bash
./azcopy cp "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/010116002950005as381.JPG" test_data/
./azcopy cp "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/010116002950005as382.JPG" test_data/
```

## Downloading 100 Images for Testing

For testing, let's download a subset of the images. To download multiple images, we could loop through and download one file at a time. However, due to some of azcopy's functionality, this might not yield the expected result and could be slow. After looking into the azcopy documentation, it suggests that we can download multiple files by feeding them as a list of file paths separated by a `;`.

Test it with this command:

```bash
./azcopy cp "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/" test_data/ --include-path '010116002950005as381.JPG;010116002950005as382.JPG;010116002952005as383.JPG;010116004822024b7481.JPG'
```

This seems to work, but to avoid downloading 100 files to the incorrect location, let's first acquire a smaller subset:

Of course, my apologies for the interruption. Let's continue:

```bash
head metadata/filesubset.txt > metadata/tinysubset.txt #get 5 lines
cat metadata/tinysubset.txt
```

We can merge the lines into a list separated by `;` using the Linux shell tool `paste`. There are many ways to achieve this, such as using a shell script with a loop, `sed`, `awk`, or writing some Python.

```bash
paste -sd ';' metadata/tinysubset.txt
```

Now, let's create a small shell script to merge these lines and download the files. This will help us keep track of what we have done:

```bash
#!/bin/bash

imagenames=$(paste -sd ';' metadata/tinysubset.txt)  # assign output of command to variable, could also use backticks

echo "files to be downloaded:"
echo $imagenames

#download
./azcopy cp \
    "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/" \
    test_data/ \
    --include-path "$imagenames"
```

Testing this seems to work, so let's now download 100 files by changing the line `imagenames=$(paste -sd ';' metadata/tinysubset.txt)` to `imagenames=$(paste -sd ';' metadata/filesubset.txt)`

This download will take approximately 2 minutes.

### Version Control

We've done a significant amount of work up to this point. Let's save what we've achieved so far to Git.

```bash
git init
git add metadata
git commit -m "Added a pair of files with lists of the image files we want to work with"
git remote add origin git@github.com:eResearchSandpit/python-image-manipulation-session.git
git push --set-upstream origin main
```

We don't want to add images to version control, so let's create a `.gitignore` file to prevent accidentally tracking a multitude of images.

```bash
nano .gitignore
```

In the `.gitignore` file, add this line:

```
test_data/
```

Now, add the `.gitignore` file to our repository.

```bash
git add .gitignore
git commit -m "Added .gitignore file, ignoring test_data/"
git push
```

## Making Changes to Images - Finally, Some Python!

We'll use a Python library named `pillow` to manipulate images. This library is derived from an older one called `PIL` (Python Image Library), which is no longer maintained. Therefore, please use `pillow` instead.

We will be regenerating our list of image files in Python. Technically, we don't need to do this as we already have a list of the filenames. However, to keep things general (since you might not have a list of filenames in your specific application), we'll regenerate the file list in Python.

### venv, conda, anaconda, oh my!

If you work on multiple Python projects, you'll likely have encountered Python virtual environments (venvs) and/or conda. You can think of these as ways to have a separate Python "install" or more accurately, an environment for each project. There are numerous reasons to use a venv or conda such as keeping different versions of a library separate. However, my favorite reason is reproducibility.

If you move to another computer, High-Performance Computing (HPC) system, or have a collaborator working with you, you'll need to know which versions of which libraries are necessary to install to make your project work. Venvs help solve this problem with requirements files. Conda can also save its environment. For this example, we'll use venvs and pip as they are lightweight and require less to install. That being said, Conda is a great option too.

Let's start by creating a venv, assuming you have a fairly recent version of Python 3 installed, everything you need should already be included.

```bash
python3 -m venv env #create a venv called env

ls #see the env folder
```

To actually use the venv, you'll need to know some particular commands. These aren't too complicated and eventually, you'll remember them. There are helper scripts available to simplify this process, and Conda is also a bit simpler. We'll do it in a generic, lightweight way:

```bash
source env/bin/activate
```

Notice the leading `env` on your prompt.

Next, install Pillow:

```bash
pip install pillow
```

Now, let's generate a Python requirements file:

```bash
pip freeze > requirements.txt
```

Finally, add the requirements file to Git:

```bash
git add requirements.txt 
git commit -m "Added requirements file with pillow"
```

### File List with Python's *pathlib*

There are many ways to generate a list of files in Python. We're going to use `pathlib` and `glob`. Note that `pathlib` was only introduced in Python 3.4, but most Python versions in use today should be newer than that.

We'll build up our Python program iteratively. I find it useful to have a REPL (Read-Eval-Print-Loop) to do this. I'll use IPython on the command line, though other options like Jupyter Notebook or Spyder can be used.

First, install IPython:

```bash
pip install ipython
```

Now, let's start with importing pathlib:

```python
from pathlib import Path

Path.cwd().joinpath('test_data')

# see output and adapt, let's store it as a variable
our_path = Path.cwd().joinpath('test_data')

# let's try to get all the files
imfiles = our_path.glob("*")

# It's just a generator object, let's iterate through it
for f in imfiles:
    print(f)
    
# Ah, just a single output, the image directory! We need to add that to our path
our_path = Path.cwd().joinpath('test_data','images') 

# Repeat the for loop
imfiles = our_path.glob("*")

# Let's iterate through it again
for f in imfiles:
    print(f)

# What if we had non-image files? Let's make it specific to the JPG files we downloaded
imfiles = our_path.glob("*.JPG")
imfiles = our_path.rglob("*.JPG")  # if we had subdirectories (recursive glob)
```

That's a bit untidy, let's put it into a script:

`imageprocess.py`
```python
from pathlib import Path

test_path='test_data'

# Set raw path to test data for now
raw_path=test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")

for filename in imfiles:
    print(filename)
```

You can run our script with:

```bash
python imageprocess.py
```

#### Version control

We've made some good progress, let's version control what we have

```bash
git status

git add imageprocess.py
git commit -m "Made a start on image processing, printing out the files we need to work with"
git push
```

## Lets edit an image

Let's get a single image and crop the bottom of it.

in ipython we can copy and paste from our script

```python
from pathlib import Path

test_path='test_data'

#Set raw path to test data for now
raw_path=test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")
```

```python
imfile=next(imfiles) # google python generator to find out about next

from PIL import Image #we'll need pillow to load the image

im = Image.open(imfile)

#explore the im object with tab autocomplete in ipython
im.height
im.show()
im.size

#Store the width and height
width, height = im.size


# Setting the points for cropped image
left = 0
top = 0
right = width
bottom = height-50

im1 = im.crop((left, top, right, bottom))

im1.show()  #hmm, need more off the bottom
bottom = height-90
im1 = im.crop((left, top, right, bottom))
im1.show()  #hmm, tiny bit more needed

bottom = height-100
im1 = im.crop((left, top, right, bottom))
im1.show()
```

### Drawing on Images

The next step in our Python image processing journey is to cover the camera vendor's brand by drawing a rectangle. This is a useful technique if you're concerned about your machine learning model training on a logo. However, in such cases, it would be even better to trim the entire bottom of the image to avoid the model training on a black square.

Let's proceed with this in the same IPython session:

```python
from PIL import Image, ImageDraw  # Import ImageDraw

# Get the new image width and height to simplify the subsequent calculations
width, height = im1.size

# Prepare im2 
im2 = ImageDraw.Draw(im1)

# The 'rectangle' function takes coordinates as follows: [(x0, y0), (x1, y1)]

# Let's estimate the size of the rectangle we want to draw
w, h = 190, 90

# Establish the rectangle's coordinates
x0 = 0
y0 = height - h
x1 = w
y1 = height

shape = [(x0, y0), (x1, y1)]

# Draw a rectangle on the image with a green outline and a black fill
im2.rectangle(shape, fill="black", outline="green")

# Attempt to display the image
im2.show()  # This won't work as expected because it's not a proper image but rather a rectangle

im1.show()  # This is what we actually need to display

# Let's modify the size of the rectangle
w, h = 200, 100

# Update the coordinates
x0 = 0
y0 = height - h
x1 = w
y1 = height

shape = [(x0, y0), (x1, y1)]

# Draw another rectangle, this time with a black outline and black fill
im2.rectangle(shape, fill="black", outline="black")

im1.show()  # Now it works!

# Save the image
im1.save('test.png')
```

The above process works well. Let's incorporate it into our script, `imageprocess.py`:

```python
from pathlib import Path
from PIL import Image, ImageDraw

test_path = 'test_data'
output_path = 'output'

# Set raw_path to test data for now
raw_path = test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data', 'images')
imfiles = raw_path.glob("*.JPG")

# Print filename we're working on and process filename
for filepath in imfiles:
    print(filepath)
    im = Image.open(filepath)

    # Store the width and height
    width, height = im.size

    # Setting the points for cropped image
    left = 0
    top = 0
    right = width
    bottom = height - 100

    # Crop the bottom off the image
    im_cropped = im.crop((left, top, right, bottom))

    # Get new image width and height
    width, height = im_cropped.size

    # Prepare to draw rectangle
    draw = ImageDraw.Draw(im_cropped)

    # Size of rectangle
    w, h = 200, 100

    # Establish the coordinates
    x0 = 0
    y0 = height - h
    x1 = w
    y1 = height    

    shape = [(x0, y0), (x1, y1)]
    draw.rectangle(shape, fill="black", outline="black")

    # How can we save the new image without overwriting the original?
    # The current filename is, for example:
    #

 PosixPath('/home/andre/Documents/talks/python_image_manip/test_data/images/010116060142029a3301.JPG')
```

We have encountered a problem: we need to save the new images without overwriting the original ones. Let's figure out how to do this by experimenting in IPython:

```python
from pathlib import Path

test_path = 'test_data'
output_path = 'output'

# Set raw_path to test data for now
raw_path = test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data', 'images')
imfiles = raw_path.glob("*.JPG")

filepath = next(imfiles)

# Check the filename with tab autocomplete
filepath.name

# Now just join to the output
outpath = Path.cwd().joinpath(output_path, filepath.name)
```

Having learned how to save images in a new location without overwriting the originals, let's add this to our script and test it.

`imageprocess.py`:
```python
from pathlib import Path
from PIL import Image, ImageDraw

test_path = 'test_data'
output_path = 'output'

# Set raw_path to test data for now
raw_path = test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data', 'images')
imfiles = raw_path.glob("*.JPG")

# Print filepath we're working on and process filename
for filepath in imfiles:
    print(filepath)
    im = Image.open(filepath)

    # Store the width and height
    width, height = im.size

    # Setting the points for cropped image
    left = 0
    top = 0
    right = width
    bottom = height - 100

    # Crop the bottom off the image
    im_cropped = im.crop((left, top, right, bottom))

    # Get new image width and height
    width, height = im_cropped.size

    # Prepare to draw rectangle
    draw = ImageDraw.Draw(im_cropped)

    # Size of rectangle
    w, h = 200, 100

    # Establish the coordinates
    x0 = 0
    y0 = height - h
    x1 = w
    y1 = height    

    shape = [(x0, y0), (x1, y1)]
    draw.rectangle(shape, fill="black", outline="black")

    # Now let's save our new image in a new location without overwriting the original
    outpath = Path.cwd().joinpath(output_path, filepath.name)

    im_cropped.save(outpath)
```

There you go! Now we're able to manipulate our images without altering the original data.

### Handling Errors and Leveraging Version Control

As you begin to run your script with the command `python imageprocess.py`, you may encounter errors or typos. Debugging is an inherent part of coding, so don't be disheartened by these setbacks. Instead, use these issues as opportunities to learn and improve your code.

Once your script is working smoothly, it's a good practice to version control it. By doing this, you create a safety net; in case anything goes wrong in the future, you can always roll back to this working version. Git is a popular version control system and here's how you can use it:

```bash
git status
git add imageprocess.py
git commit -m "Yay! A minimal working version - at least on test data" 
git push
```

### Monitoring Run Time

Good work! However, you might notice that the script takes a while to process the images. To measure exactly how long it takes, use the `time` command:

```bash
time python imageprocess.py
```

On my machine, it takes about 3.24 seconds to process 100 images. This might vary on your machine, but let's use this as a reference.

Next, we need to ascertain the total number of images we need to process. We can use `wc` (word count) command in the shell to count the lines in `metadata/filelist.txt`, as each line corresponds to an image:

```bash
wc -l < metadata/filelist.txt
```

That returns 270450, which means we have 270450 images to process. We can use IPython as a calculator to work out the estimated run time:

```python
time_per_im = 3.24/100
total_images = 270450
runtime = total_images * time_per_im

# In hours
runtime/3600
```

This results in just under 3 hours, which is manageable if you're running the script occasionally. However, if you need to run the script frequently or on a much larger dataset, you might want to consider optimizing your script to reduce the run time. This could involve techniques like parallel processing, hardware acceleration, or even more efficient coding practices. Let's continue exploring these possibilities in the next section.

### Going wide, really wide - multiprocessing

Let's make a copy of our imageprocess code
```bash
cp imageprocess.py imageprocess_parallel.py
```

Lets have a look at python multiprocessing
in ipython
```python
mp.cpu_count()

#my computer returns 12, how many does yours?
```

Looking though the python multiprocessing docs and examples, we see the easiest way to do this is to have a fuction which we run in parallel.  Let's make part of our new `imageprocess_parallel.py` a funtion which takes a single filename, applies our changes and saves the output

`imageprocess_parallel.py`
```python
from pathlib import Path
from PIL import Image, ImageDraw

test_path = 'test_data'
output_path = 'output'

#Set raw path to test data for now
raw_path = test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")

def imageprocess(filepath):
    """Prepare image to be suitable for MachineLearning

    Takes image at filepath and crops the vendor info bar off 
    the bottom. It also blocks out the vendor logo in the lower
    left corner.

    Keyword arguments:
    filepath -- the path to the image
    output_path -- the path the modified image is saved to
    """
    output_path='output'
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

# Print filepath we're working on and process filename
for filepath in imfiles:
    print(filepath)
    imageprocess(filepath, output_path)
```

That works, but adding the fuction first looks a bit messy and makes the code a little hard to follow. Let's move that to another file to make look tidier

`imagefunctions.py`
```python
from pathlib import Path
from PIL import Image, ImageDraw

def imageprocess(filepath):
    """Prepare image to be suitable for MachineLearning

    Takes image at filepath and crops the vendor info bar off 
    the bottom. It also blocks out the vendor logo in the lower
    left corner.

    Keyword arguments:
    filepath -- the path to the image
    output_path -- the path the modified image is saved to
    """
    output_path = 'output'
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
```

Let's test
```bash
python imageprocess_parallel.py
```

Ok once that's working (expect some failures), version control it!

```bash
git status
git add imageprocess_parallel.py
git add imagefunctions.py
git commit -m "added a function for image processing and the skeleton of parallel image processing"
git push
```

Let's make it a touch tidier again
```bash
mkdir library
mv imagefunctions.py library/
```

Change the code to 
`imageprocess_parallel.py`
```python
from pathlib import Path
from PIL import Image, ImageDraw
from library.imagefunctions import imageprocess #note change!

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
```

Test it's working, then see what git makes of it
```bash
git status

#git thinks we deleted the file, then created a new one, let's add them both
git add imagefunctions.py #"add" the deleted file
git add library/imagefunctions.py
git status  #note how git figures out we renamed the file

git commit -m "Moved image functions to a library directory"
git add imageprocess_parallel.py 
git commit -m "Updated imageprocess_parallel to reflect moving the functions to their own library directory"
git push
```

#### Aside - cleaning up our old code

Could we use the function and library we created in our original imageprocess.py to tidy it up?

### Let's go wide


Python multiprocessing Pool - it's a collection of resources, a pool of resources if you will. In this case, a pool of "cpus"

There are some subtleties of apply vs map

```python
from pathlib import Path
from PIL import Image, ImageDraw
from library.imagefunctions import imageprocess
import multiprocessing as mp

test_path = 'test_data'
output_path = 'output'

#Set raw path to test data for now
raw_path = test_path

# Initialise multiprocessing pool
pool = mp.Pool(mp.cpu_count())

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")

#
for result in pool.map(imageprocess, imfiles):
    pass
```

`library/imagefunctions.py`
```python
from pathlib import Path
from PIL import Image, ImageDraw

def imageprocess(filepath):
    """Prepare image to be suitable for MachineLearning

    Takes image at filepath and crops the vendor info bar off 
    the bottom. It also blocks out the vendor logo in the lower
    left corner.

    Keyword arguments:
    filepath -- the path to the image
    output_path -- the path the modified image is saved to
    """
    output_path = 'output'
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
```
