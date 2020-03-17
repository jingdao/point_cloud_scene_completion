import skimage.draw
import skimage.measure
import numpy
import sys
from tfrecord_lite import tf_record_iterator
import os
import matplotlib.pyplot as plt

def savePLY(filename, vertices, faces):
    f = open(filename,'w')
    f.write("""ply
format ascii 1.0
element vertex %d
property float x
property float y
property float z
property uchar r
property uchar g
property uchar b
element face %d
property list uchar int vertex_index
end_header
""" % (len(vertices), len(faces)))
    for p in vertices:
        f.write("%f %f %f %d %d %d\n"%(p[0],p[1],p[2],p[3],p[4],p[5]))
    for p in faces:
        f.write("3 %d %d %d\n"%(p[0],p[1],p[2]))
    f.close()
    print('Saved to %s: (%d points %d faces)'%(filename, len(vertices), len(faces)))

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
        V = []
        faces = []
        for x in range(sdf.shape[0]):
            for y in range(sdf.shape[1]):
                for z in range(sdf.shape[2]):
                    if y==int(sdf.shape[1]/2):
                        if sdf[x,y,z] < 0:
                            V.append([x,y,z,255,0,0])
                        elif sdf[x,y,z] <= 1.0:
                            V.append([x,y,z,0,255,0])
                        else:
                            V.append([x,y,z,0,0,255])
        V = numpy.array(V, dtype=float)
        V[:,:3] *= voxel_scale
        savePLY('%s/voxel_%d_%s.ply'%(foldername, int(round(voxel_scale,2)*100), k), V, faces)

