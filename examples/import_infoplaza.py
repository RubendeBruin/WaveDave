from pathlib import Path

from matplotlib import pyplot as plt

from wavedave import Spectra
from wavedave.plots.helpers import faded_line_color, apply_default_style, sync_yscales

dir = Path(__file__).parent

filename = dir / 'datafiles' / 'infoplaza.csv'

latest_forecast = Spectra.from_octopus(filename)



fig, axes = latest_forecast.plot_spectrum_bands(figsize = (8,10),
                                                   split_periods=[3,5,10],
                                                   plot_args = {'color':faded_line_color(0.8)})

plt.show()



