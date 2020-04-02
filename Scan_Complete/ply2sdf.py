import skimage.measure
import numpy
from util import loadPLY, savePLY, saveVoxels
import sys
import tensorflow as tf

if len(sys.argv) < 3:
    print('Usage: python ply2sdf.py input.ply output.tfrecords')
    sys.exit(1)

V,_ = loadPLY(sys.argv[1])
voxel_scale = 0.188
#voxel_scale = 0.047
offset = V[:,:3].min(axis=0)
V[:,:3] -= offset
#voxellize
voxel_array = numpy.array(list(set([tuple(t) for t in (V[:,:3] / voxel_scale).astype(int)])))
bbox = voxel_array.max(axis=0) - voxel_array.min(axis=0) + 2
voxels = numpy.ones(bbox) * 1.5
voxels[voxel_array[:,0], voxel_array[:,1], voxel_array[:,2]] = 0.5
print('voxels',voxels.shape)

with tf.python_io.TFRecordWriter(sys.argv[2]) as writer:
    target_sem = numpy.zeros(numpy.prod(voxels.shape), dtype=numpy.uint8).flatten().tobytes()
    print(target_sem)
    out_feature = {
        'target_sem': tf.train.Feature(bytes_list=tf.train.BytesList(value=[target_sem])),
        'input_sdf/dim': tf.train.Feature(int64_list=tf.train.Int64List(value=voxels.shape)),
        'input_sdf': tf.train.Feature(float_list=tf.train.FloatList(value=voxels.flatten().tolist())),
        'target_df/dim': tf.train.Feature(int64_list=tf.train.Int64List(value=voxels.shape)),
        'target_df': tf.train.Feature(float_list=tf.train.FloatList(value=voxels.flatten().tolist()))
    }
    example = tf.train.Example(features=tf.train.Features(feature=out_feature))
    writer.write(example.SerializeToString())
    print('Saved to %s'%sys.argv[2])

saveVoxels('/home/jd/Desktop/voxels.ply', voxels, voxel_scale, offset)
vertices, faces, normals, values = skimage.measure.marching_cubes_lewiner(voxels, 1)
V = numpy.zeros((len(vertices), 6)) * 255
V[:,:3] = vertices * voxel_scale
V[:,:3] += offset
savePLY('/home/jd/Desktop/marching_cubes.ply', V, faces)

sys.exit(1)

import mesh_to_sdf
import trimesh
import matplotlib.pyplot as plt
voxels = mesh_to_sdf.mesh_to_voxels(mesh, 100, pad=False)
print('voxels',voxels.shape,voxels.min(),voxels.max())

vertices, faces, normals, values = skimage.measure.marching_cubes_lewiner(voxels, 0)
V = np.zeros((len(vertices), 6)) * 255
V[:,:3] = vertices * voxel_scale
savePLY('/home/jd/Desktop/voxels.ply', V, faces)
voxels[voxels<0] = 0
voxels_scaled = (voxels - voxels.min()) / (voxels.max() - voxels.min())
colors = plt.get_cmap('jet')(voxels_scaled.flatten())[:,:3]

output = np.zeros((np.prod(voxels.shape), 6))
output[:,3:6] = colors * 255
n = 0
for i in range(voxels.shape[0]):
    for j in range(voxels.shape[1]):
        for k in range(voxels.shape[2]):
            if voxels[i,j,k]==0:
                output[n,:2] = 0
            else:
                output[n,0] = i 
                output[n,1] = j 
                output[n,2] = k 
            n += 1
savePLY('/home/jd/Desktop/voxels.ply',output)

points, sdf = mesh_to_sdf.sample_sdf_near_surface(mesh,
    number_of_points = 100000,
    surface_point_method='scan',
    sign_method='normal',
    scan_count=100,
    scan_resolution=400,
    sample_point_count=10000000,
    normal_sample_count=11,
    min_size=0)
print('points',points.shape,points.min(),points.max())
print('sdf',sdf.shape,sdf.min(),sdf.max())

cloud = np.zeros((len(points), 6))
sdf_scaled = (sdf - sdf.min()) / (sdf.max() - sdf.min())
colors = plt.get_cmap('jet')(sdf_scaled)[:,:3]
cloud[:,:3] = points
cloud[:,3:6] = colors * 255
savePLY('/home/jd/Desktop/wall_with_hole_sdf.ply',cloud)
