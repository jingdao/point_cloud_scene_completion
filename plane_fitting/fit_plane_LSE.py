import sys
import numpy as np
import numpy.linalg as la
import util
from svd_solve import svd, svd_solve

def fit_plane_LSE(points):
    # points: Nx4 homogeneous 3d points
    # return: 1d array of four elements [a, b, c, d] of
    # ax+by+cz+d = 0
    assert points.shape[0] >= 3 # at least 3 points needed
    
    U, S, Vt = svd(points)
    null_space = Vt[-1, :]
    return null_space

def get_point_dist(points, plane):
    # return: 1d array of size N (number of points)
    dists = np.abs(points @ plane) / np.sqrt(plane[0]**2 + plane[1]**2 + plane[2]**2)
    return dists

def fit_plane_LSE_RANSAC(points, iters=100, inlier_thresh=0.05):
    # points: Nx4 homogeneous 3d points
    # return: 
    #   plane: 1d array of four elements [a, b, c, d] of ax+by+cz+d = 0
    #   inlier_list: 1d array of size N of inlier points
    
    # make into homogeneous coordinates
    color = points[:,3:]
    p = np.hstack((points[:,:3], np.ones((points.shape[0],1))))

    max_inlier_num = -1
    max_inlier_list = None
    
    N = points.shape[0]
    assert N >= 3

    for i in range(iters):
        chose_id = np.random.choice(N, 3, replace=False)
        chose_points = p[chose_id, :]
        tmp_plane = fit_plane_LSE(chose_points)
        
        dists = get_point_dist(p, tmp_plane)
        tmp_inlier_list = np.where(dists < inlier_thresh)[0]
        tmp_inliers = p[tmp_inlier_list, :]
        num_inliers = tmp_inliers.shape[0]
        if num_inliers > max_inlier_num:
            max_inlier_num = num_inliers
            max_inlier_list = tmp_inlier_list
    #print('max_in_list: ', max_inlier_list)
        
        #print('iter %d, %d inliers' % (i, max_inlier_num))

    final_points = p[max_inlier_list, :]
    plane = fit_plane_LSE(final_points)
    #print(final_points.shape)
    #color[:,1:] = np.zeros((color.shape[0],2))
    c = np.zeros((final_points.shape[0],3))
    c[:,0]+=225
    #print(c.shape)
    sav = np.hstack((final_points[:,:3],c))
    name = 'wall_fit' + str(N) + '.ply'
    util.savePLY(name,sav)
    #print(final_points.shape)
    
    fit_variance = np.var(get_point_dist(final_points, plane))
    print('RANSAC fit variance: %f' % fit_variance)

    dists = get_point_dist(p, plane)

    select_thresh = inlier_thresh * 1

    inlier_list = np.where(dists < select_thresh)[0]

    # remove fitted points from original point cloud
    points = np.delete(points, max_inlier_list, 0)
    return points

def main():
    filename = sys.argv[1]
    v,f = util.loadPLY(filename)
    v = np.array(v)
    for _ in range(100):
        v = fit_plane_LSE_RANSAC(v)
        if v.shape[0] < 500:
            return
    print('finished!')

if __name__ == '__main__':
    main()
