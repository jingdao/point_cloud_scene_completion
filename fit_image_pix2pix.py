import sys
from PIL import Image, ImageOps
import numpy as np

shrink = True if sys.argv[1]=='1' else False #True to shrink image to Pix2Pix scale (256x256), False to resize back to original scale
preserve_aspect_ratio = False

for i in range(2,len(sys.argv)):
    filename = sys.argv[i]
    if preserve_aspect_ratio == False:
        if shrink:
            desired_width = 256
            desired_height = 256
            im = Image.open(filename)
            im = im.resize((desired_width,desired_height), resample=Image.NEAREST)
            gt = Image.open(filename.replace('input', 'gt'))
            gt = gt.resize((desired_width,desired_height), resample=Image.NEAREST)
            im_concat = np.zeros((256, 512, 3), dtype=np.uint8)
            im_concat[:, :256, :] = np.array(im)
            im_concat[:, 256:, :] = np.array(gt)
            im = Image.fromarray(im_concat)
            path, fmt = filename.split(".")
            path = path.replace('_rgb', '')
            im.save(f'../pix2pix/test/{path}_merged.{fmt}')
            print(f'../pix2pix/test/{path}_merged.{fmt}')
        else:
            original_im = Image.open("%s_rgb.png" % filename)
            desired_width, desired_height = original_im.size
            im = Image.open('../pix2pix/results/images/%s_input_merged-outputs.png' % filename)
            im = im.resize((desired_width, desired_height))
            im.save("%s_filled.png" % filename)
            print("%s_filled.png" % filename)
    else:
        im = Image.open(filename)
        im.thumbnail((desired_height,desired_width), Image.ANTIALIAS)
        reduced_size = im.size
        d_w = desired_width - reduced_size[0]
        d_h = desired_height - reduced_size[1]
        padding = (d_w//2, d_h//2, d_w-(d_w//2), d_h-(d_h//2))
        new_im = ImageOps.expand(im, padding)
        new_im.save(f'{path}_resized_aspect.{fmt}')
        print(f"saved as {path}_resized_aspect.{fmt}")
