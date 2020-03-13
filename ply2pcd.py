import sys
from util import loadPLY,savePCD

if len(sys.argv)<3:
    print('python ply2pcd.py [input.ply] [output.pcd]')
    sys.exit(1)

vertices,faces = loadPLY(sys.argv[1])
savePCD(sys.argv[2], vertices)
