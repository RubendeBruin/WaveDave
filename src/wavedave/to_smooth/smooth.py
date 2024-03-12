"""This is the last version of the smoothing algorithm that was developed 3 years ago"""

import numpy as np
from .bins import bins_from_frequency_grid


def to_continuous_1d(freq, efth,  MAXITER : int =100, TOLERANCE=1e-5):
    """Converts the spectral data """

    # Based on the grid, try to obtain the bin edges
    left, right, width, center = bins_from_frequency_grid(freq)

    # trivial case
    if np.all(efth <= 1e-6):
        return center, efth

    # store the original energy of the spectrum (1D) / energy of each spectral direction (2D)
    m0_bins = np.sum(width * efth)

    # iterator settings
    update_rate = (
        0.5  # new iteration = update_rate *guess + (1-update_rate) * actual_values
    )
    last_update = 999

    #
    f_left = center[:-1]  # datapoint left of current
    f_right = center[1:]  # datapoint right of current
    edge_internal = left[1:]  # all internal edges
    dfl = edge_internal - f_left  # internal edge to center of bin on left of edge
    dfr = f_right - edge_internal  # internal edge to center of bin on left of edge

    d_left = center - left  # width of left side of bin
    d_right = right - center  # width of right side of bin

    e0 = efth * width  # energy per bin

    _log = []

    converged = False
    for i in range(MAXITER):

        # interpolate the values on the bin-edges using linear interpolation

        # spectral density at datapoint left or right of internal edge
        # (take .data to get rid of the freq-coordinate as it is not correct anymore since we're refering to left or right)
        s_left = efth[:-1]  # .isel(freq=slice(None, -1)).data
        s_right = efth[1:]  # .isel(freq=slice(1, None)).data

        # Interpolate the values at the edges between the centers
        s_edge_internal = s_left + dfl * (s_right - s_left) / (dfr + dfl)

        # values at the outer edges are zero
        # prepend zeros to s_edge_internal
        zero_energy_at_outside = np.zeros(
            shape=(*s_edge_internal.shape[:-1], 1)
        )  # everything but the last dim
        s_left = np.append(
            zero_energy_at_outside, s_edge_internal, axis=-1
        )  # s_edge[:-1]
        s_right = np.append(s_edge_internal, zero_energy_at_outside, axis=-1)

        # Now calculate the spectral density at the frequency grid in order to keep the
        # energy per bin the same as the initial value (e0)

        # e0 =
        # 0.5 * (s_left_edge + s_datapoint) * d_left +
        # 0.5 * (s_right_edge + s_datapoint) * d_right
        # =
        # 0.5*s_left_edge * d_left + 0.5*s_datapoint * d_left + 0.5 * s_right*edge*d_right + 0.5 * s_datapoint * d_right
        #
        # 0.5 * s_datapoint ( d_left + d_right ) = e0 - 0.5 * s_left_edge * d_left - 0.5 * s_right_edge * d_right

        new_estimate = (e0 - 0.5 * s_left * d_left - 0.5 * s_right * d_right) / (
            0.5 * (d_left + d_right)
        )

        # we may have gotten datapoints below zero
        new_estimate = np.maximum(new_estimate, 0)  # note, not max!

        # update, convergence check
        update = new_estimate - efth  # signed
        change_in_update = update - last_update
        last_update = update

        # print(f'it {i} , max update {np.max(np.abs(change_in_update))}')
        _log.append(f"it {i} , max update {np.max(np.abs(change_in_update))}")

        # relaxed updates converge quicker
        efth = update_rate * new_estimate + (1 - update_rate) * efth

        # scale to original m0
        m0_cont = np.trapz(efth.data, center)
        scale = m0_bins / m0_cont
        efth *= scale

        if np.max(np.abs(change_in_update)) < TOLERANCE:
            converged = True
            break


    if not converged:
        for l in _log:
            print(l)
        raise ValueError(
            "Convergence criteria not reached - debug into printed above"
        )



    return center, efth

#
# def to_continuous_2d(efth, freq, MAXITER=100, TOLERANCE=1e-5):
#     """Converts the spectral data """
#
#     # Based on the grid, try to obtain the bin edges
#     left, right, width, center = bins_from_frequency_grid(freq)
#
#     # store the original energy of the spectrum (1D) / energy of each spectral direction (2D)
#     m0_bins = np.sum(width * efth, axis=-1)
#
#     print('original bins using derived width')
#     print(m0_bins)
#     print('bin widths')
#     print(width)
#
#     print(f'target Hs = {4*np.sqrt(np.sum(10*m0_bins))}')
#
#     if np.sum(m0_bins.shape) <= 1:
#         is_oned = True
#     else:
#         is_oned = False
#
#     # iterator settings
#     update_rate = (
#         0.5  # new iteration = update_rate *guess + (1-update_rate) * actual_values
#     )
#     last_update = 999
#
#     #
#     f_left = center[:-1]  # datapoint left of current
#     f_right = center[1:]  # datapoint right of current
#     edge_internal = left[1:]  # all internal edges
#     dfl = edge_internal - f_left  # internal edge to center of bin on left of edge
#     dfr = f_right - edge_internal  # internal edge to center of bin on left of edge
#
#     d_left = center - left  # width of left side of bin
#     d_right = right - center  # width of right side of bin
#
#     e0 = efth * width  # energy per bin
#
#     _log = []
#
#     converged = False
#     for i in range(MAXITER):
#
#         # interpolate the values on the bin-edges using linear interpolation
#
#         # spectral density at datapoint left or right of internal edge
#         # (take .data to get rid of the freq-coordinate as it is not correct anymore since we're refering to left or right)
#         if is_oned:
#             s_left = efth[:-1]  # .isel(freq=slice(None, -1)).data
#             s_right = efth[1:]  # .isel(freq=slice(1, None)).data
#         else:
#             s_left = efth[:, :-1]  # .isel(freq=slice(None, -1)).data
#             s_right = efth[:, 1:]  # .isel(freq=slice(1, None)).data
#
#         # Interpolate the values at the edges between the centers
#         s_edge_internal = s_left + dfl * (s_right - s_left) / (dfr + dfl)
#
#         # values at the outer edges are zero
#         # prepend zeros to s_edge_internal
#         zero_energy_at_outside = np.zeros(
#             shape=(*s_edge_internal.shape[:-1], 1)
#         )  # everything but the last dim
#         s_left = np.append(
#             zero_energy_at_outside, s_edge_internal, axis=-1
#         )  # s_edge[:-1]
#         s_right = np.append(s_edge_internal, zero_energy_at_outside, axis=-1)
#
#         # Now calculate the spectral density at the frequency grid in order to keep the
#         # energy per bin the same as the initial value (e0)
#
#         # e0 =
#         # 0.5 * (s_left_edge + s_datapoint) * d_left +
#         # 0.5 * (s_right_edge + s_datapoint) * d_right
#         # =
#         # 0.5*s_left_edge * d_left + 0.5*s_datapoint * d_left + 0.5 * s_right*edge*d_right + 0.5 * s_datapoint * d_right
#         #
#         # 0.5 * s_datapoint ( d_left + d_right ) = e0 - 0.5 * s_left_edge * d_left - 0.5 * s_right_edge * d_right
#
#         new_estimate = (e0 - 0.5 * s_left * d_left - 0.5 * s_right * d_right) / (
#             0.5 * (d_left + d_right)
#         )
#
#         # we may have gotten datapoints below zero
#         new_estimate = np.maximum(new_estimate, 0)  # note, not max!
#
#         # update, convergence check
#         update = new_estimate - efth  # signed
#         change_in_update = update - last_update
#         last_update = update
#
#         if np.max(np.abs(change_in_update)) < TOLERANCE:
#             converged = True
#             break
#
#         # print(f'it {i} , max update {np.max(np.abs(change_in_update))}')
#         _log.append(f"it {i} , max update {np.max(np.abs(change_in_update))}")
#
#         # relaxed updates converge quicker
#         efth = update_rate * new_estimate + (1 - update_rate) * efth
#
#         # scale to original m0
#
#         if is_oned:
#             m0_cont = -np.trapz(center, efth.data, axis=-1)
#             scale = m0_bins / m0_cont
#             efth *= scale
#         else:
#             # m0_cont = np.trapz(center, efth.data)
#
#             m0_cont = np.trapz(efth, center)
#
#             # avoid division by very small numbers
#             m0_bins_copy = m0_bins.copy()
#             m0_bins_copy[m0_cont <= 1e-9] = 1
#             m0_cont[m0_cont <= 1e-9] = 1
#
#             # scale contains all dims except frequency
#             scale = m0_bins_copy / m0_cont
#
#             # Is this the best way to do this? Does not feel very efficient
#             efth = efth * scale[:, np.newaxis]
#
#     if not converged:
#         for l in _log:
#             print(l)
#         raise ValueError(
#             "Convergence criteria not reached - debug into printed above"
#         )
#
#     return center, efth
