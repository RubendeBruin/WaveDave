from dataclasses import dataclass
from abc import abstractmethod

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .. import Event
from ..pdf.document import WaveDavePDF, ToPDFMixin
from ..plots.helpers import faded_line_color, sync_yscales, apply_default_style
from ..spectra import Spectra

import wavedave.settings as Settings


@dataclass
class MetoceanSource:
    description: str
    data: list[Spectra]
    is_buoy: bool = False


class StandardSection(ToPDFMixin):
    def __init__(self):
        self.header_text = "Metocean Report"

        self.events: list[Event] = []

        colors = ["white", Settings.COLOR_SECONDARY, Settings.COLOR_MAIN]
        self.cmap = LinearSegmentedColormap.from_list("metocean", colors)

        self.color_accent = Settings.COLOR_SECONDARY
        self.color_buoy_quiver = [c / 2 for c in Settings.COLOR_SECONDARY]

        self.figsize: tuple[float, float] = (
            8,
            9,
        )  # this is the size of the figure before it is added to the pdf

        self.y_synced = True  # all axis have same y range

        self.text_offset = 17  # space between left margin and text
        self.text_above = ""
        self.text_below = ""

        self.directions_forecast = True
        self.directions_buoy = True
        self.directions_buoy_spacing = 5  # one arrow every .... samples



    def _add_events(self, axes):
        for event in self.events:
            x = event.when
            for ax in axes:
                ax.axvline(x, color="black", linestyle="--", linewidth=0.8)

            # add text only to the first axis
            ax = axes[0]
            yy = ax.get_ylim()
            py = 0.95 * yy[1]

            ax.text(
                x,
                py,
                event.description,
                font="Arial",
                fontsize=10,
                rotation=90,
                ha="center",
                va="top",
                backgroundcolor="white",
            )

    @abstractmethod
    def render_figure(self, report: WaveDavePDF):
        raise ValueError("Abstract - This method should be overridden")

    def generate_pdf(self, report: WaveDavePDF):
        report._add_new_page_if_needed()

        report.set_x(report.l_margin + self.text_offset)
        report.write_html(self.header_text)

        self.render_figure(report)

        report.set_x(report.l_margin + self.text_offset)
        report.write_html(self.text_below)

        return report


class BreakdownSection(StandardSection):
    def __init__(self):
        super().__init__()

        self.split_periods_s: list[float] = [3.0, 6.0]
        self._sources: list[MetoceanSource] = []

    def add_source(self, source: MetoceanSource):
        self._sources.append(source)

    def render_figure(self, report):
        fig = None
        axes = None

        counter = 0
        for source in self._sources:
            n_series = len(source.data)

            if source.is_buoy:
                assert n_series == 1, "Only one series is allowed for a buoy"

            for i, data in enumerate(source.data):
                plot_args = dict()

                if source.is_buoy:
                    plot_args["marker"] = "."
                    plot_args["color"] = self.color_accent
                    plot_args["markeredgecolor"] = "k"
                    plot_args["linestyle"] = "none"
                    quiver_color = self.color_buoy_quiver
                    do_quiver = self.directions_buoy
                    quiver_spacing = self.directions_buoy_spacing
                else:
                    color = faded_line_color(i / n_series)
                    plot_args["color"] = color
                    quiver_color = color
                    do_quiver = self.directions_forecast
                    quiver_spacing = 1

                counter += 1

                fig, axes = data.plot_spectrum_bands(
                    figsize=self.figsize,
                    fig=fig,
                    axes=axes,
                    split_periods=self.split_periods_s,
                    plot_args=plot_args,
                    label=source.description + " " + data.description_source(),
                    do_quiver=(i == 0) and do_quiver,
                    quiver_spacing=quiver_spacing,
                    quiver_color=quiver_color,
                )

        # add legend below lowest axes

        axes[-1].legend(loc="upper left", bbox_to_anchor=(0, -0.2), frameon=False)

        # events

        self._add_events(axes)

        # makeup
        if self.y_synced:
            sync_yscales(axes)
        else:
            # at least set all the zeros to zero
            for ax in axes:
                ax.set_ylim(bottom=0)

        apply_default_style(fig, axes)
        fig.subplots_adjust(bottom=0.2)
        fig.tight_layout()

        filename = report.temp_folder / "breakdown.svg"
        fig.savefig(str(filename))

        report.set_x(report.l_margin)
        report.image(filename, w=report.epw)


class EnergySection(StandardSection):
    def __init__(self, spectra : Spectra):
        super().__init__()
        self.n_cols = 3
        self.spectra = spectra

    def render_figure(self, report):


        # first make a figure with the size that we like
        n_roses = len(self.events)
        n_cols = self.n_cols  # alias
        n_rows = int(np.ceil(n_roses / n_cols) + 1)

        fig, ax = plt.subplots(
            nrows=n_rows,
            ncols=n_cols,
            figsize=self.figsize,
            subplot_kw={"projection": "polar"},
        )

        # merge the top-row into one single axis
        gs = ax[0, 0].get_gridspec()
        for a in ax[0, :]:
            a.remove()
        top_axis = fig.add_subplot(gs[0, :])

        # plot the spectral energy map
        self.spectra.plot_spectrum_frequencies_over_time(cmap=self.cmap, ax=top_axis)
        rose_axes = ax.flatten()[n_cols:]

        # plot roses at the the events
        #
        # events are moved to the nearest datapoint
        # all roses have the same color-scale, which is different from the spectral energy map scale. This is
        # because they have different units. One is per degree*hZ and the other is only per hz.

        i_nearests = []
        max_rose = 0
        for i, event in enumerate(self.events):
            x = event.when
            nearest_i = self.spectra.spectrum_number_nearest_to(local_time=x)

            x = self.spectra.time_in_timezone[nearest_i]

            top_axis.axvline(x, color="black", linestyle="--", linewidth=0.8)

            yy = top_axis.get_ylim()
            py = 0.95 * yy[1]

            top_axis.text(
                x,
                py,
                event.description,
                font="Arial",
                fontsize=10,
                rotation=90,
                ha="right",
                va="top",
            )

            # get data for levels
            i_nearests.append(nearest_i)
            _, _, rose_data = self.spectra.spectra[nearest_i].grid(freq_hz=True, degrees=True)
            max_rose = max(max_rose, np.nanmax(rose_data))

        # Determine the levels and plot all using the same levels
        levels = np.linspace(0, max_rose, 20)
        for i, (event, nearest_i) in enumerate(zip(self.events, i_nearests)):
            self.spectra.plot_spectrum_2d(
                nearest_i,
                cmap=self.cmap,
                ax=rose_axes[i],
                title=event.description + "\n",
                levels=levels,
            )

        # remove the empty axes
        for i in range(n_roses, len(rose_axes)):
            rose_axes[i].remove()
        rose_axes = rose_axes[:n_roses]

        apply_default_style(fig, top_axis)
        apply_default_style(fig, rose_axes)
        fig.tight_layout()

        filename = report.temp_folder / "energy.svg"
        fig.savefig(str(filename))
        report.set_x(report.l_margin)
        report.image(filename, w=report.epw)
