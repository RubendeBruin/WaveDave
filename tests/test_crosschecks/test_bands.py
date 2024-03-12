from numpy.testing import assert_allclose

from wavespectra import read_octopus
def test_bands(octopus_file, octopus_waves):

    bands = octopus_waves.Hs_bands(split_periods=[3,7])

    ws = read_octopus(octopus_file)

    site0 = ws.isel(site=0)
    # split in period bands and plot one-by-one

    splits_s = [3,7]

    # add zero and inf
    splits = [None] + [1 / s for s in splits_s] + [None]

    expected = []

    for start, stop in zip(splits[:-1], splits[1:]):
        band = site0.spec.split(fmin=stop, fmax=start, rechunk=False)
        expected.append(band.spec.hs().values)

    for i, band in enumerate(bands):
        assert_allclose(band, expected[i], atol=0.1, rtol=0.1)  # 2x 10% tolerance

    # import matplotlib.pyplot as plt
    # for i, band in enumerate(bands):
    #    plt.plot(band)
    #    plt.plot(expected[i])
    #
    # plt.show()








