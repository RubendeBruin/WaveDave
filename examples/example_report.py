from datetime import datetime
from pathlib import Path

from wavedave import *

dir = Path(__file__).parent

filename = dir / "datafiles" / "infoplaza.csv"


forecast1 = Spectra.from_octopus(filename)
forecast2 = Spectra.from_octopus(filename, source_in_utc_plus=6)
forecast3 = Spectra.from_octopus(filename, source_in_utc_plus=12)


# events
breakfast = Event(description="Breakfast", when=datetime(2024, 3, 6, 0, 12, 0))
lunch = Event(description="Lunch", when=datetime(2024, 3, 7, 0, 0, 0))
dinner = Event(description="Dinner", when=datetime(2024, 3, 9, 0, 5, 45))

bedtime = Event(description="Bedtime", when=datetime(2024, 3, 10, 11, 0, 0))

# load waverider files

buoy = Spectra.from_octopus(filename, source_in_utc_plus=3.5)

# make a report

forecast = MetoceanSource(
    description="Forecast",
    data=[forecast1, forecast2, forecast3],  # most recent forecast on the left!
    is_buoy=False,
)

buoy = MetoceanSource(description="Buoy", data=[buoy], is_buoy=True)


report = WaveDavePDF()

report.header_text = "WaveDave4"

# ======= add a breakdown section =======
breakdown_section = BreakdownSection()
breakdown_section.add_source(forecast)
breakdown_section.add_source(buoy)
report.events = [breakfast, lunch, dinner, bedtime]

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
