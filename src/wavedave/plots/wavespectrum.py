import numpy as np
import matplotlib.pyplot as plt


from waveresponse import DirectionalSpectrum


def _plot_polar(ds: DirectionalSpectrum, ax, do_periods, cmap, max_period, levels):
    freq, dirs, vals = ds.grid(freq_hz=True, degrees=True)

    if do_periods:
        y_value = 1 / freq  # seconds
    else:
        y_value = freq

    # close the spectrum by repeating the first direction at the end
    dirs = np.append(dirs, dirs[0] + 360)

    # Convert angles from degrees to radians and adjust so that 0 is at the top
    angles = np.radians(dirs)

    #
    # # add the vals as well
    vals = np.hstack((vals, vals[:, 0:1]))

    # Create a meshgrid for period and angles
    r, theta = np.meshgrid(y_value, angles)

    # Create a polar plot
    fig = None
    if ax is None:
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, polar=True)

    if do_periods:
        if max_period is not None:
            ax.set_ylim(0, max_period)

    # Plot data
    if levels is None:
        levels = np.linspace(0, np.nanmax(vals), 20)

    ax.contourf(theta, r, vals.transpose(), cmap=cmap, levels=levels)

    return fig, ax


def plot_wavespectrum(
    ds: DirectionalSpectrum,
    cmap="RdPu",
    above_title="",
    do_periods=True,
    max_period=15,
    ax=None,
    levels=None,
):

    fig, ax = _plot_polar(ds, ax, do_periods, cmap, max_period, levels)

    ax.set_theta_zero_location("N")  # Set 0 degrees to the top
    ax.set_theta_direction(-1)  # Set angle direction to clockwise

    ax.set_title(
        f"{above_title}Hs = {ds.hs:.2f}m "
        f"Tp = {ds.tp:.1f}s"
        f" From = {ds.dirm(degrees=True):.0f}deg"
    )

    # radial labels
    if do_periods:
        r_text = "Period [s]"
    else:
        r_text = "Frequency [Hz]"

    ax.set_rlabel_position(60)
    label_position = ax.get_rlabel_position()
    ax.text(
        np.radians(label_position - 10),
        1.05 * ax.get_rmax(),
        r_text,
        ha="left",
        va="center",
        fontsize=10,
        font="Arial",
    )

    return fig, ax
