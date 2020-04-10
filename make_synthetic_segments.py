import numpy
import sys
from util import loadPLY, savePLY 
import os

gt_filename = sys.argv[1] #ground truth combined point cloud
building_name = sys.argv[2] #mason_east
pcd,_ = loadPLY(gt_filename)
print(gt_filename,pcd.shape)
minDims = pcd[:,:3].min(axis=0)
maxDims = pcd[:,:3].max(axis=0)

N = 20
for i in range(N):
	#create an interval between 10% and 90% of extent
	r1, r2 = numpy.random.random(2)*0.8 + 0.1
	x1 = minDims[0] + (maxDims[0] - minDims[0]) * min(r1,r2)
	x2 = minDims[0] + (maxDims[0] - minDims[0]) * max(r1,r2)
	r1, r2 = numpy.random.random(2)*0.8 + 0.1
	z1 = minDims[2] + (maxDims[2] - minDims[2]) * min(r1,r2)
	z2 = minDims[2] + (maxDims[2] - minDims[2]) * max(r1,r2)
	xmask = numpy.logical_or(pcd[:,0] < x1, pcd[:,0] > x2)
	zmask = numpy.logical_or(pcd[:,2] < z1, pcd[:,2] > z2)
	output = pcd[numpy.logical_or(xmask, zmask)]
	output_file = '%s/%s_synthetic%02d.ply' % (os.path.dirname(gt_filename), building_name, i)
	savePLY(output_file, output)

