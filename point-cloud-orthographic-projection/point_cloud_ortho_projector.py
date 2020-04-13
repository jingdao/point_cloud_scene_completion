'''
ortho project a point clound to defined image plane

jiang wei
'''

import bounding_box
import cameras
try:
    from .point_cloud_visualizer import DepthMapVisualizaer
    from .point_cloud_visualizer import PCDVisualizer
except Exception:
    from point_cloud_visualizer import DepthMapVisualizaer
    from point_cloud_visualizer import PCDVisualizer
import math
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from load_data import PCDDataLoader
import sys
sys.path.append("..")
from util import loadPLY, savePLY
import scipy.ndimage
import scipy.signal
import pyflann

class PointCloudOrthoProjector():

    def __init__(self, density, image_size, pc_visualizer, pixel_scale=1, num_scales=4, scale_factor=1.3):
        assert(len(image_size)==2)
        self.density = density #sqrt(num_pixels per m^2)
        self.image_size = image_size
        self.pc_visualizer = pc_visualizer
        self.pixel_scale = pixel_scale
        self.num_scales = num_scales
        self.scale_factor = scale_factor

    # def project_one_point(self, point, film):
    #     pass

    def show_sampled_image(self, depth_image, rgb_image, name):
        depth_image_filtered = scipy.signal.medfilt2d(depth_image, 3)
        rgb_image_filtered = np.zeros(rgb_image.shape, dtype=np.uint8)
        rgb_image_filtered[:,:,0] = scipy.signal.medfilt2d(rgb_image[:,:,0], 3).astype(np.uint8)
        rgb_image_filtered[:,:,1] = scipy.signal.medfilt2d(rgb_image[:,:,1], 3).astype(np.uint8)
        rgb_image_filtered[:,:,2] = scipy.signal.medfilt2d(rgb_image[:,:,2], 3).astype(np.uint8)
        im = Image.fromarray(rgb_image_filtered)
        im.save(name+"_rgb.png")
        np.save(name+"_depth.npy", depth_image_filtered)
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(depth_image_filtered, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.title('depth image')
        plt.subplot(1,2,2)
        plt.imshow(rgb_image_filtered)
        plt.title('rgb image')
        plt.show()

    def apply_median_filter(self, view_image):
        #normalized value to 0 - 255
        view_image = view_image.copy()
        view_image = (view_image+1.0) * 127.5
        view_image = view_image.astype(np.uint8)

        #apply median blur
        view_image = np.reshape(view_image, view_image.shape + (1,))
        view_image = cv2.medianBlur(view_image, 5)

        return view_image

    def sample_image_w_pyramid(self, pc, bounding_box):
        #multi-scale
        depth_images = []
        rgb_images = []
        for i in range(self.num_scales):
            density = self.density / self.scale_factor**i
            zx_depth_image, zx_rgb_image = self.sample_image(pc, bounding_box, density=density)
            depth_images.append(zx_depth_image)
            rgb_images.append(zx_rgb_image)
        
        D = bounding_box.half_xyz[1]
        final_depth_image = np.ones(depth_images[0].shape) * D
        final_rgb_image = np.zeros(rgb_images[0].shape, dtype=np.uint8)
        for i in range(self.num_scales):
            if i > 0:
                rgb_image = scipy.misc.imresize(rgb_images[i], final_rgb_image.shape, interp='nearest')
                depth_image = scipy.misc.imresize(depth_images[i], final_depth_image.shape, interp='nearest',mode='F')
            else:
                rgb_image = rgb_images[i]
                depth_image = depth_images[i] 
            id1, id2 = np.where((final_depth_image == D) & (depth_image < D))
            final_rgb_image[id1, id2, :] = rgb_image[id1, id2, :]
            final_depth_image[id1, id2] = depth_image[id1, id2]

        return final_depth_image, final_rgb_image

    def sample_image(self, pc, bounding_box, density=None):
        pc=pc.copy()
        # print('orig point size: ', pc.shape)
        if density is None:
            density = self.density
        # print('sample density:', density)
        if bounding_box.name() == 'AABB':
            pass
        elif bounding_box.name() == 'OBB':
            #transform pc and obb to aabb
            raise('unsupport bounding box type')
        else:
            raise('unsupport bounding box type')

        #convert pc to normalized space
        pc[:, :3] -= bounding_box.center
        pc[:, 0] /= bounding_box.half_xyz[0]
        #do not normalize Y coordinate because we need to recover it later!
        pc[:, 2] /= bounding_box.half_xyz[2]

        #for every point, get its x,y, draw it on film
        sample_width = int(math.ceil(bounding_box.width * density)+1)
        sample_height = int(math.ceil(bounding_box.height * density)+1)
        sample_depth = int(math.ceil(bounding_box.depth * density)+1)
        
        #sample from zx plane
        zx_depth_image = np.ones((sample_depth, sample_width)) * bounding_box.half_xyz[1]
        zx_rgb_image = np.zeros((sample_depth, sample_width, 3), dtype=np.uint8)
        for point in pc:
            c_x = int(round(((point[0] + 1.0) * density * bounding_box.half_xyz[0])))
            c_y = int(round(((point[1] + 1.0) * density * bounding_box.half_xyz[1])))
            c_z = int(round(((point[2] + 1.0) * density * bounding_box.half_xyz[2])))
            if(point[1] < zx_depth_image[c_z, c_x]): #nearest point
                zx_depth_image[c_z, c_x] = point[1]
                zx_rgb_image[c_z, c_x] = point[3:6]

        return zx_depth_image, zx_rgb_image

    def generate_ortho_projection(self, pc, bounding_box):
        #sample a image based on density
        sampled_image = self.sample_image(pc, bounding_box)

        #scale and pad to target image size




if __name__ == '__main__':
    convert3Dto2D = False #True to convert 3D to 2D, False to convert 2D to 3D
    # test_filename = 'wall_with_hole'
    test_filename = 'mason_input'
    # test_filename = 'pettit_input'
    
    if convert3Dto2D:
        ### 3D point cloud to 2D projection ###
        # load pcd point cloud
        test_pc,_ = loadPLY('../%s.ply' % test_filename)
        #flip z axis
        test_pc[:,2] = -test_pc[:,2]
        print('loaded point cloud',test_pc.shape)
        
        #calculate center and half_xyz
        min_xyz = test_pc[:,:3].min(axis=0)
        max_xyz = test_pc[:,:3].max(axis=0)
        center = 0.5 * (min_xyz + max_xyz)
        half_xyz = 0.5 * (max_xyz - min_xyz) + 0.5
        density = 50.0
        print('center',center)
        print('half_xyz',half_xyz)
        print('density',density)
        #save parameters to text file
        f = open('param_%s.txt'%test_filename, 'w')
        f.write("%f %f %f %f %f %f %f\n"%(center[0], center[1], center[2], half_xyz[0], half_xyz[1], half_xyz[2], density))
        f.close()

        bb2 = bounding_box.AABB(center=center, half_xyz=half_xyz)
        pc_visualizer2 = PCDVisualizer(skip=1, near=0, far=4)

        #create a projector object
        test_projector2 = PointCloudOrthoProjector(density=density, image_size=(252, 252), pc_visualizer=pc_visualizer2)
        depth_image, rgb_image = test_projector2.sample_image_w_pyramid(test_pc, bb2)
        #visualize and save the resulting 2D images
        test_projector2.show_sampled_image(depth_image, rgb_image, test_filename)

    else:

        ### 2D projection to 3D point cloud###

        #read in depth image and RGB image
        depth_image = np.load('%s_depth.npy' % test_filename)
        rgb_image = scipy.misc.imread('%s_rgb.png' % test_filename)
        filled_image = scipy.misc.imread('%s_filled.png' % test_filename)
        print('depth_image', depth_image.shape)
        print('rgb_image', rgb_image.shape)

        #get parameters from text file
        f = open('param_%s.txt'%test_filename, 'r')
        l = [float(t) for t in f.readline().split()]
        center = np.array([l[0], l[1], l[2]])
        half_xyz = np.array([l[3], l[4], l[5]])
        density = l[6]
        f.close()
        print('center',center)
        print('half_xyz',half_xyz)
        print('density',density)
        bb1 = bounding_box.AABB(center=center, half_xyz=half_xyz)

        #project image back to 3D point cloud
        v,u = np.nonzero(rgb_image.mean(axis=2))
        x = np.transpose((v,u)) # array of nonzero indices in rgb image (N,2)
        v_f,u_f = np.nonzero(filled_image.mean(axis=2)>100)
        output_pc = np.zeros((len(u_f), 6))
        flann = pyflann.FLANN()
        pstack = []
        idx = []
        for i in range(len(u_f)):
            #X coordinate
            output_pc[i, 0] = (u_f[i] / density / bb1.half_xyz[0] - 1.0) * bb1.half_xyz[0]
            #Y coordinate
            if np.all(rgb_image[v_f[i],u_f[i],:]) == 0:
                idx.append(i)
                pstack.append([v_f[i],u_f[i]])
            else:
                output_pc[i,1] = depth_image[v_f[i], u_f[i]]
            #Z coordinate
            output_pc[i, 2] = (v_f[i] / density / bb1.half_xyz[2] - 1.0) * bb1.half_xyz[2]
            #RGB color
            output_pc[i, 3:6] = filled_image[v_f[i], u_f[i], :] 
        pstack = np.array(pstack)
        q,_ = flann.nn(x.astype(np.int32), pstack.astype(np.int32), 1, algorithm='kdtree_simple')
        for i in range(len(idx)):
            min_v,min_u = x[q[i]]
            output_pc[idx[i],1] = depth_image[min_v, min_u]
        output_pc[:,:3] += center
        #flip z axis
        output_pc[:,2] = -output_pc[:,2]
        original_pc,_ = loadPLY('../%s.ply' % test_filename)
        output_pc = np.vstack((output_pc, original_pc))
        savePLY('%s_output.ply'%test_filename, output_pc)

