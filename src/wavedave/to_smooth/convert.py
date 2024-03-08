import numpy as np
from waveresponse import DirectionalSpectrum, WaveSpectrum

from wavedave.to_smooth.smooth_old import to_continuous_1d




def to_WaveSpectrum(freq, dir, data):
    """Converts the spectral data to a continuous spectrum

    wavespectrum: a 'wavespectra' object for a single spectrum
    """

    n_freq = len(freq)
    n_dir = len(dir)
    assert data.shape == (n_dir, n_freq)

    # make smooth 1d spectra

    spec2d = []
    for i_dir in range(n_dir):
        x, y = to_continuous_1d(freq, data[i_dir, :])
        spec2d.append(y)

    # order directions from 0 to 360
    dir = dir % 360
    idx = np.argsort(dir)
    dir = dir[idx]
    spec2d_np = np.array(spec2d)[idx, :]


    # add a zero direction if needed
    if 0 not in dir:
        # get the lowest and highest direction
        d_low = dir[0]
        d_high = 360 - dir[-1]

        d = d_low + d_high
        f_low = d_low / d
        f_high = d_high / d

        # interpolate the zero direction
        spec2d_np = np.vstack([f_low * spec2d_np[-1, :] + f_high * spec2d_np[0, :], spec2d_np])

        dir = np.append(0, dir)

    ds = WaveSpectrum(freq=freq, dirs=dir, vals=spec2d_np.transpose(), degrees = True)

    return ds





