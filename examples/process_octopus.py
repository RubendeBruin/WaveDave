from pathlib import Path

from matplotlib import pyplot as plt

from wavedave import *

folder = Path(__file__).parent / 'datafiles'

forecast = Spectra.from_octopus(folder / 'infoplaza.csv')




plt.plot(forecast.time, forecast.Tp, label = "Forecast")
plt.show()
#
#
# directory = Path(r"A:\Waves\example data\obscape\spec2D")
# buoy = Spectra.from_obscape(directory)
#
# plt.plot(buoy.time, buoy.Hs, label="Buoy")
# plt.show()



