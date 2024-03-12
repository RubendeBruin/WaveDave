from datetime import datetime
from pathlib import Path

import numpy as np

from wavedave.plots.wavespectrum import plot_wavespectrum
from waveresponse import DirectionalSpectrum

from wavedave.to_smooth.convert import to_WaveSpectrum


class Spectra:
    """Holds a series of 'DirectionalSpectrum' objects"""

    def __init__(self, wavespectra =None):
        """Creates a Spectra object

        optional input:
        wavespectra : xarray.Dataset with the wavespectra format
        """

        self.spectra : list[DirectionalSpectrum] = []  # series of DirectionalSpectrum objects
        self.time = []     # timestamps in datetime format

        # Define the data
        if wavespectra is not None:
            self._create_from_wavespectra(wavespectra)

## Properties

    @property
    def Hs(self):
        """Significant wave height [m]"""
        return [ds.hs for ds in self.spectra]

    @property
    def Tp(self):
        """Peak period [s"""
        return [ds.tp for ds in self.spectra]

    @property
    def Tz(self):
        """Zero-upcrossing period [s]"""
        return [ds.tz for ds in self.spectra]

    @property
    def dirs(self):
        """Wave directions [degrees]"""
        return self.spectra[0].dirs(degrees=True)

    @property
    def freq(self):
        """Wave frequencies [Hz]"""
        return self.spectra[0].freq(freq_hz=True)

# Squashed properties

    @property
    def freq_over_time(self):
        """Returns the frequency data over time

        :returns: 2D array with the frequency data over time
        axis 0 : time
        axis 1 : frequency
        """

        R = []
        for s in self.spectra:
            grid, values = s.spectrum1d(axis=1)
            R.append(values)

        return np.array(R, dtype=float)

    @property
    def direction_over_time(self):
        """Returns the direction data over time

        :returns: 2D array with the frequency data over time
        axis 0 : time
        axis 1 : frequency
        """

        R = []
        for s in self.spectra:
            grid, values = s.spectrum1d(axis=0)
            R.append(values)

        return np.array(R, dtype=float)

    def Hs_bands(self, split_periods : list[float]):
        """Returns the significant wave height in bands of periods [s]

        shape(n_bands, n_spectra)"""

        # assert that the periods are in the right order
        assert np.all(np.diff(split_periods) > 0), "The periods should be in increasing order"

        # create the bands
        split_hz = 1/np.array(split_periods)

        bands = [(np.inf, split_hz[0])]
        for i in range(len(split_hz)-1):
            bands.append((split_hz[i], split_hz[i+1]))
        bands.append((split_hz[-1], 0))

        # new grid with datapoints at the splits
        new_grid = np.concatenate([self.freq, split_hz])
        new_grid.sort()

        # pre-alloc
        n_bands = len(bands)
        R = np.zeros((n_bands,len(self.spectra)))

        # fill
        for i_spec,s in enumerate(self.spectra):

            # squash to non-directional
            grid, values = s.spectrum1d(axis=1)

            # add splits using interpolation
            new_values = np.interp(new_grid, grid, values)

            for i_band,band in enumerate(bands):
                idx = (new_grid <= band[0]) & (new_grid >= band[1])
                m0 = np.trapz(new_values[idx], new_grid[idx])
                R[i_band,i_spec] = 4 * np.sqrt(m0)

        return R








            ## Creation methods

    def _create_from_wavespectra(self, wavespectra):
        # Create the data

        in_dirs = wavespectra.dir.values
        in_freq = wavespectra.freq.values

        # strip site (if any)
        if 'site' in wavespectra.dims:
            wavespectra = wavespectra.isel(site=0)

        # loop over time
        self.spectra = []
        for i_time in range(len(wavespectra.time)):
            site_ti = wavespectra.isel(time=i_time)

            # make sure that the dimensions are in the right order
            DF = site_ti.transpose('dir', 'freq')

            # get the data
            values = DF.spec.efth.data

            # create the spectrum
            ds = to_WaveSpectrum(in_freq, in_dirs, values)

            # add to the list
            self.spectra.append(ds)

        self.time = wavespectra.time.data

    @staticmethod
    def from_octopus(filename : Path or str, ):
        """Reads an octopus file and returns a Spectra object"""

        filename = Path(filename)
        assert filename.is_file(), f"File {filename} does not exist"
        assert filename.exists(), f"File {filename} does not exist"

        from wavespectra import read_octopus
        data = read_octopus(str(filename))

        return Spectra(wavespectra=data)

    @staticmethod
    def from_obscape(directory : Path or str,
                     start_date : datetime or None = None,
                     end_date : datetime or None = None):
        """Reads an obscape directory and returns a Spectra object"""

        directory = Path(directory)
        assert directory.is_dir(), f"Directory {directory} does not exist"

        from wavespectra import read_obscape
        data = read_obscape(directory,
                            start_date = start_date,
                            end_date = end_date)
        return Spectra(wavespectra=data)

## Plotting

    def plot_spectrum_frequencies_over_time(self, ax = None, cmap = 'Blues', seconds=True):
        """Plots the frequency data over time"""
        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots()

        data = self.freq_over_time

        if seconds:
            y_data = 1/self.freq
            y_label = 'Period [s]'
        else:
            y_data = self.freq
            y_label = 'Frequency [Hz]'

        # plot the data
        ax.contourf(self.time, y_data, data.transpose(), cmap=cmap)
        ax.set_xlabel('Time')
        ax.set_ylabel(y_label)

    def plot_direction_over_time(self, ax = None, cmap = 'Greys'):
        """Plots the frequency data over time"""
        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots()

        data = self.direction_over_time

        # plot the data
        ax.contourf(self.time, self.dirs, data.transpose(), cmap=cmap)
        ax.set_xlabel('Time')
        ax.set_ylabel('Direction')

    def plot_spectrum_2d(self, ispec = 0 , cmap = 'Purples'):
        """Plots the spectrum at a given time index"""
        plot_wavespectrum(self.spectra[ispec], cmap=cmap)

    def plot_spectrum_bands(self, split_periods : list[float], axes = None, plot_args = None):
        """Plots the significant wave height in bands of periods [s]

        If axes are supplied then those are used to add the plotted lines to

        If not then a new figure is created, and the axes are returned and axis titles are added.
        """

        if plot_args is None:
            plot_args = {}

        bands = self.Hs_bands(split_periods)

        n = len(bands)

        add_makeup = False
        fig = None
        if axes is None:
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(nrows=n+1, ncols=1)

            add_makeup = True

        # plot the total wave height at the top
        axes[0].plot(self.time, self.Hs, **plot_args)

        for i in range(n):
            axes[i+1].plot(self.time, bands[i], **plot_args)

        if add_makeup:

            axes[0].set_title('Total Hs')
            axes[0].set_ylabel('Hs [m]')

            for i in range(n):
                if i==0:
                    axes[i+1].set_title(f'Periods < {split_periods[i]} s')
                elif i == n-1:
                    axes[i+1].set_title(f'Periods > {split_periods[i-1]} s')
                    axes[i+1].set_xlabel('Time')
                else:
                    axes[i+1].set_title(f'{split_periods[i-1]} - {split_periods[i]} s')

                axes[i+1].set_ylabel('Hs band [m]')

        return fig, axes