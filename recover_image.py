import sys
from PIL import Image

desired_size = (2082,761)

for i in range(1,len(sys.argv)):
    filename = sys.argv[i]
    path, fmt = filename.split(".")
    im = Image.open(filename)

    f = im.resize(desired_size)
    f.save(f'{path}_filled.{fmt}')
    print(f"saved as {path}_filled.{fmt}")
