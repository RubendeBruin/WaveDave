from pathlib import Path

from matplotlib import pyplot as plt

from wavespectra import read_octopus

dir = Path(__file__).parent

filename = dir / 'datafiles' / 'infoplaza.csv'

assert filename.exists()

data = read_octopus(filename)
site0 = data.isel(site=0)

print(data)


# Contour plot of spectral development
if (False):
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

# split in period bands and plot one-by-one

splits_s = [5, 8, 12]

# add zero and inf
splits = [None] + [1/s for s in splits_s] + [None]

for start, stop in zip(splits[:-1], splits[1:]):

    band = site0.spec.split(fmin = stop, fmax = start, rechunk=False)
    plt.plot(band.time, band.spec.hs(), label = f'{start} - {stop}')

plt.legend()
plt.show()


