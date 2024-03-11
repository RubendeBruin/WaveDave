from datetime import datetime
from pathlib import Path

from wavedave.to_smooth.convert import to_WaveSpectrum


class Spectra:
    """Holds a series of 'DirectionalSpectrum' objects"""

    def __init__(self, wavespectra=None):

        self.spectra = []
        self.time = []

        # Define the data
        if wavespectra is not None:
            self._create_from_wavespectra(wavespectra)

## Properties

    @property
    def Hs(self):
        return [ds.hs for ds in self.spectra]

## Creation methods

    def _create_from_wavespectra(self, wavespectra):
        # Create the data

        in_dirs = wavespectra.dir.values
        in_freq = wavespectra.freq.values

        # strip site (if any)
        if 'site' in wavespectra.dims:
            wavespectra = wavespectra.isel(site=0)

        # loop over time
        self.spectra = []
        for i_time in range(len(wavespectra.time)):
            site_ti = wavespectra.isel(time=i_time)

            # make sure that the dimensions are in the right order
            DF = site_ti.transpose('dir', 'freq')

            # get the data
            values = DF.spec.efth.data

            # create the spectrum
            ds = to_WaveSpectrum(in_freq, in_dirs, values)

            # add to the list
            self.spectra.append(ds)

        self.time = wavespectra.time.data

    @staticmethod
    def from_octopus(filename : Path or str):
        """Reads an octopus file and returns a Spectra object"""

        filename = Path(filename)
        assert filename.is_file(), f"File {filename} does not exist"
        assert filename.exists(), f"File {filename} does not exist"

        from wavespectra import read_octopus
        data = read_octopus(str(filename))
        return Spectra(wavespectra=data)

    @staticmethod
    def from_obscape(directory : Path or str,
                     start_date : datetime or None = None,
                     end_date : datetime or None = None):
        """Reads an obscape directory and returns a Spectra object"""

        directory = Path(directory)
        assert directory.is_dir(), f"Directory {directory} does not exist"

        from wavespectra import read_obscape
        data = read_obscape(directory,
                            start_date = start_date,
                            end_date = end_date)
        return Spectra(wavespectra=data)