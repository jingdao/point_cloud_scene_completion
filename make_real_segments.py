import numpy
import sys
import glob
from util import loadPLY, savePLY 
import itertools

def downsample(cloud, resolution):
	voxel_coordinates = [tuple(p) for p in numpy.round((cloud[:,:3] / resolution)).astype(int)]
	voxel_set = set()
	downsampled_cloud = []
	for i in range(len(cloud)):
		if not voxel_coordinates[i] in voxel_set:
			voxel_set.add(voxel_coordinates[i])
			downsampled_cloud.append(cloud[i])
	return numpy.array(downsampled_cloud)

dirname = sys.argv[1] #directory containing separate raw scans
building_name = sys.argv[2]
output_dir = dirname+"/.."
scans = []
filelist = []
filelist.extend(glob.glob("%s/*.ply" % dirname))
filelist = sorted(filelist)
for s in filelist:
	pcd,_ = loadPLY(s)
	print(s,pcd.shape)
	scans.append(pcd)

for L in range(1,len(scans)):
	for l in itertools.combinations(range(len(scans)), L):
		stacked = numpy.vstack([scans[i] for i in l])
		stacked = downsample(stacked, 0.01)
		output_file = '%s/%s_real%s.ply' % (output_dir, building_name, ''.join([str(i) for i in l]))
		savePLY(output_file, stacked)

