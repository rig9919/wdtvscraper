import os
import urllib
import urllib2
import re
from pytvdb import shortsearch, longsearch
import common
from common import remove_punc
import build_xml


class LocalSeries(object):

    def __init__(self, name, language):
        self.seriesname = name
        match = self.__get_series_match(self.seriesname)
        self.series_data = self.__get_series_info(match.tvdbId, language)

    def save_poster(self, destination):
        _save_poster(self.series_data.posterUrl, destination,
                     self.seriesname, 900)

    def __get_series_match(self, name):
        '''
        searches tvdb for a series with the title <name>
        returns any series that matches
        '''

        base_results = shortsearch.searchForShortSeries(name)
        #TODO: if more than one result, let user choose
        #for s in base_results:
        #    print s.name
		
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

    def __get_series_info(self, tvdbId, language):
        '''
        returns information on a series with the id <tvdbId>
        '''

        try:
            return longsearch.searchForLongSeries(tvdbId, language)
        except urllib2.HTTPError as e:
            if e.code == 404:
                print 'HTTP Error 404:', language, 'is not a valid language.'
            elif e.code == 504:
                print 'HTTP Error 504: thetvdb.com is not responding.'
            elif e.code == 503:
                print 'HTTP Error 503: thetvdb.com is overloaded.',\
                      'Try again later.'
            exit()

    def __clean_series_name(self, name, preserve_encoding=True):
        '''
        return a tv series name with all punctuation removed

        preserve_encoding: used to determine whether or not to keep accents and
                           other unicode characters or replace them with their
                           most similar looking ascii counterparts
        '''

        words = remove_punc(name, preserve_encoding)
        return ' '.join(words)


class LocalEpisode(object):

    def __init__(self, path, series_data):
        '''
        use episode identification information in <path>'s name to init

        path: path to target episode file
        '''

        self.series_data = series_data
        # split pathname into useful things upon creation
        self.__abspath = os.path.abspath(path)
        self.__dirpath = os.path.split(self.__abspath)[0]
        self.__filename = os.path.splitext(os.path.split(self.__abspath)[1])
        self.basename = self.__filename[0]
        self.ext = self.__filename[1]
        # extract the season and episode number from the basename
        self.season_num = int(self.__get_episode_id()['season'])
        self.episode_num = int(self.__get_episode_id()['episode'])
        # retrieve episode data
        self.episode_data = self.__get_match(self.series_data.episodes)

    def save_poster(self, destination):
        _save_poster(self.episode_data.bannerUrl, destination,
                     self.basename, 40)

    def save_metadata(self, destination):
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
        if re.search('S\d+E\d+', re.escape(self.basename), re.IGNORECASE):
            season = re.search('(S(?P<season>\d+)E\d+)', re.escape(self.basename),
                               re.IGNORECASE).group('season')
            # must use findall because sometimes files may consist of two episodes
            # such as star-trek-deep-space-nine-s04e01-s04e02.mkv
            # always use first episode number in these cases
            episode = re.findall('(S\d+E(?P<episode>\d+))', re.escape(self.basename),
                                 re.IGNORECASE)[0][1]
        elif re.search('\d+(x|X)\d+', re.escape(self.basename), re.IGNORECASE):
            season = re.search('(?P<season>\d+)(x|X)\d+', re.escape(self.basename),
                               re.IGNORECASE).group('season')
            episode = re.findall('\d+(x|X)(?P<episode>\d+)', re.escape(self.basename),
                                 re.IGNORECASE)[0][1]
        else:
            season = '0'
            episode = '0'
        return {'season': season, 'episode': episode}


def _save_poster(location, destination, basename, max_size):
    # If there is no art, carry on
    if location == '':
        print "No poster available: %s" % (basename)
        return
    max_size = max_size*1024
    urllib.urlretrieve(location, destination)
    while os.path.getsize(destination) > max_size:
        size = os.path.getsize(destination)
        print 'Poster size (' + str(size/1024) + 'K)', 'over 40K,',\
              'reducing quality by 10%.'
        r = os.system('convert -strip "' + destination + '" -quality 90% ' +
                       'JPEG:"' + destination + '"')
        if r or os.path.getsize(destination) == size:
            raise IOError('Could not reduce poster size.')


