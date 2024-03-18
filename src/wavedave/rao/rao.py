"""WaveDave RAO

WaveDave RAOs extend the wave-response RAOs by adding the following features:

- metadata
- load/save to file

"""

import pickle
from pathlib import Path

import waveresponse as wr
from wavedave.plots.wavespectrum import _plot_polar


class RAO(wr.RAO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.description = "Boot 10"
        self.mode = "heave"
        self.response_unit = "m"   # unit of response , so without the /m for waves.

    def save(self, filename):
        """Save the RAO to a file"""
        pickle.dump(self, open(filename, "wb"))

    @classmethod
    def load(cls, filename: str or Path):
        """Load the RAO from a file (pickle format)"""
        return pickle.load(open(filename, "rb"))

    def plot(self, ax=None):
        """Plot the RAO"""
        fig, ax = _plot_polar(self, ax, do_periods=True, cmap="RdPu", max_period=15, levels=None)

        ax.set_title(self.description + f" {self.mode} RAO [{self.response_unit}/m]")

        return fig, ax

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
    dirs = np.linspace(0.0, 360.0, num=16, endpoint=False)

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

    freq, dirs, values = wave.grid(freq_hz=True,degrees=True)

    rao =wr.RAO(freq = freq,
           dirs = dirs,
           vals = values,
                freq_hz=True,
                degrees=True,)


    # plot
    #
    import matplotlib.pyplot as plt
    #
    # # plt.plot(freqs, vals)
    # # plt.show()
    # from wavedave.plots.wavespectrum import plot_wavespectrum
    # plot_wavespectrum(wave)
    # plt.show()

    rao = RAO(freq = freq,
           dirs = dirs,
           vals = values,
                freq_hz=True,
                degrees=True,)

    rao.description = "Boot 11"
    rao.mode = "pitch"
    rao.response_unit = "degrees"

    # save
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        rao.save(tmpdirname + "/rao.pkl")


        rao2 = RAO.load(tmpdirname + "/rao.pkl")
        print(rao2.description)
        print(rao2.mode)
        print(rao2.response_unit)

        # plot
        rao2.plot()

    plt.show()