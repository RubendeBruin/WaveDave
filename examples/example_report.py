from datetime import datetime
from pathlib import Path

from wavedave import Event
from wavedave import Spectra, IntegratedForecast
from wavedave.reports.metocean import MetoceanSource, MetoceanReport

dir = Path(__file__).parent

filename = dir / 'datafiles' / 'infoplaza.csv'
if_filename = dir / 'datafiles' / 'marine_forecast_report_48127014-240311-110049_20240311.csv'


forecast1 = Spectra.from_octopus(filename)
forecast2 = Spectra.from_octopus(filename)
forecast3 = Spectra.from_octopus(filename)

forecast2.report_timezone_UTC_plus = 6
forecast3.report_timezone_UTC_plus = 12

# events
breakfast = Event(description="Breakfast",
                  when = datetime(2024,3,6,0,12,0))
lunch = Event(description="Lunch",
              when = datetime(2024,3,7,0,0,0))
dinner = Event(description="Dinner",
               when = datetime(2024,3,9,0,5,45))

bedtime = Event(description="Bedtime",
               when = datetime(2024,3,10,11,0,0))

# load waverider files

buoy = Spectra.from_octopus(filename)
buoy.report_timezone_UTC_plus = 3

# make a report

forecast = MetoceanSource(description="Forecast",
                        data=[forecast1, forecast2, forecast3],  # most recent forecast on the left!
                        is_buoy=False)

buoy = MetoceanSource(description="Buoy",
                        data=[buoy],
                        is_buoy=True)

integrated_forecast = IntegratedForecast(if_filename)


report = MetoceanReport()

report.header_text = "WaveDave4"

report.add_source(forecast)
report.add_source(buoy)

report.events = [breakfast, lunch, dinner, bedtime]

# --- integrated forecast

report.integrated_forecast = integrated_forecast  # add the integrated forecast (plotted if added)
report.integrated_plots.append("Significant wave height [m]") # single value interpreted as a time series
report.integrated_plots.append("Wave peak period [s]")
report.integrated_plots.append(["10m wind speed [m/s]",
                                "Wind direction [deg]"])  # two values interpreted as value , direction
report.integrated_plots.append("Temperature [deg C]")

# --- breakdown settings

report.breakdown = True

report.breakdown_split_periods_s = [2,5]
report.breakdown_y_synced = False

report.breakdown_text_offset = 17
report.breakdown_text_above = "<br><br>Some text above the breakdown figure<p>Project = Voor de leuk"
report.breakdown_text_below = 'Generated using WaveDave for <b>HEBO</b>'

# --- energy settings

report.energy = True
report.energy_source_i = 0    # the forecast was added as first source, so 0

report.energy_text_offset = 17
report.energy_text_above = "<br><br>Some text above the energy figure<p>Project = Voor de leuk"
report.energy_text_below = 'Generated using WaveDave for <b>HEBO</b>'
report.energy_n_cols = 2
report.energy_figsize = (10, 12)




pdf = report.generate_report()

pdf.open()
