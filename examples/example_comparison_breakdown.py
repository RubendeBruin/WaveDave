from pathlib import Path

from matplotlib import pyplot as plt

from wavedave import Spectra
from wavedave.plots.helpers import faded_line_color, apply_default_style, sync_yscales

dir = Path(__file__).parent

filename = dir / 'datafiles' / 'infoplaza.csv'

latest_forecast = Spectra.from_octopus(filename)

# === Add forecasts, plot the latest one on top ===

# fake previous forecast
previous_forcecast = Spectra.from_octopus(filename)
previous_forcecast.report_timezone_UTC_plus = 12

# the first call sets up the figure and the axes
# these are returned

# plot-args can be used to set the line-style. These are passed
# directly to the plot function.

fig, axes = previous_forcecast.plot_spectrum_bands(figsize = (8,10),
                                                   split_periods=[3,5,10],
                                                   plot_args = {'color':faded_line_color(0.8)})

# for all the subsequent calls, supply the
# axes obtained from the first call to add the data to the
# already existing plots

previous_forcecast.report_timezone_UTC_plus = 6
previous_forcecast.plot_spectrum_bands(split_periods=[3,5,10],
                                       axes=axes,
                                       plot_args = {'color':faded_line_color(0.5)})

# latest forecast
latest_forecast.plot_spectrum_bands(split_periods=[3,5,10],
                                    axes = axes,
                                    plot_args = {'color':faded_line_color(0)})

# ==== Add wave-rider ===

# fake some waverider data
previous_forcecast.report_timezone_UTC_plus = 3
previous_forcecast.plot_spectrum_bands(split_periods=[3,5,10],
                                       axes=axes,
                                       plot_args = {'marker':'.',
                                                    'color':(224/255, 188/255, 7/255),
                                                    'linestyle':'none'})


# makeup
sync_yscales(axes)
apply_default_style(fig, axes)

fig.tight_layout()

plt.show()



