import numpy
from util import loadPLY
import sys

if len(sys.argv) < 3:
    print("Usage: python get_accuracy.py ground_truth.ply prediction.ply")
    sys.exit(1)

ground_truth_points, _ = loadPLY(sys.argv[1])
predicted_points, _ = loadPLY(sys.argv[2])

voxel_resolution = 0.001
ground_truth_voxels = set([tuple(p) for p in numpy.round((ground_truth_points[:,:3] / voxel_resolution)).astype(int)])
if len(predicted_points) > 0:
    predicted_voxels = set([tuple(p) for p in numpy.round((predicted_points[:,:3] / voxel_resolution)).astype(int)])
else:
    predicted_voxels = set()
    
print('ground_truth_points', ground_truth_points.shape, len(ground_truth_voxels), 'voxels')
print('predicted_points', predicted_points.shape, len(predicted_voxels), 'voxels')

common_voxels = ground_truth_voxels.intersection(predicted_voxels)
accuracy = 1.0 * len(common_voxels) / len(ground_truth_voxels)
print('accuracy', accuracy)


