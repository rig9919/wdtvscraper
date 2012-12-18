import os
import re
from pytvdb import shortsearch, longsearch
from common import remove_punc


class LocalEpisode:

    def __init__(self, path):
        # split pathname into useful things upon creation
        self.__abspath = os.path.abspath(path)
        self.__dirpath = os.path.split(self.__abspath)[0]
        self.__filename = os.path.splitext(os.path.split(self.__abspath)[1])
        self.basename = self.__filename[0]
        self.ext = self.__filename[1]
        # extract the season and episode number from the basename
        self.season_num = int(get_episode_id(self.basename)['season'])
        self.episode_num = int(get_episode_id(self.basename)['episode'])


def clean_series_name(name, preserve_encoding=True):
    words = remove_punc(name, preserve_encoding)
    return ' '.join(words)

def get_episode_id(name):
    season = re.search('(S(?P<season>\d\d)E)', name, 
                       re.IGNORECASE).group('season')
    episode = re.search('(E(?P<episode>\d\d)$)', name, 
                        re.IGNORECASE).group('episode')
    return { 'season': season, 'episode': episode }

def get_series_match(dir_name):
    base_results = shortsearch.searchForShortSeries(dir_name)
    for series in base_results:
        # check if unicode titles match
        if (clean_series_name(series.name).lower() ==
            clean_series_name(dir_name).lower()):
            return series
        # check if ascii titles match
        if (clean_series_name(series.name, False).lower() ==
            clean_series_name(dir_name, False).lower()):
            return series
    return


def get_series_info(tvdbId):
    return longsearch.searchForLongSeries(tvdbId)


def is_match(self, season_num, episode_num, title=''):
    if self.seasonNumber == season_num and self.episodeNumber == episode_num:
        return True
    if self.name == title:
        return True
    return False


longsearch.EpisodeData.is_match = is_match
