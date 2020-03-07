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

    def show_sampled_image(self, sampled_image, name):
        sampled_image = sampled_image.copy()
        sampled_image = self.apply_median_filter(sampled_image)
        print(sampled_image.shape)
        im = Image.fromarray(sampled_image)
        im.save(name+".png")
        plt.figure()
        plt.imshow(sampled_image, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.show()

    # def show_sampled_image(self, sampled_image):
    #     sampled_image = sampled_image.copy()
    #     sampled_image = self.apply_median_filter(sampled_image)
    #     plt.figure()
    #     plt.imshow(sampled_image, cmap='hot', interpolation='nearest')
    #     plt.colorbar()
    #     plt.show()

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
        xy_images = []
        yz_images = []
        zx_images = []
        for i in range(self.num_scales):
            density = self.density / self.scale_factor**i
            xy_image, yz_image, zx_image = self.sample_image(pc, bounding_box, density=density)
            
            xy_images.append(xy_image)
            yz_images.append(yz_image)
            zx_images.append(zx_image)
        
        final_xy_image = np.ones(xy_images[0].shape)
        final_yz_image = np.ones(yz_images[0].shape)
        final_zx_image = np.ones(zx_images[0].shape)

        for i in range(self.num_scales):
            c_xy_image = cv2.resize(xy_images[i], (final_xy_image.shape[1], final_xy_image.shape[0]), interpolation=cv2.INTER_NEAREST)
            c_yz_image = cv2.resize(yz_images[i], (final_yz_image.shape[1], final_yz_image.shape[0]), interpolation=cv2.INTER_NEAREST)
            c_zx_image = cv2.resize(zx_images[i], (final_zx_image.shape[1], final_zx_image.shape[0]), interpolation=cv2.INTER_NEAREST)

            index_pos_xy = np.where((final_xy_image == 1) & (c_xy_image != 1))
            index_pos_yz = np.where((final_yz_image == 1) & (c_yz_image != 1))
            index_pos_zx = np.where((final_zx_image == 1) & (c_zx_image != 1))

            final_xy_image[index_pos_xy] = c_xy_image[index_pos_xy]
            final_yz_image[index_pos_yz] = c_yz_image[index_pos_yz]
            final_zx_image[index_pos_zx] = c_zx_image[index_pos_zx]

        return final_xy_image, final_yz_image, final_zx_image

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
        pc[:, :] -= bounding_box.center
        pc[:, 0] /= bounding_box.half_xyz[0]
        pc[:, 1] /= bounding_box.half_xyz[1]
        pc[:, 2] /= bounding_box.half_xyz[2]

        # self.pc_visualizer.show_pc(pc)

        #for every point, get its x,y, draw it on film
        sample_width = int(math.ceil(bounding_box.width * density)+1)
        sample_height = int(math.ceil(bounding_box.height * density)+1)
        sample_depth = int(math.ceil(bounding_box.depth * density)+1)
        
        #sample from xy, yz, zx plane
        # print('helght, ', sample_height)
        # print('width, ', sample_width)
        xy_image = np.ones((sample_height, sample_width))
        yz_image = np.ones((sample_height, sample_depth))
        zx_image = np.ones((sample_depth, sample_width))
        for point in pc:
            # c_x = math.ceil((point[0] + bounding_box.half_xyz[0]) * density)
            # c_y = math.ceil((point[1] + bounding_box.half_xyz[1]) * density)
            # c_x = int(round(((point[0] + bounding_box.half_xyz[0]) * density)))
            # c_y = int(round(((point[1] + bounding_box.half_xyz[1]) * density)))
            # c_z = int(round(((point[2] + bounding_box.half_xyz[2]) * density)))
            c_x = int(round(((point[0] + 1.0) * density * bounding_box.half_xyz[0])))
            c_y = int(round(((point[1] + 1.0) * density * bounding_box.half_xyz[1])))
            c_z = int(round(((point[2] + 1.0) * density * bounding_box.half_xyz[2])))
            if(point[2] < xy_image[c_y, c_x]): #nearest point
                xy_image[c_y, c_x] = point[2]
            if(point[0] < yz_image[c_y, c_z]): #nearest point
                yz_image[c_y, c_z] = point[0]
            if(point[1] < zx_image[c_z, c_x]): #nearest point
                zx_image[c_z, c_x] = point[1]
            # added point is the normalized depth value! (ex. for xy image, z value in the point is the depth)

        return xy_image, yz_image, zx_image



    def generate_ortho_projection(self, pc, bounding_box):
        #sample a image based on density
        sampled_image = self.sample_image(pc, bounding_box)

        #scale and pad to target image size




if __name__ == '__main__':
    bb1 = bounding_box.AABB(center=[0,0,0], half_xyz=[4,4,4])
    print(bb1.center)
    
    maya_camera = cameras.MayaCamera()
    pc_visualizer = DepthMapVisualizaer(maya_camera, skip=1, near=0, far=4)
    # pc_visualizer.show_pc_from_depth_map_file('./sample_data/test/1/images/depthRender/Cam1/mayaProject.000004.png', bounding_box=bb1)
    pc_visualizer.show_pc_from_depth_map_file('./zx_resized.png', bounding_box=bb1)

    test_projector = PointCloudOrthoProjector(density=100, image_size=(252, 252), pc_visualizer=pc_visualizer)
    test_depth_map = test_projector.pc_visualizer.loader.load_depth_map_from_file('./zx_resized.png')

    plt.figure()
    plt.imshow(test_depth_map)
    plt.show()
    print(1)

    test_pc = test_projector.pc_visualizer.generate_pc(test_depth_map, bb1)
    test_projector.pc_visualizer.show_pc(test_pc)
    print(2)

    final_xy_image, final_yz_image, final_zx_image = test_projector.sample_image_w_pyramid(test_pc, bb1)
    test_projector.show_sampled_image(final_xy_image,'1')
    test_projector.show_sampled_image(final_yz_image,'2')
    test_projector.show_sampled_image(final_zx_image,'3')

    # bb2 = bounding_box.AABB(center=[0,0,0], half_xyz=[0.2, 0.2, 0.3])
    bb2 = bounding_box.AABB(center=[0,0,0], half_xyz=[4,4,4])
    # bb2 = bounding_box.AABB(center=[21,-20,247], half_xyz=[20,20,20])
    pc_visualizer2 = PCDVisualizer(skip=1, near=0, far=4)

    # test_projector2 = PointCloudOrthoProjector(density=50, image_size=(252, 252), pc_visualizer=pc_visualizer2)
    test_projector2 = PointCloudOrthoProjector(density=100, image_size=(252, 252), pc_visualizer=pc_visualizer2)
    print('loading pcd point cloud!')
    # test_pc = test_projector2.pc_visualizer.loader.load_pc_from_pcd('./sample_data/bunny.pcd')
    # test_pc = test_projector2.pc_visualizer.loader.load_pc_from_pcd('./0.pcd')
    test_pc = test_projector2.pc_visualizer.loader.load_pc_from_pcd('./pcd_images/wall_with_hole.pcd')
    # test_pc = test_projector2.pc_visualizer.loader.load_pc_from_pcd('./pettit_sub.pcd')

    test_pc = test_projector2.pc_visualizer.generate_pc(test_pc, bb2)
    test_projector2.pc_visualizer.show_pc(test_pc)
    final_xy_image, final_yz_image, final_zx_image = test_projector2.sample_image_w_pyramid(test_pc, bb2)
    test_projector2.show_sampled_image(final_xy_image, 'xy')
    test_projector2.show_sampled_image(final_yz_image, 'yz')
    test_projector2.show_sampled_image(final_zx_image, 'zx')
    print('end')