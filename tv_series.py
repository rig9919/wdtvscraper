import os
import re
from pytvdb import shortsearch, longsearch
from common import remove_punc


class LocalEpisode:

    def __init__(self, path):
        '''
        use episode identification information in <path>'s name to init

        path: path to target episode file
        '''

        # split pathname into useful things upon creation
        self.__abspath = os.path.abspath(path)
        self.__dirpath = os.path.split(self.__abspath)[0]
        self.__filename = os.path.splitext(os.path.split(self.__abspath)[1])
        self.basename = self.__filename[0]
        self.ext = self.__filename[1]
        # extract the season and episode number from the basename
        self.season_num = int(get_episode_id(self.basename)['season'])
        self.episode_num = int(get_episode_id(self.basename)['episode'])

    def get_match(self, episode_list):
        '''
        search <episode_list> for an episode match
        return any episode that matches
        a match is defined as anything that has same season and episode numbers
        '''

        for episode in episode_list:
            if (int(episode.seasonNumber) == self.season_num
                and int(episode.episodeNumber) == self.episode_num):
                return episode
        return


def clean_series_name(name, preserve_encoding=True):
    '''
    return a tv series name with all punctuation removed

    preserve_encoding: used to determine whether or not to keep accents and
                       other unicode characters or replace them with their
                       most similar looking ascii counterparts
    '''

    words = remove_punc(name, preserve_encoding)
    return ' '.join(words)


def get_episode_id(name):
    '''
    returns a dict containing the season number and episode number of <name>
    '''

    season = re.search('(S(?P<season>\d\d)E\d\d)', name,
                       re.IGNORECASE).group('season')
    # must use findall because sometimes files may consist of two episodes
    # such as star-trek-deep-space-nine-s04e01-s04e02.mkv
    # always use first episode number in these cases
    episode = re.findall('(S\d\dE(?P<episode>\d\d))', name,
                        re.IGNORECASE)[0][1]
    return {'season': season, 'episode': episode}


def get_series_match(dir_name):
    '''
    searches tvdb for a series with the title <dir_name>
    returns any series that matches
    '''

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
    '''
    returns information on a series with the id <tvdbId>
    '''

    return longsearch.searchForLongSeries(tvdbId)
