import numpy
import os
import sys
sys.path.append("..")
from util import loadPLY
import bounding_box
from PIL import Image
import math
import numpy as np
import scipy.signal

def sample_image(pc, bounding_box, density):
	#convert pc to normalized space
	pc[:, :3] -= bounding_box.center
	pc[:, 0] /= bounding_box.half_xyz[0]
	#do not normalize Y coordinate because we need to recover it later!
	pc[:, 2] /= bounding_box.half_xyz[2]

	#for every point, get its x,y, draw it on film
	sample_width = int(math.ceil(bounding_box.width * density)+1)
	sample_height = int(math.ceil(bounding_box.height * density)+1)
	sample_depth = int(math.ceil(bounding_box.depth * density)+1)
	
	#sample from zx plane
	zx_depth_image = np.ones((sample_depth, sample_width)) * bounding_box.half_xyz[1]
	zx_rgb_image = np.zeros((sample_depth, sample_width, 3), dtype=np.uint8)
	for point in pc:
		c_x = int(round(((point[0] + 1.0) * density * bounding_box.half_xyz[0])))
		c_y = int(round(((point[1] + 1.0) * density * bounding_box.half_xyz[1])))
		c_z = int(round(((point[2] + 1.0) * density * bounding_box.half_xyz[2])))
		if(point[1] < zx_depth_image[c_z, c_x]): #nearest point
			zx_depth_image[c_z, c_x] = point[1]
			zx_rgb_image[c_z, c_x] = point[3:6]

	return zx_rgb_image

IMSIZE = 256
for l in sorted(os.listdir('../input')):
	if l.endswith('_gt.ply'):
		T = l[:-7]
		GT = 'input/' + l
		INPUT = 'input/' + T + '_input.ply'
		HOLE_FILLING = 'baselines/Hole_filling/' + T + '_input_hole_filled.ply'
		MESHING = 'baselines/Mesh/' + T + '_input_mesh.ply'
		HYBRID = 'baselines/hybrid/' + T + '_input_hole_filled_mesh.ply'
		PLANE_FITTING = 'baselines/plane_fitting/' + T + '_plane_fitted.ply'
		INPAINT = 'baselines/inpainting/' + T + '_inpainted.ply'
#		PIX2PIX = 'point-cloud-orthographic-projection/' + T + '_output.ply'
		PIX2PIX = 'baselines/pix2pix/' + T + '_output.ply'
		montage = np.zeros((IMSIZE, 8*IMSIZE, 3), dtype=np.uint8)
		for i, TARGET in enumerate([INPUT, GT, HOLE_FILLING, MESHING, HYBRID, PLANE_FITTING, INPAINT, PIX2PIX]):
			# load pcd point cloud
			test_pc,_ = loadPLY('../%s' % TARGET)
			#flip z axis
			test_pc[:,2] = -test_pc[:,2]
			print('loaded point cloud %s'%TARGET, test_pc.shape)

			min_xyz = test_pc[:,:3].min(axis=0)
			max_xyz = test_pc[:,:3].max(axis=0)
			center = 0.5 * (min_xyz + max_xyz)
			half_xyz = 0.5 * (max_xyz - min_xyz) + 0.5
			density = 20.0

			bb = bounding_box.AABB(center=center, half_xyz=half_xyz)
			rgb_image = sample_image(test_pc, bb, density)
			rgb_image_filtered = np.zeros(rgb_image.shape, dtype=np.uint8)
			rgb_image_filtered[:,:,0] = scipy.signal.medfilt2d(rgb_image[:,:,0], 3).astype(np.uint8)
			rgb_image_filtered[:,:,1] = scipy.signal.medfilt2d(rgb_image[:,:,1], 3).astype(np.uint8)
			rgb_image_filtered[:,:,2] = scipy.signal.medfilt2d(rgb_image[:,:,2], 3).astype(np.uint8)
			rgb_image_resized = scipy.misc.imresize(rgb_image_filtered, (IMSIZE,IMSIZE), interp='nearest')
			montage[:, i*IMSIZE:(i+1)*IMSIZE, :] = rgb_image_resized
		im = Image.fromarray(montage)
		im.save("thumbnails/%s.png" % T)

