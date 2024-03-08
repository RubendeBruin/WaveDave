import numpy as np
def bins_from_frequency_grid(bin_centers, absolute_tolerance=1e-3):
    """Determines the location of the edges of bins from the provided bin centers.

    Detects the pre-coded common frequency grids:
    - exponential grids
    - datawell waverider grid


    constant grids:
    - delta between frequencies is constant

    exponential grids:
    - frequencies are at  c1 * exp(c2 * i); bin edges are at

    Args:
        bin_centers : iterable [Hz or rad/s]
        absolute_tolerance : maximum absolute deviation in frequency step

    Returns:
        left, right, width : bin edges and bin widths [Hz rad/s, same as input]

    """

    freqs = np.array(bin_centers, dtype=float)
    nfreqs = len(freqs)

    # Check if the frequency grid is constant
    width = np.diff(freqs)
    if (np.max(width) - np.min(width)) < absolute_tolerance:
        centers = np.linspace(min(freqs), max(freqs), nfreqs)
        left = centers - 0.5 * np.mean(width)
        right = centers + 0.5 * np.mean(width)
        width = right - left
        return left, right, width, centers

    # Grid is not constant.
    # Check it the frequency grid is exponential
    #
    # to determine the bin-size we need to re-construct the original bin boundaries
    #
    # c2 is the n-log of the frequency increase factor
    # take the average to minimize the effect of lack of significant digits

    # Check it the frequency grid is exponential
    # freq_center_i = c1 * exp(c2 * i)

    increase_factor = np.mean(freqs[1:] / freqs[:-1])
    c2 = np.log(increase_factor)

    # determine c1 from the highest bin
    c1 = freqs[-1] / np.exp(c2 * nfreqs)

    # check the assumptions
    ifreq = np.arange(1, nfreqs + 1)
    freq_check = c1 * np.exp(c2 * ifreq)

    difference = freqs - freq_check
    max_difference = np.max(np.abs(difference))

    if max_difference < absolute_tolerance:
        # we have an exponential grid

        left = c1 * np.exp(c2 * (ifreq - 0.5))
        right = c1 * np.exp(c2 * (ifreq + 0.5))
        width = right - left
        centers = freq_check

        return left, right, width, centers

    # grid is not exponential and not constant

    raise ValueError(
        "The type of frequency grid can not be detected. Clean input data or increase tolerance?"
    )

def bin_drawing_coordinates(freq, values):
    """Converts the spectral data to coordinates for drawing bins.

    Args:
        freq : iterable [Hz or rad/s]
        values : iterable [m2/Hz or m2 s/rad]

    Returns:
        x, y : coordinates for drawing bins
    """

    left, right, width, centers = bins_from_frequency_grid(freq)

    x = []
    y = []

    for l,r,v in zip(left, right, values):
        x.extend([l, r])
        y.extend([v, v])

    return x, y

def bin_m0(freq, values):
    """Calculates the zeroth moment of the spectral density.

    Args:
        freq : iterable [Hz or rad/s]
        values : iterable [m2/Hz or m2 s/rad]

    Returns:
        m0 : zeroth moment [m2 or m2 s]
    """

    left, right, width, centers = bins_from_frequency_grid(freq)

    return np.sum(width * values, axis=-1)

