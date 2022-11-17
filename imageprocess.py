from pathlib import Path

test_path='test_data'

#Set raw path to test data for now
raw_path=test_path

# Generate Path objects
raw_path = Path.cwd().joinpath('test_data','images')
imfiles = raw_path.glob("*.JPG")

for filename in imfiles:
    print(filename)
