"""Boundary value problem solver."""
from __future__ import division, print_function, absolute_import

from warnings import warn

import numpy as np
from numpy.linalg import norm, pinv

from scipy.sparse import coo_matrix, csc_matrix
from scipy.sparse.linalg import splu
from scipy.optimize import OptimizeResult


EPS = np.finfo(float).eps


def estimate_fun_jac(fun, x, y, p, f0=None):
    """Estimate derivatives of an ODE system rhs with forward differences.

    Returns
    -------
    df_dy : ndarray, shape (n, n, m)
        Derivatives with respect to y. An element (i, j, q) corresponds to
        d f_i(x_q, y_q) / d (y_q)_j.
    df_dp : ndarray with shape (n, k, m) or None
        Derivatives with respect to p. An element (i, j, q) corresponds to
        d f_i(x_q, y_q, p) / d p_j. If `p` is empty, None is returned.
    """
    n, m = y.shape
    if f0 is None:
        f0 = fun(x, y, p)

    dtype = y.dtype

    df_dy = np.empty((n, n, m), dtype=dtype)
    h = EPS**0.5 * (1 + np.abs(y))
    for i in range(n):
        y_new = y.copy()
        y_new[i] += h[i]
        hi = y_new[i] - y[i]
        f_new = fun(x, y_new, p)
        df_dy[:, i, :] = (f_new - f0) / hi

    k = p.shape[0]
    if k == 0:
        df_dp = None
    else:
        df_dp = np.empty((n, k, m), dtype=dtype)
        h = EPS**0.5 * (1 + np.abs(p))
        for i in range(k):
            p_new = p.copy()
            p_new[i] += h[i]
            hi = p_new[i] - p[i]
            f_new = fun(x, y, p_new)
            df_dp[:, i, :] = (f_new - f0) / hi

    return df_dy, df_dp


def estimate_quad_jac(fun, x, y, p, f0=None):
    """Estimate derivatives of an ODE system rhs with forward differences.

    Returns
    -------
    dq_dy : ndarray, shape (n, n, m)
        Derivatives with respect to y. An element (i, j, q) corresponds to
        d q_i(x_q, y_q) / d (y_q)_j.
    dq_dp : ndarray with shape (n, k, m) or None
        Derivatives with respect to p. An element (i, j, q) corresponds to
        d q_i(x_q, y_q, p) / d p_j. If `p` is empty, None is returned.
    """
    n, m = y.shape
    if f0 is None:
        f0 = fun(x, y, p)

    dtype = y.dtype

    dq_dy = np.empty((n, n, m), dtype=dtype)
    h = EPS**0.5 * (1 + np.abs(y))
    for i in range(n):
        y_new = y.copy()
        y_new[i] += h[i]
        hi = y_new[i] - y[i]
        f_new = fun(x, y_new, p)
        dq_dy[:, i, :] = (f_new - f0) / hi

    k = p.shape[0]
    if k == 0:
        dq_dp = None
    else:
        dq_dp = np.empty((n, k, m), dtype=dtype)
        h = EPS**0.5 * (1 + np.abs(p))
        for i in range(k):
            p_new = p.copy()
            p_new[i] += h[i]
            hi = p_new[i] - p[i]
            f_new = fun(x, y, p_new)
            dq_dp[:, i, :] = (f_new - f0) / hi

    return dq_dy, dq_dp


def estimate_bc_jac(bc, ya, qa, yb, qb, p, bc0=None):
    """Estimate derivatives of boundary conditions with forward differences.

    Returns
    -------
    dbc_dya : ndarray, shape (n + k, n)
        Derivatives with respect to ya. An element (i, j) corresponds to
        d bc_i / d ya_j.
    dbc_dyb : ndarray, shape (n + k, n)
        Derivatives with respect to yb. An element (i, j) corresponds to
        d bc_i / d ya_j.
    dbc_dp : ndarray with shape (n + k, k) or None
        Derivatives with respect to p. An element (i, j) corresponds to
        d bc_i / d p_j. If `p` is empty, None is returned.
    """
    n = ya.shape[0]
    nq = qa.shape[0]
    k = p.shape[0]

    if bc0 is None:
        bc0 = bc(ya, yb, p)

    dtype = ya.dtype

    dbc_dya = np.empty((n, n + nq + k), dtype=dtype)
    h = EPS**0.5 * (1 + np.abs(ya))
    for i in range(n):
        ya_new = ya.copy()
        ya_new[i] += h[i]
        hi = ya_new[i] - ya[i]
        bc_new = bc(ya_new, qa, yb, qb, p)
        dbc_dya[i] = (bc_new - bc0) / hi
    dbc_dya = dbc_dya.T

    if nq == 0:
        dbc_dqa = None
        dbc_dqb = None
    else:
        dbc_dqa = np.empty((nq, n + nq + k), dtype=dtype)
        h = EPS ** 0.5 * (1 + np.abs(qa))
        for i in range(n):
            qa_new = qa.copy()
            qa_new[i] += h[i]
            hi = qa_new[i] - qa[i]
            bc_new = bc(ya, qa_new, yb, qb, p)
            dbc_dqa[i] = (bc_new - bc0) / hi
        dbc_dqa = dbc_dqa.T

        dbc_dqb = np.empty((nq, n + nq + k), dtype=dtype)
        h = EPS ** 0.5 * (1 + np.abs(qb))
        for i in range(n):
            qb_new = qb.copy()
            qb_new[i] += h[i]
            hi = qb_new[i] - qb[i]
            bc_new = bc(ya, qa, yb, qb_new, p)
            dbc_dqb[i] = (bc_new - bc0) / hi
        dbc_dqb = dbc_dqb.T

    h = EPS**0.5 * (1 + np.abs(yb))
    dbc_dyb = np.empty((n, n + nq + k), dtype=dtype)
    for i in range(n):
        yb_new = yb.copy()
        yb_new[i] += h[i]
        hi = yb_new[i] - yb[i]
        bc_new = bc(ya, qa, yb_new, qb, p)
        dbc_dyb[i] = (bc_new - bc0) / hi
    dbc_dyb = dbc_dyb.T

    if k == 0:
        dbc_dp = None
    else:
        h = EPS**0.5 * (1 + np.abs(p))
        dbc_dp = np.empty((k, n + nq + k), dtype=dtype)
        for i in range(k):
            p_new = p.copy()
            p_new[i] += h[i]
            hi = p_new[i] - p[i]
            bc_new = bc(ya, qa, yb, qb, p_new)
            dbc_dp[i] = (bc_new - bc0) / hi
        dbc_dp = dbc_dp.T

    return dbc_dya, dbc_dqa, dbc_dyb, dbc_dqb, dbc_dp


def compute_jac_indices(n, nq, m, k):
    """Compute indices for the collocation system Jacobian construction.

    See `construct_global_jac` for the explanation.
    """
    i_col = np.repeat(np.arange((m - 1) * n), n)
    j_col = (np.tile(np.arange(n), n * (m - 1)) +
             np.repeat(np.arange(m - 1) * n, n**2))

    i_bc = np.repeat(np.arange((m - 1) * n, m * n + k), n)
    j_bc = np.tile(np.arange(n), n + k)

    i_p_col = np.repeat(np.arange((m - 1) * n), k)
    j_p_col = np.tile(np.arange(m * n, m * n + k), (m - 1) * n)

    i_p_bc = np.repeat(np.arange((m - 1) * n, m * n + k), k)
    j_p_bc = np.tile(np.arange(m * n, m * n + k), n + k)

    i = np.hstack((i_col, i_col, i_bc, i_bc, i_p_col, i_p_bc))
    j = np.hstack((j_col, j_col + n,
                   j_bc, j_bc + (m - 1) * n,
                   j_p_col, j_p_bc))

    return i, j


def stacked_matmul(a, b):
    """Stacked matrix multiply: out[i,:,:] = np.dot(a[i,:,:], b[i,:,:]).

    In our case a[i, :, :] and b[i, :, :] are always square.
    """
    # Empirical optimization. Use outer Python loop and BLAS for large
    # matrices, otherwise use a single einsum call.
    if a.shape[1] > 50:
        out = np.empty_like(a)
        for i in range(a.shape[0]):
            out[i] = np.dot(a[i], b[i])
        return out
    else:
        return np.einsum('...ij,...jk->...ik', a, b)


def construct_global_jac(n, nq, m, k, i_jac, j_jac, h, df_dy, df_dy_middle, df_dp,
                         df_dp_middle, dq_dy, dq_dy_middle, dq_dp, dq_dp_middle,
                         dbc_dya, dbc_dqa, dbc_dyb, dbc_dqb, dbc_dp):
    """Construct the Jacobian of the collocation system.

    There are n * m + nq + k functions: m - 1 collocations residuals, each
    containing n components, followed by n + nq + k boundary condition residuals.

    There are n * m + nq + k variables: m vectors of y, each containing n
    components, followed by k values of vector p.

    For example, let m = 4, n = 2 and k = 1, then the Jacobian will have
    the following sparsity structure:

        1 1 2 2 0 0 0 0  7
        1 1 2 2 0 0 0 0  7
        0 0 1 1 2 2 0 0  7
        0 0 1 1 2 2 0 0  7
        0 0 0 0 1 1 2 2  7
        0 0 0 0 1 1 2 2  7

        5 5 0 0 0 0 6 6  9
        5 5 0 0 0 0 6 6  9
        5 5 0 0 0 0 6 6  9

        3 3 0 0 0 0 4 4  8
        3 3 0 0 0 0 4 4  8
        3 3 0 0 0 0 4 4  8

    Zeros denote identically zero values, other values denote different kinds
    of blocks in the matrix (see below). The blank row indicates the separation
    of collocation residuals from boundary conditions. And the blank column
    indicates the separation of y values from p values.

    Refer to [1]_  (p. 306) for the formula of n x n blocks for derivatives
    of collocation residuals with respect to y.

    Parameters
    ----------
    n : int
        Number of equations in the ODE system.
    nq : int
        Number of quads in the ODE system.
    m : int
        Number of nodes in the mesh.
    k : int
        Number of the unknown parameters.
    i_jac, j_jac : ndarray
        Row and column indices returned by `compute_jac_indices`. They
        represent different blocks in the Jacobian matrix in the following
        order (see the scheme above):

            * 1: m - 1 diagonal n x n blocks for the collocation residuals.
            * 2: m - 1 off-diagonal n x n blocks for the collocation residuals.
            * 3 : (n + k) x n block for the dependency of the boundary
              conditions on ya.
            * 4: (n + k) x n block for the dependency of the boundary
              conditions on yb.
            * 5: (nq + k) x n block for the dependency of the boundary
              conditions on qa.
            * 6: (nq + k) x n block for the dependency of the boundary
              conditions on qb.
            * 7: (m - 1) * n x k block for the dependency of the collocation
              residuals on p.
            * 8: (n + k) x k block for the dependency of the boundary
              conditions on p.
            * 9: (nq + k) x k block for the dependency of the boundary
              conditions on p.

    h :

    df_dy : ndarray, shape (n, n, m)
        Jacobian of f with respect to y computed at the mesh nodes.
    df_dy_middle : ndarray, shape (n, n, m - 1)
        Jacobian of f with respect to y computed at the middle between the
        mesh nodes.
    df_dp : ndarray with shape (n, k, m) or None
        Jacobian of f with respect to p computed at the mesh nodes.
    df_dp_middle: ndarray with shape (n, k, m - 1) or None
        Jacobian of f with respect to p computed at the middle between the
        mesh nodes.
    dbc_dya, dbc_dyb : ndarray, shape (n, n)
        Jacobian of bc with respect to ya and yb.
    dbc_dp: ndarray with shape (n, k) or None
        Jacobian of bc with respect to p.

    Returns
    -------
    J : csc_matrix, shape (n * m + nq + k, n * m + nq + k)
        Jacobian of the collocation system in a sparse form.

    References
    ----------
    .. [1] J. Kierzenka, L. F. Shampine, "A BVP Solver Based on Residual
       Control and the Maltab PSE", ACM Trans. Math. Softw., Vol. 27,
       Number 3, pp. 299-316, 2001.
    """
    df_dy = np.transpose(df_dy, (2, 0, 1))
    df_dy_middle = np.transpose(df_dy_middle, (2, 0, 1))

    dq_dy = np.transpose(dq_dy, (2, 0, 1))
    dq_dy_middle = np.transpose(dq_dy_middle, (2, 0, 1))
    h = h[:, np.newaxis, np.newaxis]

    dtype = df_dy.dtype

    # Computing diagonal n x n blocks.
    dPhi_dy_0 = np.empty((m - 1, n, n), dtype=dtype)
    dPhi_dy_0[:] = -np.identity(n)
    dPhi_dy_0 -= h / 6 * (df_dy[:-1] + 2 * df_dy_middle)
    T = stacked_matmul(df_dy_middle, df_dy[:-1])
    dPhi_dy_0 -= h**2 / 12 * T

    # Computing off-diagonal n x n blocks.
    dPhi_dy_1 = np.empty((m - 1, n, n), dtype=dtype)
    dPhi_dy_1[:] = np.identity(n)
    dPhi_dy_1 -= h / 6 * (df_dy[1:] + 2 * df_dy_middle)
    T = stacked_matmul(df_dy_middle, df_dy[1:])
    dPhi_dy_1 += h**2 / 12 * T

    values = np.hstack((dPhi_dy_0.ravel(), dPhi_dy_1.ravel(), dbc_dya.ravel(),
                        dbc_dyb.ravel()))

    if nq > 0:
        dPhi_dq_0 = np.empty((m - 1, nq, nq), dtype=dtype)
        dPhi_dq_0[:] = -np.identity(nq)
        dPhi_dq_0 -= h / 6 * (dq_dy[1:] + 2 * dq_dy_middle)
        T = stacked_matmul(dq_dy_middle, dq_dy[:-1])
        dPhi_dq_0 -= h**2 / 12 * T

        dPhi_dq_1 = np.empty((m - 1, nq, nq), dtype=dtype)
        dPhi_dq_1[:] = -np.identity(nq)
        dPhi_dq_1 -= h / 6 * (dq_dy[1:] + 2 * dq_dy_middle)
        T = stacked_matmul(dq_dy_middle, dq_dy[1:])
        dPhi_dq_1 -= h ** 2 / 12 * T

        values = np.hstack((values, dPhi_dq_0.ravel(), dPhi_dq_1.ravel(),
                            dbc_dqa.ravel(), dbc_dqb.ravel()))

    if k > 0:
        df_dp = np.transpose(df_dp, (2, 0, 1))
        df_dp_middle = np.transpose(df_dp_middle, (2, 0, 1))
        T = stacked_matmul(df_dy_middle, df_dp[:-1] - df_dp[1:])
        df_dp_middle += 0.125 * h * T
        dPhi_dp = -h / 6 * (df_dp[:-1] + df_dp[1:] + 4 * df_dp_middle)
        values = np.hstack((values, dPhi_dp.ravel()))

        if nq > 0:
            dq_dp = np.transpose(dq_dp, (2, 0, 1))
            dq_dp_middle = np.transpose(dq_dp_middle, (2, 0, 1))
            T = stacked_matmul(dq_dy_middle, dq_dp[:-1] - dq_dp[1:])
            dq_dp_middle += 0.125 * h * T
            dPhi_dp = -h / 6 * (dq_dp[:-1] + dq_dp[1:] + 4 * dq_dp_middle)
            values = np.hstack((values, dPhi_dp.ravel()))
            # TODO: I don't think this is right

        values = np.hstack((values, dbc_dp.ravel()))

    try:
        J = coo_matrix((values, (i_jac, j_jac)))
    except:
        breakpoint()
    return csc_matrix(J)


def collocation_fun(fun, y, p, x, h):
    """Evaluate collocation residuals.

    This function lies in the core of the method. The solution is sought
    as a cubic C1 continuous spline with derivatives matching the ODE rhs
    at given nodes `x`. Collocation conditions are formed from the equality
    of the spline derivatives and rhs of the ODE system in the middle points
    between nodes.

    Such method is classified to Lobatto IIIA family in ODE literature.
    Refer to [1]_ for the formula and some discussion.

    Returns
    -------
    col_res : ndarray, shape (n, m - 1)
        Collocation residuals at the middle points of the mesh intervals.
    y_middle : ndarray, shape (n, m - 1)
        Values of the cubic spline evaluated at the middle points of the mesh
        intervals.
    f : ndarray, shape (n, m)
        RHS of the ODE system evaluated at the mesh nodes.
    f_middle : ndarray, shape (n, m - 1)
        RHS of the ODE system evaluated at the middle points of the mesh
        intervals (and using `y_middle`).

    References
    ----------
    .. [1] J. Kierzenka, L. F. Shampine, "A BVP Solver Based on Residual
           Control and the Maltab PSE", ACM Trans. Math. Softw., Vol. 27,
           Number 3, pp. 299-316, 2001.
    """
    f = fun(x, y, p)
    y_middle = (0.5 * (y[:, 1:] + y[:, :-1]) -
                0.125 * h * (f[:, 1:] - f[:, :-1]))
    f_middle = fun(x[:-1] + 0.5 * h, y_middle, p)
    col_res = y[:, 1:] - y[:, :-1] - h / 6 * (f[:, :-1] + f[:, 1:] +
                                              4 * f_middle)

    return col_res, y_middle, f, f_middle


def prepare_sys(n, nq, m, k, fun, quad, bc, fun_jac, quad_jac, bc_jac, x, h):
    """Create the function and the Jacobian for the collocation system."""
    x_middle = x[:-1] + 0.5 * h
    i_jac, j_jac = compute_jac_indices(n, nq, m, k)

    def col_fun(y, p):
        return collocation_fun(fun, y, p, x, h)

    def sys_jac(y, q, p, y_middle, f, f_middle, bc0):
        if fun_jac is None:
            df_dy, df_dp = estimate_fun_jac(fun, x, y, p, f)
            df_dy_middle, df_dp_middle = estimate_fun_jac(
                fun, x_middle, y_middle, p, f_middle)
        else:
            df_dy, df_dp = fun_jac(x, y, p)
            df_dy_middle, df_dp_middle = fun_jac(x_middle, y_middle, p)

        if nq > 0:
            if quad_jac is None:
                dq_dy, dq_dp = estimate_quad_jac(quad, x, y, p, f0=None)
                dq_dy_middle, dq_dp_middle = estimate_quad_jac(
                    quad, x_middle, y_middle, p, f0=None)
            else:
                dq_dy, dq_dp = quad_jac(x, y, p)
                dq_dy_middle, dq_dp_middle = quad_jac(x_middle, y_middle, p)
        else:
            dq_dy = np.empty((0, 0, x.size))
            dq_dp = np.empty((0, 0, x.size))
            dq_dy_middle = np.empty((0, 0, x.size-1))
            dq_dp_middle = np.empty((0, 0, x.size-1))

        if bc_jac is None:
            if nq > 0:
                dbc_dya, dbc_dqa, dbc_dyb, dbc_dqb, dbc_dp = estimate_bc_jac(bc, y[:, 0], q[:, 0],
                                                           y[:, -1], q[:, -1], p, bc0)
            else:
                dbc_dya, dbc_dqa, dbc_dyb, dbc_dqb, dbc_dp = estimate_bc_jac(bc, y[:, 0], np.empty((0,)),
                                                           y[:, -1], np.empty((0,)), p, bc0)
        else:
            if nq > 0:
                dbc_dya, dbc_dqa, dbc_dyb, dbc_dqb, dbc_dp = bc_jac(y[:, 0], q[:, 0], y[:, -1], q[:, -1], p)
            else:
                dbc_dya, dbc_dqa, dbc_dyb, dbc_dqb, dbc_dp = bc_jac(y[:, 0], np.empty((0,)), y[:, -1], np.empty((0,)), p)

        return construct_global_jac(n, nq, m, k, i_jac, j_jac, h, df_dy,
                                    df_dy_middle, df_dp, df_dp_middle,
                                    dq_dy, dq_dy_middle, dq_dp, dq_dp_middle,
                                    dbc_dya, dbc_dqa, dbc_dyb, dbc_dqb,
                                    dbc_dp)

    return col_fun, sys_jac


def solve_newton(n, nq, m, h, col_fun, bc, jac, y, q, p, B, bvp_tol):
    """Solve the nonlinear collocation system by a Newton method.

    This is a simple Newton method with a backtracking line search. As
    advised in [1]_, an affine-invariant criterion function F = ||J^-1 r||^2
    is used, where J is the Jacobian matrix at the current iteration and r is
    the vector or collocation residuals (values of the system lhs).

    The method alters between full Newton iterations and the fixed-Jacobian
    iterations based

    There are other tricks proposed in [1]_, but they are not used as they
    don't seem to improve anything significantly, and even break the
    convergence on some test problems I tried.

    All important parameters of the algorithm are defined inside the function.

    Parameters
    ----------
    n : int
        Number of equations in the ODE system.
    m : int
        Number of nodes in the mesh.
    h : ndarray, shape (m-1,)
        Mesh intervals.
    col_fun : callable
        Function computing collocation residuals.
    bc : callable
        Function computing boundary condition residuals.
    jac : callable
        Function computing the Jacobian of the whole system (including
        collocation and boundary condition residuals). It is supposed to
        return csc_matrix.
    y : ndarray, shape (n, m)
        Initial guess for the function values at the mesh nodes.
    p : ndarray, shape (k,)
        Initial guess for the unknown parameters.
    B : ndarray with shape (n, n) or None
        Matrix to force the S y(a) = 0 condition for a problems with the
        singular term. If None, the singular term is assumed to be absent.
    bvp_tol : float
        Tolerance to which we want to solve a BVP.

    Returns
    -------
    y : ndarray, shape (n, m)
        Final iterate for the function values at the mesh nodes.
    p : ndarray, shape (k,)
        Final iterate for the unknown parameters.
    singular : bool
        True, if the LU decomposition failed because Jacobian turned out
        to be singular.

    References
    ----------
    .. [1]  U. Ascher, R. Mattheij and R. Russell "Numerical Solution of
       Boundary Value Problems for Ordinary Differential Equations"
    """
    # We know that the solution residuals at the middle points of the mesh
    # are connected with collocation residuals  r_middle = 1.5 * col_res / h.
    # As our BVP solver tries to decrease relative residuals below a certain
    # tolerance it seems reasonable to terminated Newton iterations by
    # comparison of r_middle / (1 + np.abs(f_middle)) with a certain threshold,
    # which we choose to be 1.5 orders lower than the BVP tolerance. We rewrite
    # the condition as col_res < tol_r * (1 + np.abs(f_middle)), then tol_r
    # should be computed as follows:
    tol_r = 2/3 * h * 5e-2 * bvp_tol

    # We also need to control residuals of the boundary conditions. But it
    # seems that they become very small eventually as the solver progresses,
    # i. e. the tolerance for BC are not very important. We set it 1.5 orders
    # lower than the BVP tolerance as well.
    tol_bc = 5e-2 * bvp_tol

    # Maximum allowed number of Jacobian evaluation and factorization, in
    # other words the maximum number of full Newton iterations. A small value
    # is recommended in the literature.
    max_njev = 4

    # Maximum number of iterations, considering that some of them can be
    # performed with the fixed Jacobian. In theory such iterations are cheap,
    # but it's not that simple in Python.
    max_iter = 8

    # Minimum relative improvement of the criterion function to accept the
    # step (Armijo constant).
    sigma = 0.2

    # Step size decrease factor for backtracking.
    tau = 0.5

    # Maximum number of backtracking steps, the minimum step is then
    # tau ** n_trial.
    n_trial = 4

    col_res, y_middle, f, f_middle = col_fun(y, p)

    if nq > 0:
        bc_res = bc(y[:, 0], q[:, 0], y[:, -1], q[:, -1], p)
    else:
        bc_res = bc(y[:, 0], np.empty((0,)), y[:, -1], np.empty((0,)), p)
    res = np.hstack((col_res.ravel(order='F'), bc_res))

    step = None
    y_new = None
    q_new = None
    p_new = None
    LU = None
    step_new = None
    cost = None
    cost_new = None

    njev = 0
    singular = False
    recompute_jac = True
    for iteration in range(max_iter):
        if recompute_jac:
            J = jac(y, q, p, y_middle, f, f_middle, bc_res)
            njev += 1
            try:
                LU = splu(J)
            except RuntimeError:
                singular = True
                break

            step = LU.solve(res)
            cost = np.dot(step, step)

        y_step = step[:m * n].reshape((n, m), order='F')
        q_step = step[m * n:(m * n)+nq]
        p_step = step[(m * n)+nq:]

        alpha = 1
        for trial in range(n_trial + 1):
            y_new = y - alpha * y_step
            if B is not None:
                y_new[:, 0] = np.dot(B, y_new[:, 0])

            if nq > 0:
                q_new = q - alpha * q_step

            p_new = p - alpha * p_step

            col_res, y_middle, f, f_middle = col_fun(y_new, p_new)
            if nq > 0:
                bc_res = bc(y_new[:, 0], q_new[:, 0], y_new[:, -1], q_new[:, -1], p_new)
            else:
                bc_res = bc(y_new[:, 0], np.empty((0,)), y_new[:, -1], np.empty((0,)), p_new)

            res = np.hstack((col_res.ravel(order='F'), bc_res))

            step_new = LU.solve(res)
            cost_new = np.dot(step_new, step_new)
            if cost_new < (1 - 2 * alpha * sigma) * cost:
                break

            if trial < n_trial:
                alpha *= tau

        y = y_new
        p = p_new

        if njev == max_njev:
            break

        if (np.all(np.abs(col_res) < tol_r * (1 + np.abs(f_middle))) and
                np.all(bc_res < tol_bc)):
            break

        # If the full step was taken, then we are going to continue with
        # the same Jacobian. This is the approach of BVP_SOLVER.
        if alpha == 1:
            step = step_new
            cost = cost_new
            recompute_jac = False
        else:
            recompute_jac = True

    return y, p, singular


def print_iteration_header():
    print("{:^15}{:^15}{:^15}{:^15}".format(
        "Iteration", "Max residual", "Total nodes", "Nodes added"))


def print_iteration_progress(iteration, residual, total_nodes, nodes_added):
    print("{:^15}{:^15.2e}{:^15}{:^15}".format(
        iteration, residual, total_nodes, nodes_added))


class BVPResult(OptimizeResult):
    pass


TERMINATION_MESSAGES = {
    0: "The algorithm converged to the desired accuracy.",
    1: "The maximum number of mesh nodes is exceeded.",
    2: "A singular Jacobian encountered when solving the collocation system."
}


def estimate_rms_residuals(fun, sol, x, h, p, r_middle, f_middle):
    """Estimate rms values of collocation residuals using Lobatto quadrature.

    The residuals are defined as the difference between the derivatives of
    our solution and rhs of the ODE system. We use relative residuals, i.e.
    normalized by 1 + np.abs(f). RMS values are computed as sqrt from the
    normalized integrals of the squared relative residuals over each interval.
    Integrals are estimated using 5-point Lobatto quadrature [1]_, we use the
    fact that residuals at the mesh nodes are identically zero.

    In [2] they don't normalize integrals by interval lengths, which gives
    a higher rate of convergence of the residuals by the factor of h**0.5.
    I chose to do such normalization for an ease of interpretation of return
    values as RMS estimates.

    Returns
    -------
    rms_res : ndarray, shape (m - 1,)
        Estimated rms values of the relative residuals over each interval.

    References
    ----------
    .. [1] http://mathworld.wolfram.com/LobattoQuadrature.html
    .. [2] J. Kierzenka, L. F. Shampine, "A BVP Solver Based on Residual
       Control and the Maltab PSE", ACM Trans. Math. Softw., Vol. 27,
       Number 3, pp. 299-316, 2001.
    """
    x_middle = x[:-1] + 0.5 * h
    s = 0.5 * h * (3/7)**0.5
    x1 = x_middle + s
    x2 = x_middle - s
    y1 = sol(x1)
    y2 = sol(x2)
    y1_prime = sol(x1, 1)
    y2_prime = sol(x2, 1)
    f1 = fun(x1, y1, p)
    f2 = fun(x2, y2, p)
    r1 = y1_prime - f1
    r2 = y2_prime - f2

    r_middle /= 1 + np.abs(f_middle)
    r1 /= 1 + np.abs(f1)
    r2 /= 1 + np.abs(f2)

    r1 = np.sum(np.real(r1 * np.conj(r1)), axis=0)
    r2 = np.sum(np.real(r2 * np.conj(r2)), axis=0)
    r_middle = np.sum(np.real(r_middle * np.conj(r_middle)), axis=0)

    return (0.5 * (32 / 45 * r_middle + 49 / 90 * (r1 + r2))) ** 0.5


def create_spline(y, yp, x, h):
    """Create a cubic spline given values and derivatives.

    Formulas for the coefficients are taken from interpolate.CubicSpline.

    Returns
    -------
    sol : PPoly
        Constructed spline as a PPoly instance.
    """
    from scipy.interpolate import PPoly

    n, m = y.shape
    c = np.empty((4, n, m - 1), dtype=y.dtype)
    slope = (y[:, 1:] - y[:, :-1]) / h
    t = (yp[:, :-1] + yp[:, 1:] - 2 * slope) / h
    c[0] = t / h
    c[1] = (slope - yp[:, :-1]) / h - t
    c[2] = yp[:, :-1]
    c[3] = y[:, :-1]
    c = np.rollaxis(c, 1)

    return PPoly(c, x, extrapolate=True, axis=1)


def modify_mesh(x, insert_1, insert_2):
    """Insert nodes into a mesh.

    Nodes removal logic is not established, its impact on the solver is
    presumably negligible. So only insertion is done in this function.

    Parameters
    ----------
    x : ndarray, shape (m,)
        Mesh nodes.
    insert_1 : ndarray
        Intervals to each insert 1 new node in the middle.
    insert_2 : ndarray
        Intervals to each insert 2 new nodes, such that divide an interval
        into 3 equal parts.

    Returns
    -------
    x_new : ndarray
        New mesh nodes.

    Notes
    -----
    `insert_1` and `insert_2` should not have common values.
    """
    # Because np.insert implementation apparently varies with a version of
    # numpy, we use a simple and reliable approach with sorting.
    return np.sort(np.hstack((
        x,
        0.5 * (x[insert_1] + x[insert_1 + 1]),
        (2 * x[insert_2] + x[insert_2 + 1]) / 3,
        (x[insert_2] + 2 * x[insert_2 + 1]) / 3
    )))


def wrap_functions(fun, quad, bc, fun_jac, quad_jac, bc_jac, k, a, S, D, dtype):
    """Wrap functions for unified usage in the solver."""

    fun_jac_p, fun_jac_wrapped, bc_jac_wrapped = None, None, None
    quad_jac_p, quad_jac_wrapped = None, None

    # if fun_jac is None:
    #     fun_jac_wrapped = None
    #
    # if bc_jac is None:
    #     bc_jac_wrapped = None

    if k == 0:
        def fun_p(x, y, _):
            return np.asarray(fun(x, y), dtype)

        def quad_p(x, y, _):
            return np.asarray(quad(x, y), dtype)

        def bc_wrapped(ya, qa, yb, qb, _):
            return np.asarray(bc(ya, qa, yb, qb), dtype)

        if fun_jac is not None:
            def fun_jac_p(x, y, _):
                return np.asarray(fun_jac(x, y), dtype), None

        if quad_jac is not None:
            def quad_jac_p(x, y, _):
                return np.asarray(quad_jac(x, y), dtype), None

        if bc_jac is not None:
            def bc_jac_wrapped(ya, qa, yb, qb, _):
                dbc_dya, dbc_dyb = bc_jac(ya, qa, yb, qb)
                return (np.asarray(dbc_dya, dtype),
                        np.asarray(dbc_dyb, dtype), None)
    else:
        def fun_p(x, y, p):
            return np.asarray(fun(x, y, p), dtype)

        def quad_p(x, y, p):
            return np.asarray(quad(x, y, p), dtype)

        def bc_wrapped(ya, qa, yb, qb, p):
            return np.asarray(bc(ya, qa, yb, qb, p), dtype)

        if fun_jac is not None:
            def fun_jac_p(x, y, p):
                df_dy, df_dp = fun_jac(x, y, p)
                return np.asarray(df_dy, dtype), np.asarray(df_dp, dtype)

        if quad_jac is not None:
            def quad_jac_p(x, y, p):
                dq_dy, dq_dp = quad_jac(x, y, p)
                return np.asarray(dq_dy, dtype), np.asarray(dq_dp, dtype)

        if bc_jac is not None:
            def bc_jac_wrapped(ya, qa, yb, qb, p):
                dbc_dya, dbc_dyb, dbc_dp = bc_jac(ya, qa, yb, qb, p)
                return (np.asarray(dbc_dya, dtype), np.asarray(dbc_dyb, dtype),
                        np.asarray(dbc_dp, dtype))

    if S is None:
        fun_wrapped = fun_p
    else:
        def fun_wrapped(x, y, p):
            f = fun_p(x, y, p)
            if x[0] == a:
                f[:, 0] = np.dot(D, f[:, 0])
                f[:, 1:] += np.dot(S, y[:, 1:]) / (x[1:] - a)
            else:
                f += np.dot(S, y) / (x - a)
            return f

    quad_wrapped = quad_p

    if fun_jac is not None:
        if S is None:
            fun_jac_wrapped = fun_jac_p
        else:
            Sr = S[:, :, np.newaxis]

            def fun_jac_wrapped(x, y, p):
                df_dy, df_dp = fun_jac_p(x, y, p)
                if x[0] == a:
                    df_dy[:, :, 0] = np.dot(D, df_dy[:, :, 0])
                    df_dy[:, :, 1:] += Sr / (x[1:] - a)
                else:
                    df_dy += Sr / (x - a)

                return df_dy, df_dp

    if quad_jac is not None:
        quad_jac_wrapped = quad_jac_p

    return fun_wrapped, quad_wrapped, bc_wrapped, fun_jac_wrapped, quad_jac_wrapped, bc_jac_wrapped


def solve_bvp(fun, quad, bc, x, y, q, p=None, S=None, fun_jac=None, quad_jac=None, bc_jac=None,
              tol=1e-3, max_nodes=1000, verbose=0):
    """Solve a boundary-value problem for a system of ODEs.

    This function numerically solves a first order system of ODEs subject to
    two-point boundary conditions::

        dy / dx = f(x, y, p) + S * y / (x - a), a <= x <= b
        bc(y(a), y(b), p) = 0

    Here x is a 1-dimensional independent variable, y(x) is a n-dimensional
    vector-valued function and p is a k-dimensional vector of unknown
    parameters which is to be found along with y(x). For the problem to be
    determined there must be n + k boundary conditions, i.e. bc must be
    (n + k)-dimensional function.

    The last singular term in the right-hand side of the system is optional.
    It is defined by an n-by-n matrix S, such that the solution must satisfy
    S y(a) = 0. This condition will be forced during iterations, so it must not
    contradict boundary conditions. See [2]_ for the explanation how this term
    is handled when solving BVPs numerically.

    Problems in a complex domain can be solved as well. In this case y and p
    are considered to be complex, and f and bc are assumed to be complex-valued
    functions, but x stays real. Note that f and bc must be complex
    differentiable (satisfy Cauchy-Riemann equations [4]_), otherwise you
    should rewrite your problem for real and imaginary parts separately. To
    solve a problem in a complex domain, pass an initial guess for y with a
    complex data type (see below).

    Parameters
    ----------
    fun : callable
        Right-hand side of the system. The calling signature is ``fun(x, y)``,
        or ``fun(x, y, p)`` if parameters are present. All arguments are
        ndarray: ``x`` with shape (m,), ``y`` with shape (n, m), meaning that
        ``y[:, i]`` corresponds to ``x[i]``, and ``p`` with shape (k,). The
        return value must be an array with shape (n, m) and with the same
        layout as ``y``.
    bc : callable
        Function evaluating residuals of the boundary conditions. The calling
        signature is ``bc(ya, yb)``, or ``bc(ya, yb, p)`` if parameters are
        present. All arguments are ndarray: ``ya`` and ``yb`` with shape (n,),
        and ``p`` with shape (k,). The return value must be an array with
        shape (n + k,).
    x : array_like, shape (m,)
        Initial mesh. Must be a strictly increasing sequence of real numbers
        with ``x[0]=a`` and ``x[-1]=b``.
    y : array_like, shape (n, m)
        Initial guess for the function values at the mesh nodes, i-th column
        corresponds to ``x[i]``. For problems in a complex domain pass `y`
        with a complex data type (even if the initial guess is purely real).
    p : array_like with shape (k,) or None, optional
        Initial guess for the unknown parameters. If None (default), it is
        assumed that the problem doesn't depend on any parameters.
    S : array_like with shape (n, n) or None
        Matrix defining the singular term. If None (default), the problem is
        solved without the singular term.
    fun_jac : callable or None, optional
        Function computing derivatives of f with respect to y and p. The
        calling signature is ``fun_jac(x, y)``, or ``fun_jac(x, y, p)`` if
        parameters are present. The return must contain 1 or 2 elements in the
        following order:

            * df_dy : array_like with shape (n, n, m) where an element
              (i, j, q) equals to d f_i(x_q, y_q, p) / d (y_q)_j.
            * df_dp : array_like with shape (n, k, m) where an element
              (i, j, q) equals to d f_i(x_q, y_q, p) / d p_j.

        Here q numbers nodes at which x and y are defined, whereas i and j
        number vector components. If the problem is solved without unknown
        parameters df_dp should not be returned.

        If `fun_jac` is None (default), the derivatives will be estimated
        by the forward finite differences.
    bc_jac : callable or None, optional
        Function computing derivatives of bc with respect to ya, yb and p.
        The calling signature is ``bc_jac(ya, yb)``, or ``bc_jac(ya, yb, p)``
        if parameters are present. The return must contain 2 or 3 elements in
        the following order:

            * dbc_dya : array_like with shape (n, n) where an element (i, j)
              equals to d bc_i(ya, yb, p) / d ya_j.
            * dbc_dyb : array_like with shape (n, n) where an element (i, j)
              equals to d bc_i(ya, yb, p) / d yb_j.
            * dbc_dp : array_like with shape (n, k) where an element (i, j)
              equals to d bc_i(ya, yb, p) / d p_j.

        If the problem is solved without unknown parameters dbc_dp should not
        be returned.

        If `bc_jac` is None (default), the derivatives will be estimated by
        the forward finite differences.
    tol : float, optional
        Desired tolerance of the solution. If we define ``r = y' - f(x, y)``
        where y is the found solution, then the solver tries to achieve on each
        mesh interval ``norm(r / (1 + abs(f)) < tol``, where ``norm`` is
        estimated in a root mean squared sense (using a numerical quadrature
        formula). Default is 1e-3.
    max_nodes : int, optional
        Maximum allowed number of the mesh nodes. If exceeded, the algorithm
        terminates. Default is 1000.
    verbose : {0, 1, 2}, optional
        Level of algorithm's verbosity:

            * 0 (default) : work silently.
            * 1 : display a termination report.
            * 2 : display progress during iterations.

    Returns
    -------
    Bunch object with the following fields defined:
    sol : PPoly
        Found solution for y as `scipy.interpolate.PPoly` instance, a C1
        continuous cubic spline.
    p : ndarray or None, shape (k,)
        Found parameters. None, if the parameters were not present in the
        problem.
    x : ndarray, shape (m,)
        Nodes of the final mesh.
    y : ndarray, shape (n, m)
        Solution values at the mesh nodes.
    yp : ndarray, shape (n, m)
        Solution derivatives at the mesh nodes.
    rms_residuals : ndarray, shape (m - 1,)
        RMS values of the relative residuals over each mesh interval (see the
        description of `tol` parameter).
    niter : int
        Number of completed iterations.
    status : int
        Reason for algorithm termination:

            * 0: The algorithm converged to the desired accuracy.
            * 1: The maximum number of mesh nodes is exceeded.
            * 2: A singular Jacobian encountered when solving the collocation
              system.

    message : string
        Verbal description of the termination reason.
    success : bool
        True if the algorithm converged to the desired accuracy (``status=0``).

    Notes
    -----
    This function implements a 4-th order collocation algorithm with the
    control of residuals similar to [1]_. A collocation system is solved
    by a damped Newton method with an affine-invariant criterion function as
    described in [3]_.

    Note that in [1]_  integral residuals are defined without normalization
    by interval lengths. So their definition is different by a multiplier of
    h**0.5 (h is an interval length) from the definition used here.

    .. versionadded:: 0.18.0

    References
    ----------
    .. [1] J. Kierzenka, L. F. Shampine, "A BVP Solver Based on Residual
           Control and the Maltab PSE", ACM Trans. Math. Softw., Vol. 27,
           Number 3, pp. 299-316, 2001.
    .. [2] L.F. Shampine, P. H. Muir and H. Xu, "A User-Friendly Fortran BVP
           Solver".
    .. [3] U. Ascher, R. Mattheij and R. Russell "Numerical Solution of
           Boundary Value Problems for Ordinary Differential Equations".
    .. [4] `Cauchy-Riemann equations
            <https://en.wikipedia.org/wiki/Cauchy-Riemann_equations>`_ on
            Wikipedia.

    Examples
    --------
    In the first example we solve Bratu's problem::

        y'' + k * exp(y) = 0
        y(0) = y(1) = 0

    for k = 1.

    We rewrite the equation as a first order system and implement its
    right-hand side evaluation::

        y1' = y2
        y2' = -exp(y1)

    >>> def fun(x, y):
    ...     return np.vstack((y[1], -np.exp(y[0])))

    Implement evaluation of the boundary condition residuals:

    >>> def bc(ya, yb):
    ...     return np.array([ya[0], yb[0]])

    Define the initial mesh with 5 nodes:

    >>> x = np.linspace(0, 1, 5)

    This problem is known to have two solutions. To obtain both of them we
    use two different initial guesses for y. We denote them by subscripts
    a and b.

    >>> y_a = np.zeros((2, x.size))
    >>> y_b = np.zeros((2, x.size))
    >>> y_b[0] = 3

    Now we are ready to run the solver.

    >>> from scipy.integrate import solve_bvp
    >>> res_a = solve_bvp(fun, bc, x, y_a)
    >>> res_b = solve_bvp(fun, bc, x, y_b)

    Let's plot the two found solutions. We take an advantage of having the
    solution in a spline form to produce a smooth plot.

    >>> x_plot = np.linspace(0, 1, 100)
    >>> y_plot_a = res_a.sol(x_plot)[0]
    >>> y_plot_b = res_b.sol(x_plot)[0]
    >>> import matplotlib.pyplot as plt
    >>> plt.plot(x_plot, y_plot_a, label='y_a')
    >>> plt.plot(x_plot, y_plot_b, label='y_b')
    >>> plt.legend()
    >>> plt.xlabel("x")
    >>> plt.ylabel("y")
    >>> plt.show()

    We see that the two solutions have similar shape, but differ in scale
    significantly.

    In the second example we solve a simple Sturm-Liouville problem::

        y'' + k**2 * y = 0
        y(0) = y(1) = 0

    It is known that a non-trivial solution y = A * sin(k * x) is possible for
    k = pi * n, where n is an integer. To establish the normalization constant
    A = 1 we add a boundary condition::

        y'(0) = k

    Again we rewrite our equation as a first order system and implement its
    right-hand side evaluation::

        y1' = y2
        y2' = -k**2 * y1

    >>> def fun(x, y, p):
    ...     k = p[0]
    ...     return np.vstack((y[1], -k**2 * y[0]))

    Note that parameters p are passed as a vector (with one element in our
    case).

    Implement the boundary conditions:

    >>> def bc(ya, yb, p):
    ...     k = p[0]
    ...     return np.array([ya[0], yb[0], ya[1] - k])

    Setup the initial mesh and guess for y. We aim to find the solution for
    k = 2 * pi, to achieve that we set values of y to approximately follow
    sin(2 * pi * x):

    >>> x = np.linspace(0, 1, 5)
    >>> y = np.zeros((2, x.size))
    >>> y[0, 1] = 1
    >>> y[0, 3] = -1

    Run the solver with 6 as an initial guess for k.

    >>> sol = solve_bvp(fun, bc, x, y, p=[6])

    We see that the found k is approximately correct:

    >>> sol.p[0]
    6.28329460046

    And finally plot the solution to see the anticipated sinusoid:

    >>> x_plot = np.linspace(0, 1, 100)
    >>> y_plot = sol.sol(x_plot)[0]
    >>> plt.plot(x_plot, y_plot)
    >>> plt.xlabel("x")
    >>> plt.ylabel("y")
    >>> plt.show()
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("`x` must be 1 dimensional.")
    h = np.diff(x)
    if np.any(h <= 0):
        raise ValueError("`x` must be strictly increasing.")
    a = x[0]

    y = np.asarray(y)
    if np.issubdtype(y.dtype, np.complexfloating):
        dtype = complex
    else:
        dtype = float
    y = y.astype(dtype, copy=False)

    if y.ndim != 2:
        raise ValueError("`y` must be 2 dimensional.")
    if y.shape[1] != x.shape[0]:
        raise ValueError("`y` is expected to have {} columns, but actually "
                         "has {}.".format(x.shape[0], y.shape[1]))

    if p is None:
        p = np.array([])
    else:
        p = np.asarray(p, dtype=dtype)
    if p.ndim != 1:
        raise ValueError("`p` must be 1 dimensional.")

    if tol < 100 * EPS:
        warn("`tol` is too low, setting to {:.2e}".format(100 * EPS))
        tol = 100 * EPS

    if verbose not in [0, 1, 2]:
        raise ValueError("`verbose` must be in [0, 1, 2].")

    n = y.shape[0]
    nq = q.shape[0]
    k = p.shape[0]

    if S is not None:
        S = np.asarray(S, dtype=dtype)
        if S.shape != (n, n):
            raise ValueError("`S` is expected to have shape {}, "
                             "but actually has {}".format((n, n), S.shape))

        # Compute I - S^+ S to impose necessary boundary conditions.
        B = np.identity(n) - np.dot(pinv(S), S)

        y[:, 0] = np.dot(B, y[:, 0])

        # Compute (I - S)^+ to correct derivatives at x=a.
        D = pinv(np.identity(n) - S)
    else:
        B = None
        D = None

    fun_wrapped, quad_wrapped, bc_wrapped, fun_jac_wrapped, quad_jac_wrapped, bc_jac_wrapped = wrap_functions(
        fun, quad, bc, fun_jac, quad_jac, bc_jac, k, a, S, D, dtype)

    f = fun_wrapped(x, y, p)
    if f.shape != y.shape:
        raise ValueError("`fun` return is expected to have shape {}, "
                         "but actually has {}.".format(y.shape, f.shape))

    if nq > 0:
        bc_res = bc_wrapped(y[:, 0], q[:, 0], y[:, -1], q[:, -1], p)
    else:
        bc_res = bc_wrapped(y[:, 0], [], y[:, -1], [], p)

    if bc_res.shape != (n + nq + k,):
        raise ValueError("`bc` return is expected to have shape {}, "
                         "but actually has {}.".format((n + nq + k,), bc_res.shape))

    # status = 0
    iteration = 0
    if verbose == 2:
        print_iteration_header()

    while True:
        m = x.shape[0]

        col_fun, jac_sys = prepare_sys(n, nq, m, k, fun_wrapped, quad_wrapped, bc_wrapped,
                                       fun_jac_wrapped, quad_jac_wrapped, bc_jac_wrapped, x, h)
        y, p, singular = solve_newton(n, nq, m, h, col_fun, bc_wrapped, jac_sys,
                                      y, q, p, B, tol)
        iteration += 1

        col_res, y_middle, f, f_middle = collocation_fun(fun_wrapped, y,
                                                         p, x, h)
        # This relation is not trivial, but can be verified.
        r_middle = 1.5 * col_res / h
        sol = create_spline(y, f, x, h)
        rms_res = estimate_rms_residuals(fun_wrapped, sol, x, h, p,
                                         r_middle, f_middle)
        max_rms_res = np.max(rms_res)

        if singular:
            status = 2
            break

        insert_1, = np.nonzero((rms_res > tol) & (rms_res < 100 * tol))
        insert_2, = np.nonzero(rms_res >= 100 * tol)
        nodes_added = insert_1.shape[0] + 2 * insert_2.shape[0]

        if m + nodes_added > max_nodes:
            status = 1
            if verbose == 2:
                nodes_added = "({})".format(nodes_added)
                print_iteration_progress(iteration, max_rms_res, m,
                                         nodes_added)
            break

        if verbose == 2:
            print_iteration_progress(iteration, max_rms_res, m, nodes_added)

        if nodes_added > 0:
            x = modify_mesh(x, insert_1, insert_2)
            h = np.diff(x)
            y = sol(x)
        else:
            status = 0
            break

    if verbose > 0:
        if status == 0:
            print("Solved in {} iterations, number of nodes {}, "
                  "maximum relative residual {:.2e}."
                  .format(iteration, x.shape[0], max_rms_res))
        elif status == 1:
            print("Number of nodes is exceeded after iteration {}, "
                  "maximum relative residual {:.2e}."
                  .format(iteration, max_rms_res))
        elif status == 2:
            print("Singular Jacobian encountered when solving the collocation "
                  "system on iteration {}, maximum relative residual {:.2e}."
                  .format(iteration, max_rms_res))

    if p.size == 0:
        p = None

    return BVPResult(sol=sol, p=p, x=x, y=y, q=q, yp=f, rms_residuals=rms_res,
                     niter=iteration, status=status,
                     message=TERMINATION_MESSAGES[status], success=status == 0)
