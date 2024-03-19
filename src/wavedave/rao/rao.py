"""WaveDave RAO

WaveDave RAOs extend the wave-response RAOs by adding the following features:

- metadata
- load/save to file

"""

import pickle
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

import waveresponse as wr
from wavedave.plots.wavespectrum import _plot_polar


class RAO(wr.RAO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.description = "Boot 10"
        self.mode = "heave"
        self.response_unit = "m"  # unit of response , so without the /m for waves.

    def save(self, filename):
        """Save the RAO to a file"""
        pickle.dump(self, open(filename, "wb"))

    @classmethod
    def load(cls, filename: str or Path):
        """Load the RAO from a file (pickle format)"""
        return pickle.load(open(filename, "rb"))

    def plot(self, ax=None):
        """Plot the RAO"""
        fig, ax = _plot_polar(
            self, ax, do_periods=True, cmap="RdPu", max_period=15, levels=None
        )

        ax.set_title(self.description + f" {self.mode} RAO [{self.response_unit}/m]")

        return fig, ax

    def plot1d(self, direction: float, ax=None):
        """Plot the RAO"""

        i_direction = np.where(self.dirs(degrees=True) == direction)[0][0]
        freqs, _, c = self.grid(freq_hz=True, degrees=True)
        c = c[:, i_direction]

        amp = abs(c)
        phase = np.angle(c)

        fig, ax = plt.subplots(2, 1, sharex=True)
        ax[0].plot(freqs, amp)
        ax[0].set_title(
            f"{self.description} {self.mode} RAO [{self.response_unit}/m] at {direction} degrees"
        )
        ax[0].set_ylabel("Amplitude")
        ax[0].set_xlabel("Frequency [Hz]")
        ax[1].plot(freqs, phase, "r.")
        ax[1].set_ylabel("Phase [rad]")
        ax[1].set_xlabel("Frequency [Hz]")

    @staticmethod
    def test_rao(peak=2, freqs=None):
        """Create a test RAO"""


        peak = 2  # m
        freqs = np.linspace(1 / 100, 1, 20)  # hZ

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

        freq, dirs, values = wave.grid(freq_hz=True, degrees=True)

        # make complex
        phase = np.linspace(0, 4 * np.pi, len(freq))
        values = (
            np.outer(1j * np.cos(phase), np.ones((len(dirs)))) * values
            + np.outer(np.sin(phase), np.ones(len(dirs))) * values
        )

        print(np.angle(values[:, 1]))

        rao = RAO(
            freq=freq,
            dirs=dirs,
            vals=values,
            freq_hz=True,
            degrees=True,
        )

        rao.description = "Boot 11"
        rao.mode = "pitch"
        rao.response_unit = "degrees"

        return rao


if __name__ == "__main__":

    rao = RAO.test_rao()

    rao.plot1d(direction=0)

    from waveresponse._core import _sort

    rao._dirs, rao._vals = _sort(rao._dirs, rao._vals)

    new_frequencies = np.linspace(1 / 200, 1, 100)
    rao = rao.reshape(
        freq=new_frequencies,
        freq_hz=True,
        dirs=rao.dirs(),
        degrees=True,
        complex_convert="polar",
    )

    # save
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        rao.save(tmpdirname + "/rao.pkl")

        rao2 = RAO.load(tmpdirname + "/rao.pkl")
        print(rao2.description)
        print(rao2.mode)
        print(rao2.response_unit)

        rao.plot1d(direction=0)
    # rao2.plot1d(direction=0)
    plt.show()
