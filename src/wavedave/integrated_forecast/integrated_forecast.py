from datetime import datetime, timedelta
from pathlib import Path

from wavedave import LineSource
from wavedave.helpers import MostLikelyMatch
import wavedave.settings as settings


class IntegratedForecast:
    def __init__(
        self, filename: str or Path, dateformat="%d-%b-%Y %H:%M", forecast_in_utc_plus=0
    ):
        """Reads the integrated forecast from a .csv file

        filename:
        dateformat: data-format used in the file
        forecast_in_utc_plus [0]: offset to apply on the time-stamps to get to UTC. If the forecast is supplied in UTC+7 then use 7.

        """
        filename = Path(filename)
        assert filename.exists(), f"File {filename} does not exist"
        info = []
        data = []

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

        # apply timezone offset if any to convert to UTC
        if forecast_in_utc_plus:
            for i in range(len(self.time)):
                self.time[i] = self.time[i] - timedelta(hours=forecast_in_utc_plus)

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


        # unit is the part of the column name in brackets
        unit = col.split("[")[-1][:-1]
        label = col.split("[")[0]

        return LineSource(
            x=self.time.copy(),
            y=self.data[col],
            label=label,
            unit=unit,
            direction=dir,
            datasource_description=self.source,
        )


if __name__ == "__main__":

    dir = Path(__file__).parent.parent.parent.parent

    f = IntegratedForecast(
        dir / "examples" / "datafiles" / "marine_forecast_report_20240311.csv"
    )

    import matplotlib.pyplot as plt

    plotspec = dict()
    plotspec["marker"] = "o"  # ('.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
    plotspec["linestyle"] = "none"
    plotspec["markersize"] = 5
    plotspec["markerfacecolor"] = "pink"
    plotspec["markeredgecolor"] = "purple"

    fig, axes = plt.subplots(1, 1, figsize=(10, 5))
    plt.plot(f.time, f.data[f.columns[0]], **plotspec)

    from wavedave.plots.helpers import apply_default_style
    apply_default_style(fig, axes)

    plt.show()
