import numpy
import h5py
import sys
import os
sys.path.append('..')
from util import loadPLY, savePLY

TEST_SET=["01_mason_east","02_pettit","03_seb_north","04_seb_south","05_seb_west","06_seb_east","07_mason_north","08_vl_south","09_vl_circle","10_vl_east","11_cod"]
base_path = '/home/jd/Desktop/completion3d/data/facade'

num_pts = 131072
total_train = 0
train_list = []
val_list = []
val_scale_offset = []

def saveH5(outfile, pc):
	h5_fout = h5py.File(outfile,'w')
	h5_fout.create_dataset(
		'data', data=pc,
		compression='gzip', compression_opts=4,
		dtype=numpy.float32)
	h5_fout.close()

def downsample(pc):
    partial = pc[:, :3].copy()
    center = 0.5 * (partial.min(axis=0) + partial.max(axis=0))
    partial -= center
    scale = (partial.max(axis=0) - partial.min(axis=0)).max()
    partial /= scale
    partial = partial[numpy.random.choice(len(partial), num_pts, replace=len(partial)<num_pts), :3]
    return partial, scale, center

for T in TEST_SET:
    sceneID = T[:2]
    train = []
    input_folder = '../point-cloud-orthographic-projection/%s/' % T
    train_gt_folder = '%s/train/gt/%s/' % (base_path, sceneID)
    train_partial_folder = '%s/train/partial/%s/' % (base_path, sceneID)
    val_gt_folder = '%s/val/gt/%s/' % (base_path, sceneID)
    val_partial_folder = '%s/val/partial/%s/' % (base_path, sceneID)
    if not os.path.isdir(train_gt_folder):
        os.mkdir(train_gt_folder)
    if not os.path.isdir(train_partial_folder):
        os.mkdir(train_partial_folder)
    if not os.path.isdir(val_gt_folder):
        os.mkdir(val_gt_folder)
    if not os.path.isdir(val_partial_folder):
        os.mkdir(val_partial_folder)

    for s in os.listdir(input_folder):
        if s.endswith('.ply'):
            if s.endswith('input.ply'):
                p, _ = loadPLY(input_folder + s)
                p,c,o = downsample(p)
                val_scale_offset.append([c]+list(o))
                val_list.append('%s/%s' % (sceneID, s.replace('.ply', '')))
                saveH5(val_partial_folder + s.replace('ply', 'h5'), p)
            elif s.endswith('gt.ply'):
                gt, _ = loadPLY(input_folder + s)
                gt,_,_ = downsample(gt)
                saveH5(val_gt_folder + s.replace('gt.ply','input.h5'), gt)
            else:
                train.append(s)
    total_train += len(train)

    for t in train:
        print(T, t)
        p,_ = loadPLY(input_folder + t)
        p,_,_ = downsample(p)
        train_list.append('%s/%s' % (sceneID, t.replace('.ply', '')))
        saveH5(train_partial_folder + t.replace('ply', 'h5'), p)
        saveH5(train_gt_folder + t.replace('ply','h5'), gt)
#    break

f = open('%s/train.list' % base_path, 'w')
for s in train_list:
    f.write(s + '\n')
f.close()
f = open('%s/val.list' % base_path, 'w')
for s in val_list:
    f.write(s + '\n')
f.close()
val_scale_offset = numpy.array(val_scale_offset)
numpy.savetxt('%s/val_scale_offset.txt' % base_path, val_scale_offset)
