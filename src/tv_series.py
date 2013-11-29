import os
import sys
import urllib
import urllib2
import unicodedata
import re
from pytvdb import shortsearch, longsearch
import common
from common import remove_punc, get_input, notify, print_possible_match_table,\
                   get_chosen_match, ask_alternative, uni, draw_mosaic,\
                   download_file, show_images_retrieved
import build_xml

class LocalSeries(object):

    def __init__(self, name, language, interactive, max_results):
        self.seriesname = uni(name)
        match = self.__get_series_match(self.seriesname, language, interactive,
                                         max_results)
        self.series_data = self.__get_series_info(match.tvdbId, language)

    def save_poster(self, destination, choose):
        if choose:
            print 'Creating image selection palette(s)...'
            poster_qty = _get_all_posters(self.series_data.posterUrl)
            if poster_qty <= 1:
                print 'No palette created,', poster_qty, 'image(s) available'
                _save_poster(self.series_data.posterUrl, destination,
                             self.seriesname, 900)
                return
            draw_mosaic(poster_qty)
            choice = get_input('Choose an image to use for series poster: ',
                               '(^$)|(^(Q|q)$)|(^\d{1,2}$)',
                               1, poster_qty)
            if re.match('^(Q|q)$', choice):
                exit()
            if not choice:
                posterUrl = self.series_data.posterUrl
            else:
                posterUrl = re.sub('(http://.*)-(\d{1,2})\.(.{3,4})',
                                   '\\1-' + choice + '.\\3',
                                   self.series_data.posterUrl)
            _save_poster(posterUrl, destination, self.seriesname, 900)
        else:
            _save_poster(self.series_data.posterUrl, destination,
                         self.seriesname, 900)

    def __get_series_match(self, name, language, interactive, max_results):
        '''
        searches tvdb for a series with the title <name>
        returns any series that matches
        '''

        clean_name = unicodedata.normalize('NFKD',
                                           unicode(name)).encode('ascii', 'ignore')
        base_results = shortsearch.searchForShortSeries(clean_name, language)
        if not base_results and not interactive:
            raise common.ZeroMatchlist(name)
		
        for series in base_results:
            # check if unicode titles match
            if (self.__clean_series_name(series.name).lower() ==
                self.__clean_series_name(name).lower()):
                return series
            # check if ascii titles match
            if (self.__clean_series_name(series.name, False).lower() ==
                self.__clean_series_name(name, False).lower()):
                return series
        # no series found, give user choice if they want
        if not interactive:
            raise common.NoSeriesException(name)
        series = get_chosen_match(name, base_results, max_results)
        while not series:
            users_title = ask_alternative()
            if not users_title:
                # user skipped entering a title, assuming user gave up
                raise common.NoSeriesException(self.seriesname)
            results = shortsearch.searchForShortSeries(users_title, language)
            series = get_chosen_match(users_title, results, max_results)
        return series

    def __get_series_info(self, tvdbId, language):
        '''
        returns information on a series with the id <tvdbId>
        '''

        try:
            return longsearch.searchForLongSeries(tvdbId, language)
        except urllib2.HTTPError as e:
            if e.code == 404:
                notify('http 404 error', language + ' probably is invalid')
            elif e.code == 504:
                notify('http 504 error', 'thetvdb.com is not responding')
            elif e.code == 503:
                notify('http 503 error', 'thetvdb.com is busy, try later')
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

    def __init__(self, path, series_data, use_dvdorder):
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
        self.episode_data = self.__get_match(self.series_data.episodes, use_dvdorder)

    def save_poster(self, destination):
        _save_poster(self.episode_data.bannerUrl, destination,
                     self.basename, 40)

    def save_metadata(self, destination, use_dvdorder):
        build_xml.write_tvshow(self.series_data, self.episode_data,
                               destination, use_dvdorder)

    def __get_match(self, episode_list, use_dvdorder):
        '''
        search <episode_list> for an episode match
        return any episode that matches
        a match is defined as anything that has same season and episode numbers
        '''
        if use_dvdorder:
            for episode in episode_list:
                if episode.dvd_seasonNumber and episode.dvd_episodeNumber:
                    if (float(episode.dvd_seasonNumber) == float(self.season_num)
                        and float(episode.dvd_episodeNumber) == float(self.episode_num)):
                        return episode
        else:
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

def _get_all_posters(location):
    '''
    download all available posters that share series with the one at location
    return number of available posters
    '''

    if not location:
        return 0

    # delete all temporary wdposters so series arent accidentally mixed
    filelist = os.listdir('/tmp')
    for f in filelist:
        if f.startswith('wdposter'):
            os.remove('/tmp/' + f)

    baseurl = '/'.join(location.split('/')[:-1])
    filename = location.split('/')[-1]
    basename, ext = filename.split('.')
    seriesno, posterno = basename.split('-')
    i = 1
    try:
        while True:
            location = baseurl + '/' + seriesno + '-' + str(i) + '.' + ext
            download_file(location, '/tmp/wdposter' + str(i) + '.' + ext)
            show_images_retrieved(i)
            i = i + 1
    except urllib2.HTTPError as e:
        return i-1

def _save_poster(location, destination, basename, max_size):
    # If there is no art, carry on
    if not location:
        notify('warning:', 'no image available for ' + basename)
        return
    max_size = max_size*1024
    urllib.urlretrieve(location, destination)
    is_reduced = False
    while os.path.getsize(destination) > max_size:
        size = os.path.getsize(destination)
        r = os.system('convert -strip "' + destination + '" -quality 90% ' +
                       'JPEG:"' + destination + '"')
        if r or os.path.getsize(destination) == size:
            is_reduced = True
            break
    if is_reduced:
        notify('warning:', 'image quality reduced and useless data removed for '
               + basename, sys.stderr)


