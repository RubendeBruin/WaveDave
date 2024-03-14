from datetime import datetime
from pathlib import Path


class IntegratedForecast:

    def __init__(self, filename: str or Path, dateformat='%d-%b-%Y %H:%M'):
        filename = Path(filename)
        assert filename.exists(), f"File {filename} does not exist"\

        info = []
        data = []



        # load the file
        with open(filename, 'r') as f:
            reading_info = True

            # read file line by line
            line = 'dummy'
            while line:
                line = f.readline()

                if line == '\n':
                    header = f.readline()
                    units = f.readline()
                    reading_info = False
                    continue

                if reading_info:
                    info.append(line)
                    continue

                data.append(line)

        if reading_info:
            print("No data found in file, expecting an empty line between first part and data-part of the file")
            return

        column_names = [x.strip() for x in header.split(',')]
        column_units = [x.strip() for x in units.split(',')]

        names = [f"{a} [{b}]" for a, b in zip(column_names, column_units)]

        # make result dict

        self.data = dict()
        for n in names[1:]:
            self.data[n] = []

        self.time = []

        for line in data:

            if line:
                values = line.split(',')

                # first entry is a date
                # convert the string into a datetime object

                stamp = datetime.strptime(values[0], dateformat)
                self.time.append(stamp)
                values = [float(x) for x in values[1:]]

                for name, value in zip(names[1:], values):
                    self.data[name].append(value)

        self.columns = [*self.data.keys()]








if __name__ == '__main__':
    f = IntegratedForecast(r'A:\Waves\packages\WaveDave\examples\datafiles\marine_forecast_report_48127014-240311-110049_20240311.csv')

    import matplotlib.pyplot as plt


    plotspec = dict()
    plotspec['marker'] = 'o'
    plotspec['color'] = 'red'
    plotspec['linestyle'] = 'none'
    plotspec['markersize'] = 3
    plotspec['markerfacecolor'] = 'red'
    plotspec['markeredgecolor'] = 'black'

    plt.plot(f.time, f.data[f.columns[0]], **plotspec)
    plt.show()

