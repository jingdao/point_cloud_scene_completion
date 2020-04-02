import skimage.draw
import skimage.measure
import numpy
import sys
from tfrecord_lite import tf_record_iterator
import os
import matplotlib.pyplot as plt
from util import savePLY, saveVoxels

tfrecord_filename = sys.argv[1]
voxel_scale = float(sys.argv[2]) #0.047 or 0.094 or 0.188

it = tf_record_iterator(tfrecord_filename)
if sys.argv[1].startswith('vis'):
	foldername = os.path.dirname(tfrecord_filename)
else:
    foldername = '.'
n = next(it)
for k in ['input_sdf','target_df','prediction_df']:
    if k in n:
        A = n[k]
        s = n[k+'/dim']
        sdf = A.reshape(s).copy()
#        sdf = skimage.draw.ellipsoid(6,10,16,levelset=True)
        print('Loaded sdf',sdf.shape,sdf.min(),sdf.max())
        vertices, faces, normals, values = skimage.measure.marching_cubes_lewiner(sdf, 1)
        V = numpy.ones((len(vertices), 6)) * 255
        V[:,:3] = vertices * voxel_scale
        savePLY('%s/%d_%s.ply'%(foldername, int(round(voxel_scale,2)*100), k), V, faces)
        saveVoxels('%s/voxel_%d_%s.ply'%(foldername, int(round(voxel_scale,2)*100), k), sdf, voxel_scale, cross_section=True)

