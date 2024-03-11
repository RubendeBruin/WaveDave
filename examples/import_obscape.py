import datetime
from pathlib import Path

from matplotlib import pyplot as plt

from wavedave.readers.obscape import read_obscape, get_obs_files,read_obscape_file

dir = Path(__file__).parent

filename = dir / 'datafiles' / '20240214_000000_wavebuoy_xxx_spec2D.csv'

data = read_obscape_file(str(filename))

directory = Path(r"A:\Waves\example data\obscape\spec2D")

start_date = datetime.datetime(2024, 2, 14)
end_date = datetime.datetime(2024, 2, 25)
files = get_obs_files(directory, start_date=start_date, end_date=end_date)

waves = read_obscape(directory, start_date, end_date)
print(waves)

site0 = waves.isel(site=0)

# Contour plot of spectral development
if (True):
    # squash to 1d spectra
    oned = site0.spec.oned()

    # select the data

    values = oned.transpose('freq','time')

    # plot the data
    plt.figure()

    period = 1/oned.freq  # note, freq is in Hz

    plt.contourf(oned.time,period,  values, cmap='Blues')
    plt.xlabel('Time')
    plt.ylabel('Period [s]')

plt.show()