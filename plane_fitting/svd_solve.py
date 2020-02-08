import numpy as np
import numpy.linalg as la

eps = 0.00001

def svd(A):
    u, s, vh = la.svd(A)
    S = np.zeros(A.shape)
    S[:s.shape[0], :s.shape[0]] = np.diag(s)
    return u, S, vh

def inverse_sigma(S):
    inv_S = S.copy().transpose()
    for i in range(min(S.shape)):
        if abs(inv_S[i, i]) > eps :
            inv_S[i, i] = 1.0/inv_S[i, i]
    return inv_S

def svd_solve(A, b):
    U, S, Vt = svd(A)
    inv_S = inverse_sigma(S)
    svd_solution = Vt.transpose() @ inv_S @ U.transpose() @ b
    
    print('U:')
    print(U)
    print('Sigma:')
    print(S)
    print('V_transpose:')
    print(Vt)
    print('--------------')
    print('SVD solution:')
    print(svd_solution)
    print('A multiplies SVD solution:')
    print(A @ svd_solution)

    return svd_solution