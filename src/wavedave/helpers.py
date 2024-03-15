def MostLikelyMatch(search_for, choices) -> str or bool:
    """Uses rapidfuzz to get a best match"""

    try:
        from rapidfuzz import process, fuzz

        best = process.extractOne(search_for, choices, scorer=fuzz.WRatio)
        return best[0]
    except:
        return False