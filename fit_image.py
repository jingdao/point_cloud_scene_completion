import sys
from PIL import Image, ImageOps

preserve_aspect_ratio = True
desired_size = 512

for i in range(1,len(sys.argv)):
    filename = sys.argv[i]
    path, fmt = filename.split(".")
    im = Image.open(filename)
    if preserve_aspect_ratio == False:
        im.resize((desired_size,desired_size))
        im.save(f'{path}_resized.{fmt}')
        print(f"saved as {path}_resized.{fmt}")
    else:
        im.thumbnail((desired_size,desired_size), Image.ANTIALIAS)
        reduced_size = im.size
        d_w = desired_size - reduced_size[0]
        d_h = desired_size - reduced_size[1]
        padding = (d_w//2, d_h//2, d_w-(d_w//2), d_h-(d_h//2))
        new_im = ImageOps.expand(im, padding)
        new_im.save(f'{path}_resized_aspect.{fmt}')
        print(f"saved as {path}_resized_aspect.{fmt}")