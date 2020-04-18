import numpy
from util import loadPLY
import sys
numpy.random.seed(0)

if len(sys.argv) < 3:
    print("Usage: python get_accuracy.py ground_truth.ply prediction.ply")
    sys.exit(1)

ground_truth_points, _ = loadPLY(sys.argv[1])
predicted_points, _ = loadPLY(sys.argv[2])

#normalize color to 0->1
ground_truth_points[:,3:6] /= 255.0
predicted_points[:,3:6] /= 255.0

#randomly shuffle points so that voxels can be sampled non-deterministically
numpy.random.shuffle(ground_truth_points)
numpy.random.shuffle(predicted_points)

voxel_resolution = 0.05
ground_truth_voxels = {}
predicted_voxels = {}
voxel_coordinates = numpy.round((ground_truth_points[:,:3] / voxel_resolution)).astype(int)
for i in range(len(ground_truth_points)):
    k = tuple(voxel_coordinates[i])
    if not k in ground_truth_voxels:
        ground_truth_voxels[k] = ground_truth_points[i,:]
      
voxel_coordinates = numpy.round((predicted_points[:,:3] / voxel_resolution)).astype(int)
for i in range(len(predicted_points)):
    k = tuple(voxel_coordinates[i])
    if not k in predicted_voxels:
        predicted_voxels[k] = predicted_points[i,:]
    
#print('ground_truth_points', ground_truth_points.shape, len(ground_truth_voxels), 'voxels')
#print('predicted_points', predicted_points.shape, len(predicted_voxels), 'voxels')

common_voxels = set(ground_truth_voxels.keys()).intersection(set(predicted_voxels.keys()))
voxel_recall = 1.0 * len(common_voxels) / len(ground_truth_voxels) if len(common_voxels)>0 else 0
voxel_precision = 1.0 * len(common_voxels) / len(predicted_voxels) if len(common_voxels)>0 else 0
F1_score = 2*voxel_precision*voxel_recall/(voxel_precision + voxel_recall)
#print('common_voxels', len(common_voxels))
#print('voxel_precision', voxel_precision)
#print('voxel_recall', voxel_recall)
#print('F1_score', F1_score)

position_rmse = 0
color_rmse = 0
for k in common_voxels:
    difference_squared = (ground_truth_voxels[k][:6] - predicted_voxels[k][:6])**2
    position_rmse += difference_squared[:3].sum()
    color_rmse += difference_squared[3:6].sum()

position_rmse = numpy.sqrt(position_rmse / (len(common_voxels)*3))
color_rmse = numpy.sqrt(color_rmse / (len(common_voxels)*3))
#print('position_rmse', position_rmse)
#print('color_rmse', color_rmse)

print('%.3f, %.3f, %.3f, %.3f, %.3f'%(voxel_precision, voxel_recall, F1_score, position_rmse, color_rmse))


