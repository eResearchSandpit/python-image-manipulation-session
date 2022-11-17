### Download metadata

Get azcopy which we'll use to get a subset of the data

https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10

(use cliget)

We can use azcopy to get the files, they are all in a huge single directory, we can list it (it'll take forever) with
```
./azcopy list https://lilablobssc.blob.core.windows.net/wellington-unzipped/images > metadata/filelist.txt
```

This takes about 5 min to run, so I've put it up on github for us

We can get a subset of the metadata
```bash
cd metadata
cat filelist.txt | head -n 100 | cut -d ' ' -f 2 | cut -d ';' -f 1 > filesubset.txt
```

To download the data, lets try get just one file, let's choose the first one

```bash
cd ..
head metadata/filesubset.txt
#Returns
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
Download a couple of files to have a look
```bash
./azcopy cp "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/010116002950005as381.JPG" test_data/

./azcopy cp "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/010116002950005as382.JPG" test_data/
```

#### Quick aside

Generate an image diff to help us see what's happening using imagemagick

```bash
 compare -fuzz 10% 010116002950005as381.JPG 010116002950005as382.JPG -compose src diff.png
```

## Download a 100 images to test with

To test, lets download a subset of the images.  To download multiple images, we could do it in a loop, dowloading one file at a time.  Beause of some of the way that azcopy works, this doesn't really work as expected and it'll be slow. Looking at the azcopy docs a way to download multiple files is too feed them as a list of files separarated by a `;`

To test
```bash
./azcopy cp "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/" test_data/ --include-path '010116002950005as381.JPG;010116002950005as382.JPG;010116002952005as383.JPG;010116004822024b7481.JPG'
```

That seems to work, but I'm scared of downloading 100 files to the wrong place, so lets just get a subset.
```bash
head metadata/filesubset.txt > metadata/tinysubset.txt #get 5 lines
cat metadata/tinysubset.txt
```

To join the lines together into a list separated by `;` we can use the linux shell tool called `paste` - there are a lot of ways to do this, from a shell script with a loop, `sed`, `awk` or writing some python.

```bash
paste -sd ';' metadata/tinysubset.txt
```

Lets create a small shell script to do this and download the files, this helps us keep a record of what we did.

```bash
#!/bin/bash

imagenames=$(paste -sd ';' metadata/tinysubset.txt)  # assign output of command to variable, could also use backtics

echo "files to be downloaded:"
echo $imagenames

#download
./azcopy cp \
    "https://lilablobssc.blob.core.windows.net/wellington-unzipped/images/" \
    test_data/ \
    --include-path "$imagenames"

```

Testing that seems to work, so let's do the 100 file download by changing the line `imagenames=$(paste -sd ';' metadata/tinysubset.txt)` to `imagenames=$(paste -sd ';' metadata/filesubset.txt)`

This will take about 2 min

### Version control

We've done a bunch of work so far. Lets add what we have to git.

```bash
git init
git add metadata
git commit -m "Added a pair of files with lists of the image files we want to work with"
git remote add origin git@github.com:eResearchSandpit/python-image-manipulation-session.git
git push --set-upstream origin main
```

We don't want to version control images, so let's add a `.gitignore` file so we can avoid accidentally version controlling a bunch of images.

```
nano .gitignore

#add this line
test_data/
```

Add the gitigore file to our repo.
```bash
git add .gitignore
git commit -m "Added .gitignore file, ignoring test_data/"
git push
```

## Making changes to images, finally some python!

We'll be using a python libary called `pillow` to manipulate images - this is library that is derived from an older library called `PIL` or Python Image Library.  It's no longer maintained, so use pillow instead.

We will be re generating our list of image files in python - strictly we don't need to do this, we already have a list of the filenames!  However, you might not in your application so to keep things general, we'll regenerate the filelist in python

### venv, conda, anaconda oh my!

If you work on many python projects, you'l have come across python venvs and/or conda. You can think of these as ways to have a python "install" or more accuratly an enviroment for each project.  There are a lot of reasons to use a venv or conda such as keeping different versions of a libary separate. My favorite reason is reproducability. 

If you move to another computer, HPC or have a collaborator working with you, what versions of what libaries do you need to install to make your project work?  Venvs help solve this problem with requirements files.  Conda can also save it's enviroment.  We'll be using venvs and pip in this examples as it's very light weight and has less to install. Conda is great too though.

Let's start by creating a venv, assuming you have a fairly new version of python 3 installed everything you need should already be included.

```
python3 -m venv env #greate a venv called env

ls # see the env folder
```

To actually use the venv you need some arcana, it's not too bad and eventually you just remember it.  There are helper scripts you can use to simplify this, conda is also a little simpler.  We'll do it the generic lightweight way 

```bash=
source env/bin/activate
```

Note the leading `env` on your prompt.

Install pillow
```
pip install pillow
```

We can now generate a python requirements file
```
pip freeze > requirements.txt
```

Add the requirements file to git
```
git add requirements.txt 
git commit -m "Added requirements file with pillow"
```

### Filelist with python *pathlib*

There are a lot of ways to generate a list of files in python, we're going to use `pathlib` and glob.  Note that pathlib was only introduced in python 3.4 - but most folks python version should be newer than that.

We'll build up our python program iteratively.  I find it hand to have a REPL (Read-Eval-Print-Loop) to do this.  I'll use Ipython on the command line - there are other options like doing this in a jupyter notebook or spyder etc.

Install ipython
```bash
pip install ipython
```

We'll start with importing pathlib.  In ipython
```python
from pathlib import Path

Path.cwd().joinpath('test_data')

#see output and adapt, lets sstore as a variable
our_path = Path.cwd().joinpath('test_data')

#lets try get all the files
imfiles = our_path.glob("*")

#Just an generator objects, lets iterate though it
for f in imfiles:
    print(f)
    
#ah just a single output, the image directory!  we need to add that to our path
our_path = Path.cwd().joinpath('test_data/images')
#or
our_path = Path.cwd().joinpath('test_data','images') # a bit more general


#Repeat the for loop
imfiles = our_path.glob("*")

#Just an generator objects, lets iterate though it
for f in imfiles:
    print(f)

    
#what if we had non image files?  Lets make it specific to the JPG files we downloaded
imfiles = our_path.glob("*.JPG")
imfiles = our_path.rglob("*.JPG")  # if we had subdirectories (recursive glob)

```

That's a bit untidy, lets put it into a script.



`imageprocess.py`
```python
from pathlib import Path

test_path='test_data'

#Set raw path to test data for now
raw_path=test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")

for filename in imfiles:
    print(filename)
```

run our script

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

### Lets edit an image

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

Now we can optionally cover the vendor brand - probably the best way to prep the images for ML would be to crop away the entire lower secton including the brand, but we'll show how to draw on images as it could be useful

In the same ipython session
```python
from PIL import Image, ImageDraw #need ImageDraw


#get new image width and height, this'll make the math easier
width, height = im1.size

#prepare im2 
im2 = ImageDraw.Draw(im1)

#google drawing rectangles with pillow
#rectangle takes coordinates like so
#[(x0, y0), (x1, y1)]


#Estimate size of rectangle
w, h = 190, 90

x0 = 0
y0 = height - h
x1 = w
y1 = height


#[(x0, y0), (x1, y1)]
shape = [(x0, y0), (x1, y1)]

im2.rectangle(shape, fill ="black",outline ="green")
im2.show()  #Doesn't work!  It's not a proper image, it's really rectangle

im1.show() # we need slightly more


#Estimate size of rectangle
w, h = 200, 100

x0 = 0
y0 = height - h
x1 = w
y1 = height


#[(x0, y0), (x1, y1)]
shape = [(x0, y0), (x1, y1)]

im2.rectangle(shape, fill ="black",outline ="black")

im1.show() 

#saved the image
im1.save('test.png')
ls
rm test.png
```

That seemed to work, let's put it into the script

`imageprocess.py`
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

# Print filename we're working on and process filename
for filepath in imfiles:
    print(filepath)
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
    # current filename is
    # PosixPath('/home/andre/Documents/talks/python_image_manip/test_data/images/010116060142029a3301.JPG')
    #im1.save(filename)
```

Ah, we've reached a problem!  How do we save without overwiting our original files?

Experiment in ipython!

```python
from pathlib import Path

test_path = 'test_data'
output_path = 'output'

#Set raw path to test data for now
raw_path = test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")

filepath = next(imfiles)

#try tab autocomplete
filepath.name

#Now just join to the output
outpath = Path.cwd().joinpath(output_path,filepath.name)
```

Let's add that to the end of out script and test it.

`imageprocess.py`
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

# Print filepath we're working on and process filename
for filepath in imfiles:
    print(filepath)
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

There will likely be errors and typos causing problems when this is run, 

```bash
python imageprocess.py
```

Once that's working, let's version control it. That way if we break it in future, we have a working version

```bash
git status
git add imageprocess.py
git commit -m "Yay! A minimal working version - at least on test data" 
git push
```

### Run time woes

Great job!  That did seem to take a while to run, so lets time it
```bash
time python imageprocess.py
#returns
3.24s user 0.14s system 99% cpu 3.381 total
```

On my computer, that takes about 3.24 seconds to do 100 images.

Let's double check how many images we need to process.  `wc` is a shell command which can count lines (it stands for word count)
```bash
wc -l < metadata/filelist.txt

#returns
270450
```

Hmm, lets use ipython as a calculator
```python
time_per_im = 3.24/100
total_images = 270450
runtime = total_images * time_per_im
runtime

#in hours
runtime/3600

#returns
2.4340500000000005
```

Three hours isn't too bad! If you only need to run this once, I'd say you're basically done. However, what if you wanted to do this often and needed to go much faster?

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
