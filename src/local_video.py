import os
import re
from PIL import Image
from pytmdb3 import tmdb3
from common import split_full_title, get_input, print_possible_match_table, uni
import common


class LocalVideo:
    '''
    object used to describe a video file on the user's machine
    contains methods for searching tmdb for movie info
    '''

    def __init__(self, path):
        '''
        use movie title information contained in <path>'s filename to init

        path: path to target movie file
        '''

        # split pathname into useful things upon creation
        self.__abspath = uni(os.path.abspath(path))
        self.__dirpath = uni(os.path.split(self.__abspath)[0])
        self.__filename = os.path.splitext(os.path.split(self.__abspath)[1])
        self.basename = uni(self.__filename[0])
        self.ext = uni(self.__filename[1])
        # extract the title and year from the basename
        self.title = split_full_title(self.basename, False)['title']
        self.year = split_full_title(self.basename)['year']
        self.full_title = self.title + ' (' + self.year + ')'
        # unicode support
        self.uni_title = split_full_title(self.basename)['title']
        self.uni_full_title = self.uni_title + ' (' + self.year + ')'
        self.tmdb_data = None
        self.matched_method = None

    def get_match(self, assume_match):
        # get match from tmdb
        self.tmdb_data = self.__get_match(assume_match)
        self.matched_method = self.tmdb_data['method']
        self.tmdb_data = self.tmdb_data['data']

    def __get_possible_match_list(self):
        '''
        return the results from searching tmdb for the object's title w/ year
        failing that, return the results of a search for the title
        if no results for either search, return None
        '''

        # search for unicode movie title with year
        results = tmdb3.searchMovieWithYear(self.uni_full_title)
        # if no results, search for unicode title without year
        if not results:
            results = tmdb3.searchMovie(self.uni_title)

        return results

    def __get_match(self, assume_match=False):
        '''
        search the results for a movie match
        a match is defined as anything that has the same title and year
        return the first match found
        if the user used the <assume_match> switch and there is only one result
            return it as a match without checking if title and years are same
        '''

        possible_matches = self.__get_possible_match_list()
        if not possible_matches:
            raise common.ZeroMatchlist(self.basename)

        if assume_match:
            if len(possible_matches) == 1:
                title_matched = possible_matches[0].is_title_match(self.uni_title)
                year_matched = possible_matches[0].is_year_match(self.year)
                if (title_matched and year_matched):
                    return {'data': possible_matches[0], \
                            'method': title_matched}
                return {'data': possible_matches[0], \
                        'method': 'assumed'}
        for item in possible_matches:
            # if the year and title are the same, it is most likely a match
            # first, check if unicode title matches
            title_matched = item.is_title_match(self.uni_title)
            year_matched = item.is_year_match(self.year)
            if (title_matched and year_matched):
                return {'data': item, 'method': title_matched}
            # now check if ascii title matches
            title_matched = item.is_title_match(self.title)
            if (title_matched and year_matched):
                return {'data': item, 'method': title_matched}
        raise common.NonzeroMatchlistNoMatches(self.basename,
                                               len(possible_matches))


