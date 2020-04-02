import numpy

def loadPLY(filename):
	vertices = []
	faces = []
	numV = 0
	numF = 0
	f = open(filename,'r')
	while True:
		l = f.readline()
		if l.startswith('element vertex'):
			numV = int(l.split()[2])
		elif l.startswith('element face'):
			numF = int(l.split()[2])
		elif l.startswith('end_header'):
			break
	for i in range(numV):
		l = f.readline()
		vertices.append([float(j) for j in l.split()])
	for i in range(numF):
		l = f.readline()
		faces.append([int(j) for j in l.split()[1:4]])
	f.close()
	return numpy.array(vertices),numpy.array(faces)

def savePLY(filename, points, faces=None):
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
""" % len(points))
	if faces is None:
		f.write("end_header\n")
	else:
		f.write("""
element face %d
property list uchar int vertex_index
end_header
""" % (len(faces)))
	for p in points:
		f.write("%f %f %f %d %d %d\n"%(p[0],p[1],p[2],p[3],p[4],p[5]))
	if not faces is None:
		for p in faces:
			f.write("3 %d %d %d\n"%(p[0],p[1],p[2]))
	f.close()
	print('Saved to %s: (%d points)'%(filename, len(points)))

def loadPCD(filename):
	pcd = open(filename,'r')
	for l in pcd:
		if l.startswith('DATA'):
			break
	points = []
	for l in pcd:
		ll = l.split()
		x = float(ll[0])
		y = float(ll[1])
		z = float(ll[2])
		if len(ll)>3:
			rgb = int(ll[3])
			b = rgb & 0xFF
			g = (rgb >> 8) & 0xFF
			r = (rgb >> 16) & 0xFF
			points.append([x,y,z,r,g,b])
		else:
			points.append([x,y,z])
	pcd.close()
	points = numpy.array(points)
	return points

def savePCD(filename,points):
	if len(points)==0:
		return
	f = open(filename,"w")
	l = len(points)
	header = """# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z rgb
SIZE 4 4 4 4
TYPE F F F I
COUNT 1 1 1 1
WIDTH %d
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS %d
DATA ascii
""" % (l,l)
	f.write(header)
	for p in points:
		rgb = (int(p[3]) << 16) | (int(p[4]) << 8) | int(p[5])
		f.write("%f %f %f %d\n"%(p[0],p[1],p[2],rgb))
	f.close()
	print('Saved %d points to %s' % (l,filename))

def saveVoxels(filename, voxels, voxel_scale=1.0, offset=[0.0,0.0,0.0], cross_section=False):
	V = []
	for x in range(voxels.shape[0]):
		for y in range(voxels.shape[1]):
			for z in range(voxels.shape[2]):
				if not cross_section or y==int(voxels.shape[1]/2):
					if voxels[x,y,z] < 0: #unknown
						V.append([x,y,z,255,0,0])
					elif voxels[x,y,z] <= 1.0: #occupied
						V.append([x,y,z,0,255,0])
					else: #free space
						V.append([x,y,z,0,0,255])
	V = numpy.array(V, dtype=float)
	V[:,:3] *= voxel_scale
	V[:,:3] += numpy.array(offset)
	savePLY(filename, V)
