import numpy as np
import pyflann
import sys

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
	return np.array(vertices),np.array(faces)

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

scene, _ = loadPLY(sys.argv[1])
out, _ = loadPLY(sys.argv[2])

flann = pyflann.FLANN()
q,_ = flann.nn(scene[:, :3], out[:, :3], 1, algorithm='kdtree_simple')
for i in range(len(q)):
    out[i, 3:6] = scene[q[i], 3:6]
savePLY(sys.argv[3], out)
