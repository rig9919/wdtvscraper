from pytvdb import shortsearch, longsearch
from common import split


def get_series_match(dir_name):
    base_results = shortsearch.searchForShortSeries(dir_name)
    for series in base_results:
        # check if unicode titles match
        if (split(series.name)['title'].lower() ==
            split(dir_name)['title'].lower()):
            return series
        # check if ascii titles match
        if (split(series.name, False)['title'].lower() ==
            split(dir_name, False)['title'].lower()):
            return series
    return
