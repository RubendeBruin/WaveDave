import copy
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from wavedave.plots.wavespectrum import plot_wavespectrum
from waveresponse import DirectionalSpectrum, WaveSpectrum

from wavedave.to_smooth.convert import to_WaveSpectrum


class Spectra:
    """Holds a series of 'DirectionalSpectrum' objects

    The time is in UTC and is represented as a list of datetime objects
    The report_timezone_UTC_plus is the offset in hours from UTC to the local time and
    is used to convert the time to local time for plots and reports. The time in the
    report timezone is accessed with the property time_in_timezone.

    metadata (optional) is a dictionary with information about the source of the data

    """

    def __init__(self, wavespectra=None, metadata=None):
        """Creates a Spectra object

        optional input:
        wavespectra : xarray.Dataset with the wavespectra format
        """

        self.spectra: list[
            DirectionalSpectrum
        ] = []  # series of DirectionalSpectrum objects
        self.time: list[datetime] = []  # timestamps in datetime format (UTC)

        """Set the timezone for plots and reports"""
        self.report_timezone_UTC_plus: float = 0
        self.report_timezone_name = "UTC"

        # Define the data
        if wavespectra is not None:
            self._create_from_wavespectra(wavespectra)

        if metadata is None:
            metadata = {}

        self.metadata = metadata

    def copy(self):
        """Returns a copy of the object"""
        return copy.deepcopy(self)

    # Fuzzy metadata processing

    def description_source(self):
        """Tries to create a description of the object source - fuzzy"""
        if "source" in self.metadata:
            return self.metadata["source"]
        elif "filename" in self.metadata:
            return str(Path(self.metadata["filename"]).stem)
        else:
            return ""

    # Time management

    @property
    def time_in_timezone(self):
        """Returns the time in the report timezone"""
        # apply timezone by subtracting the offset in hours to the time
        return [t - timedelta(hours=self.report_timezone_UTC_plus) for t in self.time]

    def human_time(self, time: datetime):
        """Returns the time in human-readable format"""
        # apply timezone by adding the offset in hours to the time
        time = time + timedelta(hours=self.report_timezone_UTC_plus)

        return time.strftime("%Y-%m-%d %H:%M")

    def spectrum_number_nearest_to(self, local_time: datetime):
        """Returns the number with time nearest to the given local time"""
        utc_time = local_time + timedelta(hours=self.report_timezone_UTC_plus)

        # find the nearest time (convert to seconds to use abs and argmin)
        time_diff = [abs((t - utc_time).total_seconds()) for t in self.time]
        return np.argmin(time_diff)

    # Properties

    @property
    def _holds_wavespectra(self):
        """Returns True if the object holds wavespectra data"""
        return len(self.spectra) > 0 and isinstance(self.spectra[0], WaveSpectrum)

    @property
    def Hs(self):
        """Significant wave height [m]"""
        assert self._holds_wavespectra, "Hs is not defined for non-WaveSpectrum objects"
        # noinspection PyUnresolvedReferences

        return [ds.hs for ds in self.spectra]

    @property
    def Tp(self):
        """Peak period [s]"""

        assert self._holds_wavespectra, "Tp is not defined for non-WaveSpectrum objects"
        # noinspection PyUnresolvedReferences
        return [ds.tp for ds in self.spectra]

    @property
    def Tz(self):
        """Zero-upcrossing period [s]"""

        return [ds.tz for ds in self.spectra]

    @property
    def dirp(self):
        """Peak direction [degrees]"""

        assert self._holds_wavespectra, "Peak direction is not defined for non-WaveSpectrum objects"
        # noinspection PyUnresolvedReferences
        return [ds.dirp(degrees=True) for ds in self.spectra]

    @property
    def dirm(self):
        """Mean direction [degrees]"""

        assert self._holds_wavespectra, "Mean direction is not defined for non-WaveSpectrum objects"
        # noinspection PyUnresolvedReferences
        return [ds.dirm(degrees=True) for ds in self.spectra]

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
            grid, values = s.spectrum1d(axis=1, freq_hz=True, degrees=True)
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

    # Methods

    # Bandpassing

    def bands(self, split_periods: list[float]):
        """Returns new Spectra objects with the data split in bands of periods [s]"""

        assert np.all(
            np.diff(split_periods) > 0
        ), "The periods should be in increasing order"

        # create the bands
        split_hz = [1 / p for p in split_periods]

        band0 = self.bandpassed(freq_min=split_hz[0])
        bands = [band0]
        for i in range(len(split_hz) - 1):
            bands.append(
                self.bandpassed(freq_min=split_hz[i + 1], freq_max=split_hz[i])
            )
        bands.append(self.bandpassed(freq_max=split_hz[-1]))

        return bands

    def Hs_bands(self, split_periods: list[float]):
        """Returns the significant wave height in bands of periods [s]"""

        bands = self.bands(split_periods)
        return [b.Hs for b in bands]

    def bandpassed(self, freq_min: float = None, freq_max: float = None):
        """Returns a new Spectra object (a copy) with the bandpassed data"""

        # construct new data
        new_spectra = []
        for s in self.spectra:
            new_spectra.append(s.bandpassed(freq_min=freq_min, freq_max=freq_max))

        # create the new object
        new = self.copy()
        new.spectra = new_spectra

        return new

    # Creation methods

    def _create_from_wavespectra(self, wavespectra):
        # Create the data

        in_dirs = wavespectra.dir.values
        in_freq = wavespectra.freq.values

        # strip site (if any)
        if "site" in wavespectra.dims:
            wavespectra = wavespectra.isel(site=0)

        # loop over time
        self.spectra = []
        for i_time in range(len(wavespectra.time)):
            site_ti = wavespectra.isel(time=i_time)

            # make sure that the dimensions are in the right order
            DF = site_ti.transpose("dir", "freq")

            # get the data
            values = DF.spec.efth.data

            # create the spectrum
            ds = to_WaveSpectrum(in_freq, in_dirs, values)

            # add to the list
            self.spectra.append(ds)

        # convert numpy.datetime64 to datetime objects
        self.time = []
        for t in wavespectra.time.data:
            # Convert to datetime
            timestamp = (t - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(
                1, "s"
            )
            self.time.append(datetime.fromtimestamp(timestamp))

    @staticmethod
    def from_octopus(
        filename: Path or str,
    ):
        """Reads an octopus file and returns a Spectra object"""

        filename = Path(filename)
        assert filename.is_file(), f"File {filename} does not exist"
        assert filename.exists(), f"File {filename} does not exist"

        # noinspection PyUnresolvedReferences
        from wavespectra import read_octopus

        try:
            data = read_octopus(str(filename))
        except Exception as e:
            raise ValueError(f"Could not read file {filename} which is expected to be in the 'octopus' format containing 2D spectra.\nGot the following error: {e}")

        return Spectra(wavespectra=data, metadata={"filename": filename})

    @staticmethod
    def from_obscape(
        directory: Path or str,
        start_date: datetime or None = None,
        end_date: datetime or None = None,
    ):
        """Reads an obscape directory and returns a Spectra object"""

        directory = Path(directory)
        assert directory.is_dir(), f"Directory {directory} does not exist"

        # noinspection PyUnresolvedReferences
        from wavespectra import read_obscape

        data = read_obscape(directory, start_date=start_date, end_date=end_date)
        return Spectra(wavespectra=data)

    # Getting LineSources

    def give_linesource(self, y_prop, dir_prop = None, unit = None):
        """Returns a LineSource object"""
        from wavedave.plots.elements import LineSource

        y = getattr(self, y_prop)

        if dir_prop is not None:
            dir = getattr(self, dir_prop)
        else:
            dir = None

        return LineSource(label = y_prop,
                          x = self.time_in_timezone,
                          y = y,
                          dir = dir,
                          datasource_description=self.description_source(),
                          unit = unit)

    def give_Hs_LineSource(self):
        return self.give_linesource("Hs", dir_prop="dirp", unit = "m")

    def give_Tp_LineSource(self):
        return self.give_linesource("Tp", unit = "s")

    # Plotting =====================================================================

    def plot_spectrum_frequencies_over_time(
        self, ax=None, cmap="Blues", seconds=True, levels=None
    ):
        """Plots the frequency data over time"""
        import matplotlib.pyplot as plt

        fig = None
        if ax is None:
            fig, ax = plt.subplots()

        data = self.freq_over_time

        if seconds:
            y_data = 1 / self.freq
            y_label = "Period [s]"
        else:
            y_data = self.freq
            y_label = "Frequency [Hz]"

        # plot the data
        if levels is None:
            levels = np.linspace(data.min(), data.max(), 20)
        ax.contourf(
            self.time_in_timezone, y_data, data.transpose(), cmap=cmap, levels=levels
        )
        ax.set_xlabel("Time")
        ax.set_ylabel(y_label)

        return fig, ax

    def plot_direction_over_time(self, ax=None, cmap="Greys"):
        """Plots the frequency data over time"""
        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots()

        data = self.direction_over_time

        # plot the data
        levels = np.linspace(data.min(), data.max(), 20)
        ax.contourf(
            self.time_in_timezone,
            self.dirs,
            data.transpose(),
            cmap=cmap,
            levels=levels,
        )

        ax.set_xlabel("Time")
        ax.set_ylabel("Direction")

    def plot_spectrum_2d(self, ispec=0, cmap="Purples", title="", ax=None, levels=None):
        """Plots the spectrum at a given time index"""

        above_title = f"{title}{self.human_time(self.time[ispec])}\n"
        return plot_wavespectrum(
            self.spectra[ispec],
            cmap=cmap,
            above_title=above_title,
            ax=ax,
            levels=levels,
        )

    def plot_spectrum_bands(
        self,
        split_periods: list[float],
        fig=None,
        axes=None,
        plot_args=None,
        figsize=None,
        label=None,
        do_quiver=True,
        quiver_color="k",
        quiver_spacing=1,
    ):
        """Plots the significant wave height in bands of periods [s]

        If axes are supplied then those are used to add the plotted lines to

        If not then a new figure is created, and the axes are returned and axis titles are added.


        returns: fig, axes

        fig  : Matplotlib figure
        axes : list of Matplotlib axes
        """

        if plot_args is None:
            plot_args = {}

        bands = self.bands(split_periods)

        n = len(bands)

        add_makeup = False

        if axes is None:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(nrows=n + 1, ncols=1, figsize=figsize)
            add_makeup = True

        spectra = [self] + bands

        for ax, spec in zip(axes, spectra):
            # plot the total wave height at the top
            ax.plot(spec.time_in_timezone, spec.Hs, label=label, **plot_args)

            if do_quiver:
                # add quiver
                directions_deg = spec.dirp

                # quiver needs:
                # x, y, u, v arrays
                # x and y are the position of the arrow
                # u and v are the direction of the arrow

                qx = []
                qy = []
                qu = []
                qv = []
                q_scale = 40

                for i in range(0, len(spec.time), quiver_spacing):
                    qx.append(spec.time_in_timezone[i])
                    qy.append(spec.Hs[i])
                    qu.append(-np.sin(np.radians(directions_deg[i])))
                    qv.append(-np.cos(np.radians(directions_deg[i])))

                ax.quiver(
                    qx,
                    qy,
                    qu,
                    qv,
                    angles="xy",
                    scale_units="width",
                    headaxislength=3,
                    headlength=10,
                    headwidth=6,
                    minlength=0.1,
                    scale=q_scale,
                    width=0.002,
                    color=quiver_color,
                )

        if add_makeup:
            axes[0].set_title("Total Hs")
            axes[0].set_ylabel("Hs [m]")

            for i in range(n):
                if i == 0:
                    axes[i + 1].set_title(f"Periods < {split_periods[i]} s")
                elif i == n - 1:
                    axes[i + 1].set_title(f"Periods > {split_periods[i-1]} s")
                else:
                    axes[i + 1].set_title(
                        f"Periods {split_periods[i-1]} - {split_periods[i]} s"
                    )

            for i in range(1, n):
                # remove tick labels for x axis
                axes[i].set_xticklabels([])

            for a in axes:
                a.set_ylabel("Hs [m]")

            axes[-1].set_xlabel("Time")

        return fig, axes
