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