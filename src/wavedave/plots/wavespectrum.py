import numpy as np
import matplotlib.pyplot as plt


from waveresponse import DirectionalSpectrum


def plot_wavespectrum(ds : DirectionalSpectrum, cmap = 'RdPu'):

    freq, dirs, vals = ds.grid(freq_hz=True, degrees=True)
    periods = 1/freq     # seconds

    # close the spectrum by repeating the first direction at the end
    dirs = np.append(dirs, dirs[0]+360)


    # Convert angles from degrees to radians and adjust so that 0 is at the top
    angles = np.radians([(angle - 90) % 360 for angle in dirs])

    #
    # # add the vals as well
    vals = np.hstack((vals, vals[:,0:1]))

    # Create a meshgrid for period and angles
    r, theta = np.meshgrid(periods, angles)

    # Create a polar plot
    plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_zero_location('N')  # Set 0 degrees to the top
    ax.set_theta_direction(-1)  # Set angle direction to clockwise

    # Plot data
    contour = ax.contourf(theta, r, vals.transpose(), cmap=cmap)
