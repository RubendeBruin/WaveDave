import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from ..pdf.document import WaveDavePDF
from ..plots.helpers import faded_line_color, sync_yscales, apply_default_style
from ..spectra import Spectra


@dataclass
class MetoceanSource:
    description: str
    data: list[Spectra]
    is_buoy: bool = False




class MetoceanReport:
    def __init__(self):
        self.header_text = "Metocean Report"
        self._sources: list[MetoceanSource] = []

        self.events: list[Event] = []


        #
        self.title = "Title"
        self.date = "Yesterday"
        self.project = "Project"
        self.author = "Author"


        # ===== Colors ======

        blue = (40 / 255, 40 / 255, 92 / 255)
        yellow = (255 / 255, 214 / 255, 0 / 255)
        colors = ["white", yellow, blue]

        self.cmap = LinearSegmentedColormap.from_list("metocean", colors)
        self.color = blue
        self.color_accent = yellow
        self.color_buoy_quiver = (255 / 500, 214 / 500, 0 / 500)

        # ===== Integrated fcst =====

        self.integrated_forecast = None
        self.integrated_plots = []
        self.integrated_figsize: tuple[float, float] = (
            8,
            10,
        )  # this is the size of the figure before it is added to the pdf

        self.integrated_text_offset = 17  # space between left margin and text
        self.integrated_text_above = "This is the data from the .csv forecast.<p>"
        self.integrated_text_below = (
            "It does not always match the spectral forecast.<br>The spectral forecast is model output. "
            "The integrated forecast may have had an additional human touch.<p>"
        )

        self.integrated_show_events = True

        # ===== Breakdown =====

        self.breakdown = True
        self.breakdown_figsize: tuple[float, float] = (
            8,
            9,
        )  # this is the size of the figure before it is added to the pdf
        self.breakdown_split_periods_s: list[float] = [3.0, 6.0]
        self.breakdown_y_synced = True  # all axis have same y range

        self.breakdown_text_offset = 17  # space between left margin and text
        self.breakdown_text_above = ""
        self.breakdown_text_below = ""

        self.breakdown_show_events = True

        self.breakdown_directions_forecast = True
        self.breakdown_directions_buoy = True
        self.breakdown_directions_buoy_spacing = 10  # one arrow every .... samples

        # ====== Energy [ Spectral Energy Map And Roseplots] ======
        #                 based on forecast only

        self.energy = True
        self.energy_source_i = 0

        self.energy_figsize: tuple[float, float] = (
            10.0,
            10.0,
        )  # this is the size of the figure before it is added to the pdf
        self.energy_n_cols = 3

        self.energy_text_offset = 17
        self.energy_text_above = ""
        self.energy_text_below = ""

    def add_source(self, source: MetoceanSource):
        self._sources.append(source)

    def generate_report(self):
        report = WaveDavePDF()
        report.title = self.title
        report.author = self.author
        report.project = self.project
        report.date = self.date

        if self.integrated_forecast:
            self._add_integrated_forecast(report)

        if self.breakdown:
            self._add_breakdown(report)

        if self.energy:
            self._add_energy(report, self._sources[self.energy_source_i])

        return report

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

    def _add_integrated_forecast(self, report):
        n = len(self.integrated_plots)

        fig, axes = plt.subplots(n, 1, figsize=self.integrated_figsize)

        for i, (ax, columns) in enumerate(zip(axes, self.integrated_plots)):
            x = self.integrated_forecast.time
            if isinstance(columns, str):
                if columns not in self.integrated_forecast.columns:
                    raise ValueError(
                        f"Column {columns} not found in the integrated forecast, we have {self.integrated_forecast.columns}"
                    )

                y = self.integrated_forecast.data[columns]
                ax.plot(x, y, color=self.color)
                ax.set_title(" ".join(columns.split()[:-1]))
                ax.set_ylabel(columns.split()[-1])

            else:  # line and quiver
                y = self.integrated_forecast.data[columns[0]]
                dir = self.integrated_forecast.data[columns[1]]

                ax.plot(x, y, color=self.color)
                ax.set_title(" ".join(columns[0].split()[:-1]))
                ax.set_ylabel(columns[0].split()[-1])

                qx = []
                qy = []
                qu = []
                qv = []
                q_scale = 40

                for i in range(0, len(x), 5):
                    qx.append(x[i])
                    qy.append(y[i])
                    qu.append(-np.sin(np.radians(dir[i])))
                    qv.append(-np.cos(np.radians(dir[i])))

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
                    color=self.color,
                )

        if self.integrated_show_events:
            self._add_events(axes)

        for ax in axes:
            ax.set_ylim(bottom=0)
        apply_default_style(fig, axes)

        fig.tight_layout()

        filename = report.temp_folder / "integrated_forecast.svg"

        fig.savefig(str(filename))

        left_space = self.breakdown_text_offset

        report.add_new_page_if_needed()

        report.set_x(report.l_margin + left_space)
        report.write_html(self.integrated_text_above)

        report.set_x(report.l_margin)
        report.image(filename, w=report.epw)
        report.set_x(report.l_margin + left_space)
        report.write_html(self.integrated_text_below)

        return report

    def _add_breakdown(self, report):
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
                    do_quiver = self.breakdown_directions_buoy
                    quiver_spacing = self.breakdown_directions_buoy_spacing
                else:
                    color = faded_line_color(i / n_series)
                    plot_args["color"] = color
                    quiver_color = color
                    do_quiver = self.breakdown_directions_forecast
                    quiver_spacing = 1

                counter += 1
                fig, axes = data.plot_spectrum_bands(
                    figsize=self.breakdown_figsize,
                    fig=fig,
                    axes=axes,
                    split_periods=self.breakdown_split_periods_s,
                    plot_args=plot_args,
                    label=source.description + " " + data.description_source(),
                    do_quiver=(i == 0) and do_quiver,
                    quiver_spacing=quiver_spacing,
                    quiver_color=quiver_color,
                )

        # add legend below lowest axes

        axes[-1].legend(
            loc="lower left", bbox_to_anchor=(0, -counter * 0.3), frameon=False
        )

        # events

        if self.breakdown_show_events:
            self._add_events(axes)

        # makeup
        if self.breakdown_y_synced:
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

        left_space = self.breakdown_text_offset

        report.add_new_page_if_needed()

        report.set_x(report.l_margin + left_space)
        report.write_html(self.breakdown_text_above)

        report.set_x(report.l_margin)
        report.image(filename, w=report.epw)
        report.set_x(report.l_margin + left_space)
        report.write_html(self.breakdown_text_below)

        return report

    def _add_energy(self, report, data: MetoceanSource):
        source = data.data[0]

        # first make a figure with the size that we like
        n_roses = len(self.events)
        n_cols = self.energy_n_cols  # alias
        n_rows = int(np.ceil(n_roses / n_cols) + 1)

        fig, ax = plt.subplots(
            nrows=n_rows,
            ncols=n_cols,
            figsize=self.energy_figsize,
            subplot_kw={"projection": "polar"},
        )

        # merge the top-row into one single axis
        gs = ax[0, 0].get_gridspec()
        for a in ax[0, :]:
            a.remove()
        top_axis = fig.add_subplot(gs[0, :])

        # plot the spectral energy map
        source.plot_spectrum_frequencies_over_time(cmap=self.cmap, ax=top_axis)
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
            nearest_i = source.spectrum_number_nearest_to(local_time=x)

            x = source.time_in_timezone[nearest_i]

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
            _, _, rose_data = source.spectra[nearest_i].grid(freq_hz=True, degrees=True)
            max_rose = max(max_rose, np.nanmax(rose_data))

        # Determine the levels and plot all using the same levels
        levels = np.linspace(0, max_rose, 20)
        for i, (event, nearest_i) in enumerate(zip(self.events, i_nearests)):
            source.plot_spectrum_2d(
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

        left_space = self.energy_text_offset

        report.add_new_page_if_needed()

        report.set_x(report.l_margin + left_space)
        report.write_html(self.energy_text_above)

        report.set_x(report.l_margin)
        report.image(filename, w=report.epw)
        report.set_x(report.l_margin + left_space)

        report.write_html(self.energy_text_below)
