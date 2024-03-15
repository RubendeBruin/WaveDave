from datetime import datetime, timedelta
from pathlib import Path

from wavedave import LineSource
from wavedave.helpers import MostLikelyMatch
import wavedave.settings as settings


class IntegratedForecast:
    def __init__(
        self, filename: str or Path, dateformat="%d-%b-%Y %H:%M", local_timezone=None
    ):
        """Reads the integrated forecast from a .csv file

        filename:
        dateformat: data-format used in the file
        local_timezone: offset to apply on the time-stamps to get to local timezone. If None, the default timezone is used

        """
        filename = Path(filename)
        assert filename.exists(), f"File {filename} does not exist"
        info = []
        data = []

        self.local_timezone = local_timezone
        if self.local_timezone is None:
            self.local_timezone = settings.LOCAL_TIMEZONE

        # load the file
        with open(filename, "r") as f:
            reading_info = True

            # read file line by line
            line = "dummy"
            while line:
                line = f.readline()

                if line == "\n":
                    header = f.readline()
                    units = f.readline()
                    reading_info = False
                    continue

                if reading_info:
                    info.append(line)
                    continue

                data.append(line)

        if reading_info:
            raise ValueError(
                "No data found in file, expecting an empty line between first part and data-part of the file"
            )

        column_names = [x.strip() for x in header.split(",")]
        column_units = [x.strip() for x in units.split(",")]

        names = [f"{a} [{b}]" for a, b in zip(column_names, column_units)]

        self.source = Path(filename).stem

        # make result dict

        self.data = dict()
        for n in names[1:]:
            self.data[n] = []

        self.time = []

        for line in data:
            if line:
                values = line.split(",")

                # first entry is a date
                # convert the string into a datetime object

                try:
                    stamp = datetime.strptime(values[0], dateformat)
                except:
                    raise ValueError(f"Could not convert '{values[0]}' to a datetime object when reading line '{line}'")
                self.time.append(stamp)
                values = [float(x) for x in values[1:]]

                for name, value in zip(names[1:], values):
                    self.data[name].append(value)

        self.columns = [*self.data.keys()]

    def print(self):
        print("Columns in the integrated forecast:")
        print("\n".join(self.columns))

    def _chk_column(self, column):
        if column not in self.columns:
            columns = "\n".join(self.columns)

            suggestion = MostLikelyMatch(column, self.columns)
            if suggestion:
                suggestion = f"\n\nDid you mean '{suggestion}'?"
            else:
                suggestion = ""

            raise ValueError(
                f"Column {column} not found in the integrated forecast, we have \n {columns}{suggestion}"
            )

    def give_source(self, col: str, dir: str or None = None):
        """
        label: label to use
        y_column: the column to be used as y
        dir_column: the column to be used as direction
        """

        self._chk_column(col)

        if dir:
            self._chk_column(dir)
            dir = self.data[dir]

        times = [t - timedelta(hours=self.local_timezone) for t in self.time]

        # unit is the part of the column name in brackets
        unit = col.split("[")[-1][:-1]
        label = col.split("[")[0]

        return LineSource(
            x=times,
            y=self.data[col],
            label=label,
            unit=unit,
            dir=dir,
            datasource_description=self.source,
        )


if __name__ == "__main__":
    f = IntegratedForecast(
        r"A:\Waves\packages\WaveDave\examples\datafiles\marine_forecast_report_48127014-240311-110049_20240311.csv"
    )

    import matplotlib.pyplot as plt

    plotspec = dict()
    plotspec["marker"] = "o"
    plotspec["color"] = "red"
    plotspec["linestyle"] = "none"
    plotspec["markersize"] = 3
    plotspec["markerfacecolor"] = "red"
    plotspec["markeredgecolor"] = "black"

    plt.plot(f.time, f.data[f.columns[0]], **plotspec)
    plt.show()
