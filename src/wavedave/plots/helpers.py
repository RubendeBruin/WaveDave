import numpy as np
import matplotlib.dates as mdates

import wavedave.settings as Settings


def sync_yscales(axes):
    """Synchronizes the y-axis of a list of axes"""

    # get the limits
    limits = [ax.get_ylim() for ax in axes]
    # get the min and max
    min_ = min([l[0] for l in limits])
    max_ = max([l[1] for l in limits])
    # set the limits
    for ax in axes:
        ax.set_ylim(min_, max_)

    return axes


def apply_default_style(fig, axes):
    if not isinstance(axes, (tuple, list, np.ndarray)):
        axes = [axes]

    DATE_FORMATTER = mdates.DateFormatter(Settings.DATE_FORMAT)

    # set font
    for ax in axes:
        for item in (
            [ax.title, ax.xaxis.label, ax.yaxis.label]
            + ax.get_xticklabels()
            + ax.get_yticklabels()
        ):
            item.set_fontsize(10)
            item.set_fontname("Arial")

        # if x-axis is a date axis, set the date format
        if ax.xaxis.get_major_locator().__class__ == "mdates":
            ax.xaxis.set_major_formatter(DATE_FORMATTER)

    for ax in axes:
        # dashed grid
        ax.grid(linestyle="--", linewidth=0.5)

    return fig


def faded_line_color(factor: float, color=(40 / 255, 40 / 255, 92 / 255)):
    """Return default color faded with factor. 0 = fully present, 1 = fully faded"""

    deltas = [1 - c for c in color]

    return [a + b * factor for a, b in zip(color, deltas)]
