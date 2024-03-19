"""TimeSeries class for handling time series data.

T0 is stored as datetime object
time is stored as time since T0 in seconds.
signals are stored as numpy arrays in a dictionary.

"""

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

class TimeSeries:

    def __init__(self, T0 : datetime, time : list[float] or np.ndarray, signals : dict, source : dict or None = None):
        """T0 : timestamp of the first data point
        time : time since T0 in seconds
        signals : dictionary with keys as signal names and values as numpy arrays, aligned with time
        source: dictionary with metadata about the source of the data, optional
        """

        if source is None:
            source = dict()
        assert isinstance(source, dict), "source should be a dictionary"

        assert isinstance(T0, datetime), "T0 should be a datetime object"
        assert is_iterable(time), "time should be a sequence"
        assert isinstance(time[0], (int,float)), "time should be a sequence of floats"
        assert isinstance(signals, dict), "signals should be a dictionary"
        for k, v in signals.items():
            assert isinstance(k, str), "keys in signals should be strings"
            assert is_iterable(v), "values in signals should be sequences"
            assert isinstance(v[0], (int, float)), "values in signals should be sequences of floats"
            assert len(v) == len(time), "values in signals should be the same length as time"

        self.T0 = T0
        self.time = time
        self.signals = signals

    @property
    def is_equidistant(self):
        return len(np.unique(np.diff(self.time))) == 1

    @property
    def dt(self):
        """Return the constant time step in seconds, only valid if the time series is equidistant"""
        return self.time[1]

    def make_equidistant(self, interpolate = False):
        """Make the time series equidistant by distributing the data points evenly over the time range
        If interpolate is True, the signals are interpolated to the new time points, else the samples are shifted in time.
        """

        if self.is_equidistant:
            return

        new_time = np.linspace(self.time[0], self.time[-1], len(self.time))

        if interpolate:
            new_signals = dict()
            for k, v in self.signals.items():
                new_signals[k] = np.interp(new_time, self.time, v)
            self.signals = new_signals

        self.time = new_time

    def specdens(self, signal_name : str, **kwargs):
        """Return the spectrum of a signal using scipy.signal.welch

        by default uses a hann window, override by setting window='something' in kwargs

        returns f, Pxx
        """
        from scipy.signal import welch

        if 'window' not in kwargs:
            kwargs['window'] = 'hann'

        f, Pxx = welch(self.signals[signal_name], fs = 1/self.dt,  **kwargs)
        return f, Pxx

    def plot_signal(self, signal_name : str or list or None, ax=None, **kwargs):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()

        if signal_name is None:
            signal_name = list(self.signals.keys())
        elif isinstance(signal_name, str):
            signal_name = [signal_name]

        for signal_name in signal_name:
            ax.plot(self.time, self.signals[signal_name], **kwargs)

        ax.set_xlabel("Time [s]")
        ax.set_ylabel(signal_name)

        return ax

    def __repr__(self):
        return f"TimeSeries(T0 = {self.T0}, time = {self.time}, signals = {self.signals})"

    def plot_wavelet(self, signal_name : str or None = None, ax=None, cmap = 'magma_r', **kwargs):
        """Plot the wavelet of a signal using scipy.signal.cwt
        """

        from scipy.signal import cwt, morlet2

        # note: morlet2 is morlet but then made suitable for the cwt command
        if signal_name is None:
            signal_name = list(self.signals.keys())[0]

        signal = self.signals[signal_name]

        dt = self.dt

        width = np.arange(1,100)
        R = cwt(signal, morlet2, width)

        if ax is None:

            fig, ax = plt.subplots()


        # extent : floats (left, right, bottom, top)
        w = 5   # standard w0 for morlet2 = 5
        fac = 4 * np.pi  / (w + np.sqrt(2+w**2)) # conversion factor
        yy = (100*fac * dt, 0)
        xx = (0, max(self.time))
        extend = (xx[0],xx[1], yy[0],yy[1])
        ps = np.power(abs(R),2)
        ax.imshow(ps,  cmap=cmap, aspect='auto', extent =extend)
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Period [s]')

        # plot the spectral density on the left
        spec = np.sum(ps, axis=1)

        # scale to 1/10th of the width of the graph
        scale = 0.1 * xx[1] / np.max(spec)

        ax.plot(scale * spec, np.linspace(yy[1],yy[0], num=len(spec)), color = 'black', linewidth = 1)

        return ax

    def plot(self, signal_name : str or None or int = None):

        if signal_name is None:
            signal_name = list(self.signals.keys())[0]

        if isinstance(signal_name, int):
            signal_name = list(self.signals.keys())[signal_name]

        fig, ax = plt.subplots(2,1, figsize = (10,6))

        self.plot_signal(signal_name, ax = ax[0], color = 'purple', linewidth = 1)
        self.plot_wavelet(signal_name, ax = ax[1])

        # make the x-axis of the top plot invisible
        ax[0].set_xticklabels([])
        ax[0].set_xlabel('')

        ax[0].set_title(f"{signal_name}, its wavelet and spectral density (welch and from wavelet), f = {1/self.dt:.2f} hz")

        ax[0].set_xlim([0, max(self.time)])
        ax[1].set_xlim([0, max(self.time)])

        f, S = self.specdens(signal_name)
        f[f==0] = 1e-10 # avoid division by zero

        # scale
        yy = ax[1].get_ylim()
        scale = 0.1 * max(self.time)/ np.max(S)
        S = scale * S
        ax[1].set_ylim(yy)

        ax[1].plot(S, 1/f, color = 'purple', linewidth = 1)


        fig.tight_layout()

        from wavedave.plots.helpers import apply_default_style
        apply_default_style(fig, ax)