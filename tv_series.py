import os
import urllib
import re
from pytvdb import shortsearch, longsearch
import common
from common import remove_punc
import build_xml

class LocalSeries(object):

    def __init__(self, name):
        self.seriesname = name
        match = self.__get_series_match(self.seriesname)
        self.series_data = self.__get_series_info(match.tvdbId)

    def save_poster(self, destination):
        if os.path.isfile(destination):
            raise IOError('Did not save poster: ' + destination +
                          ' already exists')
        urllib.urlretrieve(self.series_data.posterUrl, destination)

    def __get_series_match(self, name):
        '''
        searches tvdb for a series with the title <name>
        returns any series that matches
        '''
    
        base_results = shortsearch.searchForShortSeries(name)
        for series in base_results:
            # check if unicode titles match
            if (self.__clean_series_name(series.name).lower() ==
                self.__clean_series_name(name).lower()):
                return series
            # check if ascii titles match
            if (self.__clean_series_name(series.name, False).lower() ==
                self.__clean_series_name(name, False).lower()):
                return series
        raise common.NoSeriesException(self.seriesname)
        
    def __get_series_info(self, tvdbId):
        '''
        returns information on a series with the id <tvdbId>
        '''

        return longsearch.searchForLongSeries(tvdbId)

    def __clean_series_name(self, name, preserve_encoding=True):
        '''
        return a tv series name with all punctuation removed
    
        preserve_encoding: used to determine whether or not to keep accents and
                           other unicode characters or replace them with their
                           most similar looking ascii counterparts
        '''
    
        words = remove_punc(name, preserve_encoding)
        return ' '.join(words)
    

class LocalEpisode(LocalSeries):

    def __init__(self, path, series_name):
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
        self.season_num = int(self.__get_episode_id()['season'])
        self.episode_num = int(self.__get_episode_id()['episode'])
        super(LocalEpisode, self).__init__(series_name)
        self.episode_data = self.__get_match(self.series_data.episodes)

    def save_poster(self, destination):
        if os.path.isfile(destination):
            raise IOError('Did not save poster: ' + destination +
                          ' already exists')
        urllib.urlretrieve(self.episode_data.bannerUrl, destination)

    def save_metadata(self, destination):
        if os.path.isfile(destination):
            raise IOError('Did not save metadata: ' + destination +
                          ' already exists')
        build_xml.write_tvshow(self.series_data, self.episode_data,
                               destination)

    def __get_match(self, episode_list):
        '''
        search <episode_list> for an episode match
        return any episode that matches
        a match is defined as anything that has same season and episode numbers
        '''

        for episode in episode_list:
            if (int(episode.seasonNumber) == self.season_num
                and int(episode.episodeNumber) == self.episode_num):
                return episode
        raise common.NoEpisodeException(self.basename)

    def __get_episode_id(self):
        '''
        returns a dict containing season number and episode number of object
        '''
    
        season = re.search('(S(?P<season>\d\d)E\d\d)', self.basename,
                           re.IGNORECASE).group('season')
        # must use findall because sometimes files may consist of two episodes
        # such as star-trek-deep-space-nine-s04e01-s04e02.mkv
        # always use first episode number in these cases
        episode = re.findall('(S\d\dE(?P<episode>\d\d))', self.basename,
                            re.IGNORECASE)[0][1]
        return {'season': season, 'episode': episode}
