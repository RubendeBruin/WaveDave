from pathlib import Path

from numpy import trapz

import wavedave
from wavedave.plots.wavespectrum import plot_wavespectrum
from wavedave.to_smooth.bins import bin_drawing_coordinates, bin_m0
from wavedave.to_smooth.convert import to_WaveSpectrum
from wavedave.to_smooth.smooth_old import to_continuous_1d

dir = Path(__file__).parent

filename = dir / 'datafiles' / 'wavespectra_octopusfile.oct'
print(filename)

assert filename.exists()

from wavespectra import read_octopus
data = read_octopus(filename)

freq = data.freq.data
dir = data.dir.data
values = data.spec.efth

assert data.site.size == 1

# get single site
site0 = data.isel(site=0)

# loop over the time
spectra = []
for i_time in range(len(site0.time)):
    site_ti = site0.isel(time=i_time)

    # make sure that the dimensions are in the right order
    DF = site_ti.transpose('dir', 'freq')

    print(i_time)
    ds = to_WaveSpectrum(freq, dir, DF.spec.efth.data)

    spectra.append(ds)

# # compare Hs
#
# hs_bins = data.spec.hs()
# hs_smooth = [ds.hs for ds in spectra]
#
# import matplotlib.pyplot as plt
# plt.plot(hs_bins, label = 'bins')
# plt.plot(hs_smooth, label = 'smooth')
# plt.legend()
#
# compare Tp
#
# tp_bins = data.spec.tz()
# tp_smooth = [ds.m1 for ds in spectra]
#
# import matplotlib.pyplot as plt
# plt.plot(tp_bins, label = 'bins')
# plt.plot(tp_smooth, label = 'smooth')
# plt.legend()
# plt.show()

#
# ds = to_DirectionalSpectrum(freq, dir, DF.spec.efth.data)
# plot_wavespectrum(ds)
#
#
#
#
# values = DF.spec.efth.data
#
# assert values.shape == (len(data.dir), len(data.freq))
#
# import matplotlib.pyplot as plt
#
# i_time = 0
# i_interesting = (27,25,24,19,15,11,4,3)
#
# for i_dir in i_interesting:
#     plt.figure()
#     plt.title(i_dir)
#     freq = DF.spec.freq
#     values = DF.spec.efth.data
#
#     values = values[i_dir, :]
#
#
#     x,y = bin_drawing_coordinates(freq, values)
#     m0_bins = bin_m0(freq, values)
#
#     plt.plot(freq, values, 'r*', label = 'original data')
#     plt.plot(x, y, 'k-', linewidth=1, label = f'original m0 = {m0_bins:.2}')
#
#     x, y = to_continuous_1d(freq, values)
#     m0_smooth = trapz(y, x)
#
#
#     plt.plot(x, y, 'b.-', label = f'smooth m0 = {m0_smooth:.2}')
#
#     plt.legend()
#
#
#
#
# plt.show()
#
#
#
#
# # from waveresponse import DirectionalSpectrum
# #
# # ds = DirectionalSpectrum(freq =freq, dirs=dir, vals = values[0,:,:])
#
#
# print('DONE!')