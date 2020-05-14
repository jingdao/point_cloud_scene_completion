import numpy

import sys

sys.path.append('Hole_filling')

from util import loadPLY, savePLY

from HoleDetection import fill_holes


points,_ = loadPLY('./Data/02_pettit_input.ply')

points = points[:, :6]
print(len(points[0,:]))

print('Loaded',len(points),'points')

points_XYZ = points[:,[0,2,1]] #swap Y&Z coordinates


synthetic_points_XYZ = fill_holes(points_XYZ, max_circumradius=0.7, max_ratio_radius_area=0.02, distance=0.01)

print('Created',len(synthetic_points_XYZ),'synthetic points')

synthetic_points_XYZ = synthetic_points_XYZ[:,[0,2,1]] #swap Y&Z coordinates

synthetic_points = numpy.zeros((len(synthetic_points_XYZ), 6))

synthetic_points_color = points[:,3:6].mean(axis=0)

print("Apply color", synthetic_points_color)

synthetic_points[:,:3] = synthetic_points_XYZ

synthetic_points[:,3:6] = synthetic_points_color


result_points = numpy.vstack((synthetic_points, points))

savePLY('./Data/02_pettit_input_hole_filled.ply', result_points)