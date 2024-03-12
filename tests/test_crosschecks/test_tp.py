from numpy.testing import assert_allclose

from wavespectra import read_octopus

def test_octopus_tp(octopus_file, octopus_waves):

    data = read_octopus(octopus_file)

    expected = data.isel(site=0).spec.tp().values
    actual = octopus_waves.Tp

    assert_allclose(expected, actual, rtol=0.05)


def test_octopus_hs(octopus_file, octopus_waves):

    data = read_octopus(octopus_file)

    expected = data.isel(site=0).spec.hs().values
    actual = octopus_waves.Hs

    assert_allclose(expected, actual, rtol=0.05)
