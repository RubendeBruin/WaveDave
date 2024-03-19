import numpy as np
import matplotlib.pyplot as plt
from wavedave import RAO
def test_interpolate_RAO_phase():
    rao = RAO.test_rao()

    rao.plot1d(direction=0)

    from waveresponse._core import _sort

    rao._dirs, rao._vals = _sort(rao._dirs, rao._vals)

    new_frequencies = np.linspace(1 / 200, 1, 100)
    rao = rao.reshape(
        freq=new_frequencies,
        freq_hz=True,
        dirs=rao.dirs(),
        degrees=True,
        complex_convert="polar",
    )

    # save
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        rao.save(tmpdirname + "/rao.pkl")

        rao2 = RAO.load(tmpdirname + "/rao.pkl")
        print(rao2.description)
        print(rao2.mode)
        print(rao2.response_unit)

    rao.plot1d(direction=0)
    # rao2.plot1d(direction=0)
    plt.show()
