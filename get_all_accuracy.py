import numpy
import os
import subprocess
import sys

results_filename = 'results.txt'

try:
    f = open(results_filename, 'r')
except IOError:
    f = open(results_filename, 'w')
    for l in sorted(os.listdir('input')):
        if l.endswith('_gt.ply'):
            T = l[:-7]
            print(T)
            f.write(T+"\n")
            GT = 'input/' + l
            INPUT = 'input/' + T + '_input.ply'
            HOLE_FILLING = 'baselines/Hole_filling/' + T + '_input_hole_filled.ply'
            MESHING = 'baselines/Mesh/' + T + '_input_mesh.ply'
            HYBRID = 'baselines/hybrid/' + T + '_input_hole_filled_mesh.ply'
            PLANE_FITTING = 'baselines/plane_fitting/' + T + '_plane_fitted.ply'
            INPAINT = 'baselines/inpainting/' + T + '_inpainted.ply'
#            PIX2PIX = 'point-cloud-orthographic-projection/' + T + '_output.ply'
            PIX2PIX = 'baselines/pix2pix/' + T + '_output.ply'
            for TARGET in [INPUT, HOLE_FILLING, MESHING, HYBRID, PLANE_FITTING, INPAINT, PIX2PIX]:
                s = subprocess.check_output(['./get_accuracy', GT, TARGET])
                if not isinstance(s, str):
                    s = s.decode('utf-8')
                print(s)
                f.write(s)
    f.close()
    f = open(results_filename, 'r')

METHODS = ['input', 'hole_filling', 'meshing', 'hybrid', 'plane_fitting', 'inpainting', 'pix2pix']
results = [[] for i in range(len(METHODS))]
aggregates = []
results = [[] for i in range(len(METHODS))]
for i in range(11):
    l = f.readline()
    for j in range(len(METHODS)):
        l = f.readline()
        results[j].append([float(k) for k in l.split(',')])
for i in range(len(METHODS)):
    print(METHODS[i])
    A = []
    for k in results[i]:
        print(k)
        A.append(k)
    aggregates.append(numpy.array(A).mean(axis=0))
print('%15s, %5s, %5s, %5s, %5s, %5s'%('method', 'prc', 'rcl', 'F1', 'prmse', 'crmse'))
for i in range(len(METHODS)):
    print('%15s, %5.3f, %5.3f, %5.3f, %5.3f, %5.3f' % (METHODS[i], aggregates[i][0],  aggregates[i][1], aggregates[i][2], aggregates[i][3], aggregates[i][4]))
f.close()
