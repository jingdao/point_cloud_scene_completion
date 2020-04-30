import numpy as np
import scipy.misc
import matplotlib.pyplot as plt
import scipy.signal

TEST_SET=["01_mason_east","02_pettit","03_seb_north","04_seb_south","05_seb_west","06_seb_east","07_mason_north","08_vl_south","09_vl_circle","10_vl_east","11_cod"]
for t in TEST_SET:
    print(t)
    result = scipy.misc.imread('results/images/interp/%s_input_merged-outputs.png' % t)
    I = scipy.misc.imread('interpolated_test/%s_input_merged.png' % t)
    inputs = I[:,:256,:]
    gt = I[:,256:512,:]
    interp = I[:,512:,:]

    inputs_fg = np.any(inputs > 128, axis=2)
    result_fg = np.any(result > 128, axis=2)
    gt_fg = np.any(gt > 128, axis=2)
    tp = np.logical_and(result_fg, gt_fg).sum()
    fp = np.logical_and(result_fg, np.logical_not(gt_fg)).sum()
    fn = np.logical_and(np.logical_not(result_fg), gt_fg).sum()
    prc = 1.0 * tp / (tp + fp)
    rcl = 1.0 * tp / (tp + fn)
    result_norm = result/255.0 * 2 - 1
    gt_norm = gt/255.0 * 2 - 1
    L1 = np.abs(result_norm - gt_norm).mean()

    mask = np.logical_and(result_fg, gt_fg) 
    color_rmse = np.sqrt(np.mean((result[mask]/255.0 - gt[mask]/255.0)**2))
    print('%.3f/%.3f %.3f %.3f' % (prc,rcl,L1, color_rmse))

    gt_mean = gt[gt_fg].reshape(-1,3).mean(axis=0)
    fix_mean = result.copy()
    added_mask = np.logical_and(result_fg, np.logical_not(inputs_fg))
    fix_mean[added_mask] = gt_mean
    fix_nn = result.copy()
    fix_nn[added_mask] = interp[added_mask]
    fix_median = result.copy()
    fix_median[:,:,0] = scipy.signal.medfilt2d(result[:,:,0], 3)
    fix_median[:,:,1] = scipy.signal.medfilt2d(result[:,:,1], 3)
    fix_median[:,:,2] = scipy.signal.medfilt2d(result[:,:,2], 3)
    color_rmse_mean = np.sqrt(np.mean((fix_mean[mask]/255.0 - gt[mask]/255.0)**2))
    color_rmse_nn = np.sqrt(np.mean((fix_nn[mask]/255.0 - gt[mask]/255.0)**2))
    color_rmse_median = np.sqrt(np.mean((fix_median[mask]/255.0 - gt[mask]/255.0)**2))
    print('%.3f %.3f %.3f %.3f' % (color_rmse, color_rmse_mean, color_rmse_nn, color_rmse_median))

    scipy.misc.imsave('results/images/%s_input_merged-outputs.png' % t, fix_nn)

#    plt.subplot(1,4,1)
#    plt.imshow(result)
#    plt.subplot(1,4,2)
#    plt.imshow(fix_mean)
#    plt.subplot(1,4,3)
#    plt.imshow(fix_nn)
#    plt.subplot(1,4,4)
#    plt.imshow(fix_median)
#    plt.show()
