def test_freq_over_time(waves):
    data = waves.freq_over_time

    assert data.shape[0] == len(waves.spectra)
    assert data.shape[1] == len(waves.freq)