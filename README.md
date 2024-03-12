# WaveDave
Practical marine waves and wave response calculations

## Introduction

WaveDave is a Python package for practical marine waves and wave response calculations.

It heavily relies on, and combines the functionality of the following packages:
- [wavespectra](https://wavespectra.readthedocs.io/en/latest/)
- [waveresponse](https://docs.4insight.io/waveresponse/python/latest/index.html)

WaveSpectra is used for importing wave-spectra from real-life sources such as forecasts, models or measurements buoys.
WaveResponse is used for plotting and combining the wave-spectra with RAOs.

This package adds:
- a comprehensable API for creating wave-spectra from external sources (completely wrapping all required wavespectra calls)
- conversion of binned wave-spectra to smooth spectra
- a Spectra object that contains a series of wave-response wave-spectra and corresponding time-stamps.

Example:

```python
from wavedave import Spectra
import matplotlib.pyplot as plt

forecast = Spectra.from_octopus('forecasefile.csv')
plt.plot(forecast.time, forecast.Hs, label = "Forecast")
```

# Conventions

times are datetime objects
frequency is in Hz
Direction is in degrees using coming-from convention



## Timezone

Internally all data is treated as UTC

When plotting or reporting, the time is shifted with the amount of hours specified in `report_timezone_UTC_plus`.





# Creation

Spectra.from_octopus
Spectra.from_obscape

# Properties

Spectra.time : time-series

.Hs : significant wave height
.Tp : peak period

.Tz

.dirs [degrees]

.freq [Hz]



Period bands

.Hs_bands(split_periods)



## Squashed properties

.dir_over_time

.freq_over_time










# Conversion from binned to smooth
WaveDave.to_smooth contains some magic to convert binned wave-spectra to smooth wave-spectra.

# Plotting

plot_spectrum: plots a topview of the 2d spectrum

plot_spectrum_bands

plot_direction_over_time

plot_spectrum_frequencies_over_time


### helpers

sync_ylimits

apply_default_style





