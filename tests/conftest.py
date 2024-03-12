from pathlib import Path

import pytest
from wavedave import Spectra

DATADIR = Path(__file__).parent / 'test_files'

@pytest.fixture
def octopus_file():
    return DATADIR / 'octopusfile.oct'

@pytest.fixture
def waves():
    waves = Spectra.from_octopus(DATADIR / 'octopus.csv')
    return waves

@pytest.fixture
def octopus_waves():
    waves = Spectra.from_octopus(DATADIR / 'octopusfile.oct')
    return waves

@pytest.fixture
def jonswap_hs35_tp10_from_45():
    import numpy as np
    import waveresponse as wr

    freq = np.arange(0.01, 1, 0.01)
    dirs = np.linspace(0.0, 360.0, endpoint=False)
    hs = 3.5
    tp = 10.0
    dirp = 45.0

    _, spectrum1d = wr.JONSWAP(freq, freq_hz=True)(hs, tp)
    spread_fun = wr.CosineFullSpreading(s=2, degrees=True)

    wave = wr.WaveSpectrum.from_spectrum1d(
        freq,
        dirs,
        spectrum1d,
        spread_fun,
        dirp,
        freq_hz=True,
        degrees=True,
        clockwise=True,
        waves_coming_from=True,
    )

    return wave