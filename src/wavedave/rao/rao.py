"""WaveDave RAO

WaveDave RAOs extend the wave-response RAOs by adding the following features:

- metadata
- load/save to file

"""

import pickle
from pathlib import Path

import waveresponse as wr


class RAO(wr.RAO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        description = "Boot 10"
        mode = "heave"
        response_unit = "m"   # unit of response , so without the /m for waves.

    def save(self, filename):
        """Save the RAO to a file"""
        pickle.dump(self, open(filename, "wb"))

    @classmethod
    def load(cls, filename: str or Path):
        """Load the RAO from a file (pickle format)"""
        return pickle.load(open(filename, "rb"))


if __name__ == "__main__":
    # Example usage

    # Create a RAO
    #

    import numpy as np

    peak = 2  # m
    freqs = np.linspace(1 / 100, 1, 100)  # hZ

    # use a jonswap shape as RAO example
    js = wr.JONSWAP(freqs, freq_hz=True)
    _, vals = js(hs=2, tp=10, gamma=5)

    # scale the peak
    scale = peak / np.max(vals)
    vals *= scale

    spread_fun = wr.CosineFullSpreading(s=2, degrees=True)
    dirs = np.linspace(0.0, 180.0, num=16, endpoint=False)

    wave = wr.WaveSpectrum.from_spectrum1d(
        freqs,
        dirs,
        vals,
        spread_fun,
        0,
        freq_hz=True,
        degrees=True,
        clockwise=False,
        waves_coming_from=False,
    )

    rao =wr.RAO(freq_hz=True,
           freq = wave.freq,
           dirs = wave.dirs,
           vals = wave.vals,)

    rao.a

    # plot
    #
    import matplotlib.pyplot as plt
    #
    # plt.plot(freqs, vals)
    # plt.show()
    from wavedave.plots.wavespectrum import plot_wavespectrum
    plot_wavespectrum(wave)
    plt.show()

    # rao = RAO()
