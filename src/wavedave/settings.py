LOCAL_TIMEZONE: float = 0  # UTC+ timezone to use as default

COLOR_MAIN = (40 / 255, 40 / 255, 92 / 255)  # DARK BLUE
COLOR_SECONDARY = (255 / 255, 214 / 255, 0 / 255)  # YELLOW

import matplotlib.dates as mdates
DATE_FORMATTER = mdates.DateFormatter("%d - %b")
