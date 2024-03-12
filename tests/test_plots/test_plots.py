import matplotlib.pyplot as plt

from wavedave.plots.helpers import sync_yscales, apply_default_style


def test_plot_spectrum_frequencies_over_time(waves):
    fig, ax = plt.subplots()
    waves.plot_spectrum_frequencies_over_time()

def test_plot_direction_over_time(waves):
    fig, ax = plt.subplots()
    waves.plot_direction_over_time(ax=ax)


def test_plot_bands(waves):
    fig, axes = waves.plot_spectrum_bands(split_periods=[3,7])
    sync_yscales(axes)
    apply_default_style(fig, axes)
    fig.tight_layout()
    plt.show()

def test_plot_spec_2d(waves):
    waves.plot_spectrum_2d()
    plt.show()