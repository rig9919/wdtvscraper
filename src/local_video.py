import os
import re
from pytmdb3 import tmdb3
from common import split_full_title, get_input
import common

MAXRESULTS = 20


def print_possible_match_table(mlist):
    '''
    print summarized information of every Movie contained in <mlist>

    mlist: a list of Movies gotten from the search results
    '''
    for i, item in enumerate(mlist[0:MAXRESULTS]):
        s = unicode(i) + ') ' + item.full_title() + ' # ' + item.overview
        print s[0:80]
        #print str(i) + ')', item.full_title(), '#', item.overview[0:80]


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
        self.__abspath = os.path.abspath(path)
        self.__dirpath = os.path.split(self.__abspath)[0]
        self.__filename = os.path.splitext(os.path.split(self.__abspath)[1])
        self.basename = self.__filename[0]
        self.ext = self.__filename[1]
        # extract the title and year from the basename
        self.title = split_full_title(self.basename, False)['title']
        self.year = split_full_title(self.basename)['year']
        self.full_title = self.title + ' (' + self.year + ')'
        # unicode support
        self.uni_title = split_full_title(self.basename)['title']
        self.uni_full_title = self.uni_title + ' (' + self.year + ')'
        self.tmdb_data = None
        self.is_assumed = True

    def get_match(self, assume_match):
        # get match from tmdb
        self.tmdb_data = self.__get_match(assume_match)
        self.is_assumed = self.tmdb_data['is_assumed']
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
                if (possible_matches[0].is_title_match(self.title) and
                    possible_matches[0].is_year_match(self.year)):
                    return {'data': possible_matches[0], 'is_assumed': False}
                return {'data': possible_matches[0], 'is_assumed': True}
        for item in possible_matches:
            # if the year and title are the same, it is most likely a match
            # first, check if unicode title matches
            if (item.is_title_match(self.uni_title) and
                item.is_year_match(self.year)):
                return {'data': item, 'is_assumed': False}
            # now check if ascii title matches
            if (item.is_title_match(self.title) and
                item.is_year_match(self.year)):
                return {'data': item, 'is_assumed': False}
        raise common.NonzeroMatchlistNoMatches(self.basename,
                                               len(possible_matches))

    def get_chosen_match(self, custom_title=''):
        '''
        allow user to choose from a list of results that were retrieved with
           by searching for the object's title
        if <custom_title> is used, user chooses from results retrieved by
           searching for that instead
        '''

        if custom_title != '':
            results = tmdb3.searchMovie(custom_title)
        else:
            results = tmdb3.searchMovie(self.uni_title)

        while True:
            # display the search results
            print_possible_match_table(results)
            if len(results) < MAXRESULTS:
                valid_movies = len(results) - 1
            else:
                valid_movies = MAXRESULTS - 1

            # ask user to decide which title matches
            user_input = get_input('Which title matches ' + self.basename +
                                  '? (N=none/#m=more detail) ',
                                  '(^$)|(^(N|n)$)|(^(Q|q)$)|(^\d{1,2}(M||m)$)',
                                  valid_movies)
            # they chose none so return None
            if re.match('(^$)|(^(N|n)$)', user_input):
                return
            # they chose to quit the program
            elif re.match('^(Q|q)$', user_input):
                exit()
            # they want more information on a movie
            elif re.match('^\d{1,2}(m|M)$', user_input):
                option = re.search('.$', user_input).group(0)
                choice = re.search('^\d{1,2}', user_input).group(0)
                # make sure they picked a valid movie choice
                if int(choice) < MAXRESULTS and int(choice) < len(results):
                    item = results[int(choice)]
                else:
                    # their choice was invalid, start from the top
                    continue

                # show more information if they chose option m
                if re.match('^(m|M)$', option):
                    # give user a preview of the poster
                    try:
                        tmp = '.scrapertemp'
                        if os.path.isfile(tmp + '.metathumb'):
                            os.remove(tmp + '.metathumb')
                        item.download_poster('w342', tmp)
                        pil = __import__('PIL', fromlist=['Image'])
                        img = pil.Image.open(tmp + '.metathumb')
                        img.show()
                    except ImportError:
                        print 'Could not preview poster. PIL is required.'
                    except OSError:
                        pass
                    except:
                        print 'Could not preview poster'
                    finally:
                        if os.path.isfile(tmp + '.metathumb'):
                            os.remove(tmp + '.metathumb')

                    # print some summary information
                    print 'Title:', item.title, '\n' \
                          'Genres:', item.get_genres(), '\n' \
                          'Initial Release:', str(item.year()), '\n' \
                          'Runtime:', str(item.runtime), '\n' \
                          'IMDB id:', item.imdb, '\n' \
                          'Overview:', item.overview

                    # ask if this movie matches
                    user_input = get_input('Does this movie match yours? '
                                           '(yes/No) ',
                                          '(^$)|(^(Y|y)$)|(^(N|n)$)|(^(Q|q)$)')
                    # they chose yes, return this movie
                    if re.match('^(y|Y)$', user_input):
                        return item
                    # they chose no, start from the top
                    elif re.match('(^$)|(^(N|n)$)', user_input):
                        continue
                    # they chose to quit the program
                    elif re.match('^(q|Q)$', user_input):
                        exit()
            # they choose a movie from the search results
            elif re.match('^\d{1,2}$', user_input):
                choice = int(user_input)
            break

        # return the movie of their choice if it's valid
        if int(choice) < len(results):
            return results[int(choice)]
        return