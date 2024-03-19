import numpy as np
import matplotlib.pyplot as plt
from wavedave import RAO
from waveresponse import calculate_response, DirectionalSpectrum, WaveSpectrum


def test_response_calc_1d(jonswap_hs35_tp10_from_45):
    # rao = RAO.test_rao()  # get the test RAO

    print(jonswap_hs35_tp10_from_45.moment(0))
    frequency, energy = jonswap_hs35_tp10_from_45.spectrum1d(freq_hz=True)


    # reshape energy
    energy = np.array([energy]).transpose()

    """
     def __init__(
        self,
        freq,
        dirs,
        vals,
        freq_hz=False,
        degrees=False,
        clockwise=False,
        waves_coming_from=True,"""


    # values shall be provided in radians and radians/s

    wave1d = WaveSpectrum(
        freq=frequency,
        dirs=np.array([45]),
        vals=energy,
        freq_hz=True,
        degrees=True,
        clockwise=True,
        waves_coming_from=True,
    )

    print(wave1d.hs)
    print(wave1d.tp)
