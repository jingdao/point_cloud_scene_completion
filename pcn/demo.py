# Author: Wentao Yuan (wyuan1@cs.cmu.edu) 05/31/2018

import argparse
import importlib
import models
import numpy as np
import tensorflow as tf
#from matplotlib import pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
#from open3d import *
from io_util import read_pcd, save_pcd, loadPLY, savePLY
import sys
#import pyflann

def plot_pcd(ax, pcd):
    ax.scatter(pcd[:, 0], pcd[:, 1], pcd[:, 2], zdir='y', c=pcd[:, 0], s=0.5, cmap='Reds', vmin=-1, vmax=0.5)
    ax.set_axis_off()
    ax.set_xlim(-0.3, 0.3)
    ax.set_ylim(-0.3, 0.3)
    ax.set_zlim(-0.3, 0.3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', default='demo_data/car.pcd')
    parser.add_argument('--output_path', default='test.pcd')
    parser.add_argument('--model_type', default='pcn_cd')
    parser.add_argument('--checkpoint', default='data/trained_models/pcn_cd')
    parser.add_argument('--num_gt_points', type=int, default=16384)
    args = parser.parse_args()

    inputs = tf.placeholder(tf.float32, (1, None, 3))
    gt = tf.placeholder(tf.float32, (1, args.num_gt_points, 3))
    print(gt.shape)
    npts = tf.placeholder(tf.int32, (1,))
    model_module = importlib.import_module('.%s' % args.model_type, 'models')
    model = model_module.Model(inputs, npts, gt, tf.constant(1.0))

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    config.allow_soft_placement = True
    sess = tf.Session(config=config)

    saver = tf.train.Saver()
    saver.restore(sess, args.checkpoint)

#    partial = read_point_cloud(args.input_path)
#    partial = np.array(partial.points)
    print('Processing', args.input_path)
    if args.input_path.endswith('.pcd'):
        partial = read_pcd(args.input_path)
    elif args.input_path.endswith('.ply'):
        scene, _ = loadPLY(args.input_path)
        partial = scene[:, :3].copy()
        center = 0.5 * (partial.min(axis=0) + partial.max(axis=0))
        partial -= center
        scale = (partial.max(axis=0) - partial.min(axis=0)).max()
        partial /= scale
        save_pcd('scaled_partial.pcd', partial)
        mean_color = scene[:, 3:6].mean(axis=0)
    print('partial', partial.shape)
    complete = sess.run(model.outputs, feed_dict={inputs: [partial], npts: [partial.shape[0]]})[0]
    print('complete', complete.shape)
    save_pcd('scaled_complete.pcd', complete)
    out = np.zeros((len(complete), 6))
    out[:, :3] = complete*scale + center
    out[:, 3:6] = mean_color
#    flann = pyflann.FLANN()
#    q,_ = flann.nn(scene[:, :3], out[:, :3], 1, algorithm='kdtree_simple')
#    for i in range(len(q)):
#        out[i, 3:6] = scene[q[i], 3:6]
    savePLY(args.output_path, out)
#    save_pcd(args.output_path, complete)

#    fig = plt.figure(figsize=(8, 4))
#    ax = fig.add_subplot(121, projection='3d')
#    plot_pcd(ax, partial)
#    ax.set_title('Input')
#    ax = fig.add_subplot(122, projection='3d')
#    plot_pcd(ax, complete)
#    ax.set_title('Output')
#    plt.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0)
#    plt.show()
