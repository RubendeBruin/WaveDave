from datetime import timedelta, datetime

import wavedave.settings as Settings


def MostLikelyMatch(search_for, choices) -> str or bool:
    """Uses rapidfuzz to get a best match"""

    try:
        from rapidfuzz import process, fuzz

        best = process.extractOne(search_for, choices, scorer=fuzz.WRatio)
        return best[0]
    except:
        return False


def human_time(time: datetime, timezone_utc_plus=0, format=None):
    """Returns the time in human-readable format"""
    # apply timezone by adding the offset in hours to the time
    time = time + timedelta(hours=timezone_utc_plus)

    if format is None:
        format = Settings.DATE_FORMAT

    return time.strftime(format)
