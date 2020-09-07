import numpy
import os
import subprocess
import sys

METHODS = ['input', 'hole_filling', 'meshing', 'hybrid', 'plane_fitting', 'inpainting', 'pix2pix', 'pcn', 'pcn2', 'folding', 'folding2', 'topnet', 'topnet2']
#METHODS = ['input', 'hole_filling', 'meshing', 'hybrid', 'plane_fitting', 'inpainting', 'pix2pix', 'pcn', 'pcn2', 'folding', 'folding2']
TEST_SET=["01_mason_east","02_pettit","03_seb_north","04_seb_south","05_seb_west","06_seb_east","07_mason_north","08_vl_south","09_vl_circle","10_vl_east","11_cod"]
#TEST_SET=["02_pettit", "07_mason_north"]
aggregates = []
results = [[] for i in range(len(METHODS))]
#for l in sorted(os.listdir('input')):
#    if l.endswith('_gt.ply'):
for ts in TEST_SET:
        l = '%s_gt.ply' % ts
        T = l[:-7]
        print(T)
        GT = 'input/' + l
        INPUT = 'input/' + T + '_input.ply'
        HOLE_FILLING = 'baselines/Hole_filling/' + T + '_input_hole_filled.ply'
        MESHING = 'baselines/Mesh/' + T + '_input_mesh.ply'
        HYBRID = 'baselines/hybrid/' + T + '_input_hole_filled_mesh.ply'
        PLANE_FITTING = 'baselines/plane_fitting/' + T + '_plane_fitted.ply'
        INPAINT = 'baselines/inpainting/' + T + '_inpainted.ply'
        PIX2PIX = 'point-cloud-orthographic-projection/' + T + '_output.ply'
#        PIX2PIX = 'baselines/pix2pix/' + T + '_output.ply'
#        PCN = '../pcn/tmp_fix/' + T + '.ply'
        PCN = 'baselines/PCN/' + T + '.ply'
        PCN2 = 'baselines/PCN_upsampled/' + T + '.ply'
        FOLDING = 'baselines/Folding/' + T + '.ply'
        FOLDING2 = 'baselines/Folding_upsampled/' + T + '.ply'
        TOPNET = 'baselines/TopNet/' + T + '.ply'
        TOPNET2 = 'baselines/TopNet_upsampled/' + T + '.ply'
        for j,TARGET in enumerate([INPUT, HOLE_FILLING, MESHING, HYBRID, PLANE_FITTING, INPAINT, PIX2PIX, PCN, PCN2, FOLDING, FOLDING2, TOPNET, TOPNET2]):
#        for j,TARGET in enumerate([INPUT, HOLE_FILLING, MESHING, HYBRID, PLANE_FITTING, INPAINT, PIX2PIX, PCN, PCN2, FOLDING, FOLDING2]):
            s = subprocess.check_output(['./get_accuracy', GT, TARGET, '0.05'])
            if not isinstance(s, str):
                s = s.decode('utf-8')
            print(s.strip())
            results[j].append([float(k) for k in s.split(',')])

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
