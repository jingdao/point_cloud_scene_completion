import numpy
from util import savePLY
numpy.random.seed(0)

#create point cloud from wall (XZ plane)
N = 10000
pcd = numpy.zeros((N, 6))
pcd[:,0] = numpy.around(numpy.random.random(N), decimals=3) #random X coordinate
pcd[:,2] = numpy.around(numpy.random.random(N), decimals=3) #random Z coordinate
pcd[:,3:6] = 255 #white color
savePLY('wall.ply', pcd)

#create artificial hole
hole_position = [0.75, 0, 0.75]
hole_radius = 0.2
r = numpy.sqrt((pcd[:,0]-hole_position[0])**2 + (pcd[:,2]-hole_position[2])**2)
savePLY('wall_with_hole.ply', pcd[r > hole_radius, :])

#fill in hole with color
pcd_color = pcd.copy()
pcd_color[r <= hole_radius, 3:6] = [255, 0, 0]
savePLY('wall_with_color.ply', pcd_color)

#add noise
pcd_noise = pcd.copy()
pcd_noise[:,:3] += numpy.random.randn(N,3)*0.01
savePLY('wall_with_noise.ply', pcd_noise)
