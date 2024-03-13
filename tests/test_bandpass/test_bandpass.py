from math import sqrt

from matplotlib import pyplot as plt
from numpy.testing import assert_allclose

from wavedave.plots.wavespectrum import plot_wavespectrum


def test_bandpass(jonswap_hs35_tp10_from_45):
    bp_0 = jonswap_hs35_tp10_from_45.bandpassed(freq_min = 1/8)
    bp_1 = jonswap_hs35_tp10_from_45.bandpassed(1/12, 1/8)
    bp_2 = jonswap_hs35_tp10_from_45.bandpassed(freq_max = 1/12)
    #
    # plot_wavespectrum(bp_0)
    # plot_wavespectrum(bp_1)
    # plot_wavespectrum(bp_2)
    # plt.show()

    # check the Hs

    assert bp_0.hs < jonswap_hs35_tp10_from_45.hs
    assert bp_1.hs < jonswap_hs35_tp10_from_45.hs
    assert bp_2.hs < jonswap_hs35_tp10_from_45.hs

    # assert that the direction is the same for all
    assert_allclose(bp_0.dirp(), bp_1.dirp(), rtol = 0.1)
    assert_allclose(bp_0.dirp(), bp_2.dirp(), rtol = 0.1)


    hs_total = sqrt(bp_0.hs**2 + bp_1.hs**2 + bp_2.hs**2)

    assert_allclose(hs_total, 3.5, rtol = 0.004)

