from datetime import datetime
from pathlib import Path

from matplotlib import pyplot as plt

from wavedave import Spectra
from wavedave.plots.helpers import faded_line_color, apply_default_style, sync_yscales

dir = Path(__file__).parent
filename = dir / 'datafiles' / 'infoplaza.csv'
forecast = Spectra.from_octopus(filename)

# ===

# first make a figure with the size that we like
fig, ax = plt.subplots(figsize = (10,3))
_ , ax = forecast.plot_spectrum_frequencies_over_time(cmap = 'Reds', ax = ax)

# add some lines to the plot to indicate times of interest
# times are in the local timezone and are plotted as vertical lines
# the times are in the local timezone and are represented as datetime objects

times_of_interest = []
times_of_interest.append((datetime(2024,3,6,12,0,0), "Breakfast"))
times_of_interest.append((datetime(2024,3,7,0,0,0), "Lunch"))
times_of_interest.append((datetime(2024,3,9,0,5,45),"Dinner"))

# get the spectra nearest to those times, we are NOT going to interpolate
for t, title in times_of_interest:
    # get the nearest spectra
    nearest_i = forecast.spectrum_number_nearest_to(local_time=t)
    # plot a vertical line at that time
    x = forecast.time_in_timezone[nearest_i]

    ax.axvline(x, color = 'black', linestyle = '--', linewidth = 0.8)

    y = ax.get_ylim()
    y = 0.95*y[1]

    ax.text(x, y, title, font='Arial', fontsize=10, rotation=90, ha = 'right', va = 'top')

    # and create a roseplot for this time
    rose_fig, rose_ax = forecast.plot_spectrum_2d(nearest_i, cmap = 'Oranges', title=title + '\n\n')
    apply_default_style(rose_fig, rose_ax)


# makeup
apply_default_style(fig, ax)

fig.tight_layout()

plt.show()



