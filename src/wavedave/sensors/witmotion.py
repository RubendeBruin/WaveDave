"""The 50 euro witmotion sensor
WT9011 is a 9-axis IMU sensor that can be used to measure acceleration, angular velocity, and magnetic field.
"""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import signal

from wavedave.sensors.timeseries import TimeSeries


def read(filename, T0 = None):
    """Read the data from a witmotion sensor

    T0 is the start time of the data, if None, it is read from the data file as the chip time
    """

    data = pd.read_csv(filename, index_col=False)

    # make a new time index
    start_time = datetime.strptime(data['Time'][0], ' %H:%M:%S.%f')
    times = [(datetime.strptime(a, ' %H:%M:%S.%f')-start_time).total_seconds() for a in data['Time']]


    rx = data['Angle X(°)'].to_numpy()
    ry = data['Angle Y(°)'].to_numpy()
    rz = data['Angle Z(°)'].to_numpy()

    print(data.columns)

    ax = data['Acceleration X(g)'].to_numpy()
    ay = data['Acceleration Y(g)'].to_numpy()
    az = data['Acceleration Z(g)'].to_numpy()

    # get the date
    if T0 is None:
        date = data['Chip Time()'][0]  # something line ' 2024-3-19 16:44:16.689'
        try:
            T0 = datetime.strptime(date.split(' ')[1], '%Y-%m-%d')
            T0 += timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
        except:
            raise ValueError(f'Could not parse the date from {date}')


    # make a time series
    ts = TimeSeries(T0, times, {'rx': rx, 'ry': ry, 'rz': rz, 'ax': ax, 'ay': ay, 'az': az})

    ts.make_equidistant(interpolate=False)

    return ts

if __name__ == '__main__':
    # filename = r"A:\Waves\example data\witmotion\2024-03-19\16-33-23-240\data__1.csv"     # corrupt file
    filename = r"A:\Waves\example data\witmotion\2024-03-19\16-39-20-214\data__1.csv"
    # filename = r"A:\Waves\example data\witmotion\2024-03-19\16-44-25-984\data__1.csv"
    # filename = r"A:\Waves\example data\witmotion\2024-03-19\16-46-37-868\data__1.csv"
    # filename = r"A:\Waves\example data\witmotion\2024-03-19\16-49-27-976\data__1.csv"
    # filename = r"A:\Waves\example data\witmotion\2024-03-19\16-52-34-731\data__1.csv"
    ts= read(filename, T0 = datetime(2024,3,19,16,33,23))
    # plt.plot(times, rx, label='x')

    for i in range(len(ts.signals)):
        ts.plot(i)




    plt.show()

    # v = rx
    #
    # fig, ax = plt.subplots(2,1)
    #
    # # plt.plot(np.diff(times))
    # ax[0].plot(times, v)
    #
    # new_times = np.linspace(0, times[-1], len(times))
    #
    # ax[0].plot(new_times, v)
    #
    # # use Welch to calculate the spectral density
    # f, Pxx = signal.welch(v, fs=1/np.mean(np.diff(new_times)), nperseg=512, window='hann')
    #
    # ax[1].plot(1/f, Pxx)
    #
    # plt.show()
