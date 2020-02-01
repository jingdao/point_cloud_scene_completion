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
	return numpy.array(vertices),numpy.array(vertices)

def savePLY(filename, points):
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
end_header
""" % len(points))
	for p in points:
		f.write("%f %f %f %d %d %d\n"%(p[0],p[1],p[2],p[3],p[4],p[5]))
	f.close()
	print('Saved to %s: (%d points)'%(filename, len(points)))
