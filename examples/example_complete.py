from datetime import datetime
from pathlib import Path

from wavedave import *


dir = Path(__file__).parent
filename = dir / 'datafiles' / 'marine_forecast_report_20240311.csv'
filename2 = dir / 'datafiles' / 'marine_forecast_report_20240310.csv'

spec_filename = dir / 'datafiles' / 'infoplaza.csv'


spectral_forecast = Spectra.from_octopus(spec_filename)


# Read the forecast

integrated_forecast = IntegratedForecast(filename)

# print the available columns
integrated_forecast.print()

# get the sources that we want,
# use the column names from the printout
max_waveheight = integrated_forecast.give_source("Maximum wave height [m]")
sig_waveheight = integrated_forecast.give_source("Significant wave height [m]")
sig_waveheight.color = "red"

temperature = integrated_forecast.give_source("Temperature [deg C]")

# example with direction
wind10 = integrated_forecast.give_source("10m wind speed [m/s]", "Wind direction [deg]")
wind10.dir_plot_spacing = 5

# example of scaling
wind_at_top = integrated_forecast.give_source("10m wind speed [m/s]", "Wind direction [deg]")
wind_at_top.label = "Wind at top of crane"
wind_at_top.dir_plot_spacing = 5
wind_at_top.scale(1.5)

# older forecast with a different time-format
yesterdays_forecast = IntegratedForecast(filename2, dateformat="%m/%d/%Y %H:%M")
yesterdays_max_waveheight = yesterdays_forecast.give_source("Maximum wave height [m]")
yesterdays_max_waveheight.fade_line_color(0.5)

yesterdays_wind = yesterdays_forecast.give_source("10m wind speed [m/s]", "Wind direction [deg]")
yesterdays_wind.fade_line_color(0.5)

# Make a figure using elements

# Figure with a single plot
waveheights = Graph(source = [max_waveheight, sig_waveheight], title="Wave heights")
fig1 = Figure(graphs = waveheights,
             legend=True,)


# Figure with multiple plots
temp = Graph(source = temperature)
wind = Graph(source = wind10)
wind_at_top = Graph(source = wind_at_top)

fig2 = Figure([temp, wind, wind_at_top],
             figsize = (5,6))

# Figure with multiple plots and shared x-axis
# Note that legends are only added to the lowest plot.

waveheight_comparison = Graph(source = [max_waveheight, yesterdays_max_waveheight])
wind_comparison = Graph(source = [wind10, yesterdays_wind])

fig3 = Figure([waveheight_comparison, wind_comparison],
             share_x = SharedX.UNION,
             legend = True,
             figsize = (10,6))


# Spectra can also be used as a source
Hs_spectral = spectral_forecast.give_Hs_LineSource()
Hs_comparison = Graph(source = [sig_waveheight, Hs_spectral])

fig4 = Figure(Hs_comparison,
              legend_force_full_context=True)  # this automatically sets legend to True as well

# X-axis alignment
Hs_spectral_graph = Graph(source = Hs_spectral, title = "Spectral wave height [m]")
Hs_integrated_graph = Graph(source = sig_waveheight, title = "Integrated wave height [m]")

fig5 = Figure([Hs_spectral_graph, Hs_integrated_graph], share_y = True)

fig6 = Figure([Hs_spectral_graph, Hs_integrated_graph],share_x=SharedX.UNION)

# ==== Limits and Events =====

# events
breakfast = Event(description="Breakfast",
                  when = datetime(2024,3,13,0,12,0))
lunch = Event(description="Lunch",
              when = datetime(2024,3,14,0,0,0))
dinner = Event(description="Dinner",
               when = datetime(2024,3,15,0,5,45))

bedtime = Event(description="Bedtime",
               when = datetime(2024,3,18,11,0,0))


# limits
too_hot = Limit("Max temperature", 15)
wind = Limit("Max wind", 10)

# limits are added to Graphs
# events are added to a Figure

wind_with_limit = Graph(source = wind10, limit = wind)
temperature_with_limit = Graph(source = temperature, limit=too_hot)

fig7 = Figure([wind_with_limit, temperature_with_limit], events = [breakfast, lunch, dinner, bedtime])

# Make a pdf report

report = WaveDavePDF()

report.add_header("Just some examples of custom plots")
report.add_text("Colors default to those defined in Settings, but can be changed manually per LineSource:")
report.add(fig1)

report.add_page_break()
report.add_header("FigSize")
report.add_text("The figsize can be set per figure. Setting it too low will make the text relatively large, like so:")


report.add(fig2)

report.add_page_break()
report.add_header("Legends")
report.add_text("Legends are added only to the lowest graph of a figure. But you may add more figures to a page although you "
                "may need to tweak the figsize to make them fit. <p>Figures are created over the full widht of the page, the aspect "
                "is used to calculate the height.</p>")
report.add(fig3)
report.add(fig4)

report.add_page_break()
report.add_header("Shared x-axis and/or y-axis options")
report.add_text("Y axis shared, X axis not")
report.add(fig5)
report.add_text("X axis shared, Y axis not")
report.add(fig6)

report.add_page_break()
report.add_header("Example of using limits and events")
report.add_text("Events are added per Figure. They are identical for all graphs in the figure.<p>Limits are added to individual graphs.")

report.add(fig7)




filename = dir / "datafiles" / "infoplaza.csv"


forecast1 = Spectra.from_octopus(filename)
forecast2 = Spectra.from_octopus(filename)
forecast3 = Spectra.from_octopus(filename)

forecast2.report_timezone_UTC_plus = 6
forecast3.report_timezone_UTC_plus = 12

# events
breakfast = Event(description="Breakfast", when=datetime(2024, 3, 6, 0, 12, 0))
lunch = Event(description="Lunch", when=datetime(2024, 3, 7, 0, 0, 0))
dinner = Event(description="Dinner", when=datetime(2024, 3, 9, 0, 5, 45))

bedtime = Event(description="Bedtime", when=datetime(2024, 3, 10, 11, 0, 0))

# load waverider files

buoy = Spectra.from_octopus(filename)
buoy.report_timezone_UTC_plus = 3

# make a report

forecast = MetoceanSource(
    description="Forecast",
    data=[forecast1, forecast2, forecast3],  # most recent forecast on the left!
    is_buoy=False,
)

buoy = MetoceanSource(description="Buoy", data=[buoy], is_buoy=True)


report.header_text = "WaveDave4"

# ======= add a breakdown section =======
breakdown_section = BreakdownSection()
breakdown_section.add_source(forecast)
breakdown_section.add_source(buoy)
breakdown_section.events = [breakfast, lunch, dinner, bedtime]

report.add(breakdown_section)

# ======= add an energy section =======

energy_section = EnergySection(forecast1)
energy_section.n_cols = 2
energy_section.events = [breakfast, lunch, dinner, bedtime]
report.add(energy_section)

# ======= Some custom text, on a new page ======

report.add(PageBreakIfNeeded())

report.add(Header("This is a header"))

report.add(
    Text(
        "Some text, just because we can<p>This is HTML with limited support for tags. <b>bold</b> <i>italic</i> <u>underline</u> <br>line break",
    )
)


report.open()
