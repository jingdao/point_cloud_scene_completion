import sys
import numpy as np
import numpy.linalg as la
import util
from svd_solve import svd, svd_solve
from hole_filling import fill_holes

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
    fitted = np.zeros((0,points.shape[1]))

    for _ in range(100):
        if points.shape[0] < 500:
            break

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

        final_points = p[max_inlier_list, :]
        plane = fit_plane_LSE(final_points)
        # assign random color to segmented plane
        #c = np.ones((final_points.shape[0],3)) * np.random.randint(256, size=(1,3))
        c = points[max_inlier_list, 3:]
        sav = np.hstack((final_points[:,:3],c))
        # set color as mean of plane color
        color = np.mean(c,0)
        # points to be filled
        pts = sav[:,[0,2,1]]
        hole = fill_holes(pts, distance=0.05, max_circumradius=0.2, max_ratio_radius_area=0.1)
        hole = hole[:,[0,2,1]]
        # add color to hole points
        hole = np.hstack((hole, np.ones(hole.shape)*color))
        # add to already fitted point cloud
        fitted = np.concatenate((fitted,sav,hole))        
        fit_variance = np.var(get_point_dist(final_points, plane))
        #print('RANSAC fit variance: %f' % fit_variance)

        dists = get_point_dist(p, plane)

        select_thresh = inlier_thresh * 1

        inlier_list = np.where(dists < select_thresh)[0]

        # remove fitted points from original point cloud
        points = np.delete(points, max_inlier_list, 0)
        p = np.delete(p, max_inlier_list, 0)

    util.savePLY('plane_fitted.ply', fitted)
    return points

def main():
    filename = sys.argv[1]
    v,_ = util.loadPLY(filename)
    v = np.array(v)
    for _ in range(100):
        v = fit_plane_LSE_RANSAC(v)
        if v.shape[0] < 500:
            return
    print('finished!')

if __name__ == '__main__':
    main()
