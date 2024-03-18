from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np

from wavedave.pdf.document import ToPDFMixin, WaveDavePDF
from wavedave.plots.helpers import sync_yscales, apply_default_style, faded_line_color


# sig, max20 , max30, max3h
# single, double


class StatisticsType(Enum):
    NONE = 0
    STD = 1
    SAS = 2  # single amplitude significant
    DAS = 3
    SM20 = 4  # single amplitude max 20
    DM20 = 5
    SM30 = 6
    DM30 = 7
    SM3H = 8
    DM3H = 9


# Determines how multiple plots below each other should share x-axis limits
#
class SharedX(Enum):
    NONE = 0
    UNION = 1
    INTERSECTION = 2


# Event is a vertical line in the graph, annotated with a text
@dataclass
class Event:
    description: str
    when: datetime

    def __post_init__(self):
        assert isinstance(self.when, datetime), "when must be a datetime object, for example datetime(2024, 7, 26,12,0,0)"
        assert isinstance(self.description, str), "description must be a string"

    def render(self, ax, text=True):
        x = self.when
        ax.axvline(x=self.when, color="k", linestyle="--", linewidth=1)

        # add text only to the first axis
        if text:
            yy = ax.get_ylim()
            py = (0.95 * yy[1] - yy[0]) + yy[0]

            ax.text(
                x,
                py,
                self.description,
                font="Arial",
                fontsize=10,
                rotation=90,
                ha="center",
                va="top",
                backgroundcolor="white",
            )


# Limit is a constant horizontal line in the graph, annotated with a text
@dataclass
class Limit:
    description: str
    value: float

    def __post_init__(self):
        assert isinstance(self.value, (float,int)), f"value must be a number, for example 1.5, got {self.value}"
        assert isinstance(self.description, str), "description must be a string"

    def render(self, ax):
        ax.axhline(self.value, color="k", linestyle="--", linewidth=1)

        xx = ax.get_xlim()
        x = 1.02 * (xx[1] - xx[0]) + xx[0]
        # x = xx[1]

        ax.text(
            x,
            self.value,
            self.description,
            font="Arial",
            fontsize=10,
            ha="left",
            va="center",
            backgroundcolor="white",
        )


@dataclass
class LineSource:
    label: str

    x: list[datetime]
    y: list[float]

    datasource_description: str = ""  # for example the filename

    unit: str = ""

    statistics_type: StatisticsType = StatisticsType.NONE

    direction: list[
        float
    ] or None = None  # dir is going to with 0 = up, 90 = right, 180 = down, 270 = left

    dir_plot_spacing: int = 1  # plot arrows only every n-th direction

    # Note: color is also used for the color of the quiver
    color: tuple or None or str = None
    marker: str or None or str = ""

    plotspec: dict or None = None

    def __post_init__(self):
        """Executed after init"""
        if self.color is None:
            import wavedave.settings as Settings

            self.color = Settings.COLOR_MAIN

        assert len(self.x) == len(self.y), "x and y must have the same length"
        assert isinstance(self.x[0], datetime), "x must be a list of datetime objects"
        assert isinstance(self.y[0], (int, float)), "y must be a list of numbers"
        assert isinstance(self.label, str), "label must be a string"
        assert isinstance(self.unit, str), "unit must be a string"
        assert isinstance(self.statistics_type, StatisticsType), "statistics_type must be a StatisticsType"
        assert isinstance(self.dir_plot_spacing, int), "dir_plot_spacing must be an integer"
        assert isinstance(self.color, (tuple, str)), "color must be a tuple or a string"
        assert isinstance(self.marker, (str, type(None))), "marker must be a string or None"
        assert isinstance(self.plotspec, (dict, type(None))), "plotspec must be a dictionary or None"


    @property
    def label_full_context(self):
        """Returns the label with the datasource description if available."""
        r = self.label
        if self.datasource_description:
            r += f" - {self.datasource_description}"
        return r

    def scale(self, factor):
        """Applies a scale to the y-values of the source.
        !!! Do not forget to manaully adjust unit, statistics_type or label !!!"""
        self.y = [y * factor for y in self.y]

    def fade_line_color(self, factor: float):
        """Applies a fade to the line color of the source.
        0 = fully present, 1 = fully faded."""
        self.color = faded_line_color(factor, self.color)

    def render(self, ax):
        if self.plotspec is None:
            self.plotspec = dict()

        if self.marker:  # plotting markers
            self.plotspec["marker"] = self.marker
            self.plotspec["markercolor"] = self.color
            self.plotspec["linetype"] = "none"
        else:  # plotting a line
            # override / add color to linespec
            self.plotspec["color"] = self.color
            self.plotspec["linewidth"] = 1

        ax.plot(self.x, self.y, label=self.label, **self.plotspec)

        if self.direction:
            self._render_quiver(ax)

    def _render_quiver(self, ax):
        qx = []
        qy = []
        qu = []
        qv = []
        q_scale = 40

        for i in range(0, len(self.x), self.dir_plot_spacing):
            qx.append(self.x[i])
            qy.append(self.y[i])
            qu.append(-np.sin(np.radians(self.direction[i])))
            qv.append(-np.cos(np.radians(self.direction[i])))

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


@dataclass
class Graph:
    # All sources shall have the same statistics type
    source: LineSource or list[LineSource]

    title: str or None = None  # title defaults to the label of the first source

    ymin: float or None = 0.0  # by default y starts at 0, set to None to auto-scale
    ymax: float or None = None  # enforce y-lim

    limit: Limit or None = None

    def __post_init__(self):
        """Executed after init"""
        if isinstance(self.source, LineSource):
            self.source = [self.source]

        assert isinstance(self.source, (list, tuple)), "source must be a list of LineSource objects"
        assert isinstance(self.source[0], LineSource), f"source must be a list of LineSource objects, got: {type(self.source[0])}"
        assert isinstance(self.title, (str, type(None))), "title must be a string or None"
        assert isinstance(self.ymin, (float, type(None))), "ymin must be a float or None"
        assert isinstance(self.ymax, (float, type(None))), "ymax must be a float or None"
        assert isinstance(self.limit, (Limit, type(None))), f"limit must be a Limit object or None, got {type(self.limit)}"

        # check that all sources have the same statistics type
        st = self.source[0].statistics_type
        for s in self.source[1:]:
            assert (
                s.statistics_type == st
            ), f"All sources must have the same statistics type. Source 0 has statistics type: {st} and source {(self.source.index(s))} has statistics type: {s.statistics_type}."

        # check that all sources have the same unit
        unit = self.source[0].unit
        for s in self.source[1:]:
            assert (
                s.unit == unit
            ), f"All sources must have the same unit. Source 0 has unit: {unit} and source {self.source.index(s)} has unit: { s.unit }."

    def render(self, ax):
        for source in self.source:
            source.render(ax)

        title = self.title or self.source[0].label
        ax.set_title(title)

        if self.limit:
            self.limit.render(ax)

        ax.set_ylabel(self.source[0].unit)
        ax.set_ylim(bottom=self.ymin, top=self.ymax)


@dataclass
class Figure(ToPDFMixin):
    graphs: Graph or list[Graph]

    events: list[Event] or None = None
    share_x: SharedX = SharedX.NONE
    share_y: bool = False  # share y-axis limits (union)
    legend: bool = False  # adds legend to the figure
    legend_force_full_context: bool = False  # legend = label + source description
    figsize: tuple = (10, 5)

    def __post_init__(self):
        """Executed after init"""
        if isinstance(self.graphs, Graph):
            self.graphs = [self.graphs]

        if self.legend_force_full_context:
            self.legend = True

        assert isinstance(self.graphs, (list, tuple)), "graphs must be a list of Graph objects"
        assert isinstance(self.graphs[0], Graph), f"graphs must be a list of Graph objects, got: {type(self.graphs[0])}"
        assert isinstance(self.events, (list, type(None))), "events must be a list of Event objects or None"
        if self.events:
            assert isinstance(self.events[0], Event), f"events must be a list of Event objects, got: {type(self.events[0])}"
        assert isinstance(self.share_x, SharedX), "share_x must be a SharedX object"
        assert isinstance(self.share_y, bool), "share_y must be a boolean"
        assert isinstance(self.legend, bool), "legend must be a boolean"
        assert isinstance(self.legend_force_full_context, bool), "legend_force_full_context must be a boolean"
        assert isinstance(self.figsize, (tuple, list)), "figsize must be a tuple or list"


    def render(self):
        n = len(self.graphs)
        fig, axes = plt.subplots(nrows=n, ncols=1, figsize=self.figsize)

        if n == 1:
            axes = [axes]

        for graph, ax in zip(self.graphs, axes):
            graph.render(ax)

        if n > 1:
            # shared y

            if self.share_y:
                axes = sync_yscales(axes)

            # shared x

            if self.share_x == SharedX.UNION:
                # get minimum and maximum x-values for all graphs
                x_min = min([ax.get_xlim()[0] for ax in axes])
                x_max = max([ax.get_xlim()[1] for ax in axes])

                for ax in axes:
                    ax.set_xlim(x_min, x_max)

            elif self.share_x == SharedX.INTERSECTION:
                # get minimum and maximum x-values for all graphs
                x_min = max([ax.get_xlim()[0] for ax in axes])
                x_max = min([ax.get_xlim()[1] for ax in axes])

                for ax in axes:
                    ax.set_xlim(x_min, x_max)

            else:
                pass  # keep the individual x-limits

        # legend
        if self.legend:
            ax = axes[-1]
            handles, labels = ax.get_legend_handles_labels()

            # if all labels are the same, then replace then with the source label
            if len(set(labels)) == 1:
                labels = [
                    source.datasource_description for source in self.graphs[0].source
                ]

            if self.legend_force_full_context:
                labels = [source.label_full_context for source in self.graphs[0].source]

            ax.legend(
                handles,
                labels,
                loc="upper left",
                bbox_to_anchor=(0, -0.2),
                frameon=False,
            )

        # add events
        if self.events:
            for event in self.events:
                for ax in axes:
                    event.render(ax, text=ax == axes[0])

        # default style
        fig = apply_default_style(fig, axes)
        fig.tight_layout()

        return fig

    def generate_pdf(self, report: WaveDavePDF):
        fig = self.render()

        # save to svg and add to report
        filename = report.temp_folder / "figure.svg"
        fig.savefig(str(filename))
        report.set_x(report.l_margin)
        report.image(filename, w=report.epw)


if __name__ == "__main__":
    times = [
        datetime(2024, 3, 10, 0, 0, 0),
        datetime(2024, 3, 10, 5, 0, 0),
        datetime(2024, 3, 10, 10, 0, 0),
    ]

    line1 = LineSource(label="Forecast", x=times, y=[1, 4, 2])

    line2 = LineSource(label="Forecast", x=times, y=[1, 3, 2], color="r")

    events = [
        Event(description="Breakfast", when=times[0]),
        Event(description="Lunch", when=times[1]),
        Event(description="Dinner", when=times[2]),
    ]

    limit_Hs = Limit("Max for personel transfer", 1.5)

    import wavedave.settings as Settings
    Settings.DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    graph = Graph(title="Wave height", source=[line1, line2])

    graph2 = Graph(title="Wave height", source=line1, limit=limit_Hs)

    figure = Figure(
        graphs=[graph, graph2],
        events=events,
        share_x=SharedX.UNION,
        share_y=True,
        legend=True,
        figsize=(10, 5),
    )

    figure.render()
    plt.show()
