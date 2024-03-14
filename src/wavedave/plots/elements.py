from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import matplotlib.pyplot as plt

from wavedave.plots.helpers import sync_yscales


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


# Event is a vertical line in the graph
@dataclass
class Event:
    description: str
    when: datetime


# Limit is a constant horizontal line in the graph
@dataclass
class Limit:
    description: str
    value: float


@dataclass
class LineSource:
    label: str

    x: list[datetime]
    y: list[float]

    unit: str = ""

    y_scale: float = 1.0

    statistics_type: StatisticsType = StatisticsType.NONE

    dir: list[float] or None = None

    dir_spacing: int = 1

    # Note: color is also used for the color of the quiver
    color: tuple or None or str = "k"
    marker: str or None or str = ""

    plotspec: dict or None = None


@dataclass
class Graph:
    # All sources shall have the same statistics type
    source: LineSource or list[LineSource]

    title: str or None = None  # title defaults to the label of the first source

    ymin: float or None = 0.0  # by default y starts at 0
    ymax: float or None = None  # enforce y-lim

    limit: Limit or None = None

    def render(self, ax):
        for source in self.source:
            source.render(ax)

        title = self.title or self.source[0].label
        ax.set_title(title)

        if self.

@dataclass
class Figure:
    graphs: list[Graph]

    events: list[Event] or None = None
    share_x: SharedX = SharedX.NONE
    share_y: bool = False  # share y-axis limits (union)
    legend: bool = False  # adds legend to the figure
    figsize: tuple = (10, 5)

    def render(self):
        n = len(self.graphs)
        fig, axes = plt.subplots(nrows=n, ncols=1, figsize=self.figsize)
        for graph, axes in zip(self.graphs, axes):
            graph.render(axes)

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
            axes[-1].legend(
                loc="upper left", bbox_to_anchor=(0, 0), frameon=False
            )

        # add events
        if self.events:
            for event in self.events:
                x = event.when
                for ax in axes:
                    ax.axvline(x=event.when, color="k", linestyle="--")

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

        return fig


@dataclass
class Page:
    figure: Figure

    heading: str = ""
    text_above: str = ""
    text_below: str = ""
    text_left: float = 17


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

    page = Page(
        figure=figure,
        heading="Report",
        text_above="Some text above",
        text_below="Some text below",
    )
