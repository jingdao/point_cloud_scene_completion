import numpy as np
import matplotlib.pyplot as plt
import pyflann
import os
import scipy.misc

for mode in ['train','test']:
    for filename in os.listdir('pix2pix/%s' % mode):
        I = scipy.misc.imread('pix2pix/%s/%s' % (mode, filename))
        gt = I[:, 256:, :]
        I = I[:, :256, :]
        interpolated = I.copy()

        mask = I.mean(axis=2) > 0
        v,u = np.nonzero(mask)
        x = np.transpose((v,u))
        flann = pyflann.FLANN()
        pstack = np.transpose(np.nonzero(np.logical_not(mask)))
        print(filename, pstack.shape)
        K = 10 if mode=='train' else 1
        q,_ = flann.nn(x.astype(np.int32), pstack.astype(np.int32), K, algorithm='kdtree_simple')
        for i in range(len(pstack)):
            if K==1:
                min_v,min_u = x[q[i]]
                M = I[min_v, min_u, :]
            else:
                M = np.zeros(3)
                for k in range(K):
                    min_v,min_u = x[q[i,k]]
                    M += I[min_v, min_u, :]
                M /= K
            interpolated[pstack[i,0], pstack[i,1], :] = M

        interpolated = np.hstack((I, gt, interpolated))
        scipy.misc.imsave('pix2pix/interpolated_%s/%s' % (mode, filename), interpolated)

