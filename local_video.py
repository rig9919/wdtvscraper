import os, re
from pytmdb3 import tmdb3
from common import split
import common

MAXRESULTS = 20

def print_possible_match_table(possible_match_list):
    for i,item in enumerate(possible_match_list[0:MAXRESULTS]):
        print '  %i) %s # %s'%(i, item.full_title(), item.overview[0:80])

def get_input(prompt, valid_choice_pattern, choice_list_length=-1):
    while True:
        try:
            user_input = raw_input(prompt)
            if re.match(valid_choice_pattern, user_input):
                if re.match('\d{1,2}', user_input):
                    valid_movies = int(re.match('\d{1,2}', 
                                                user_input).group(0))
                    if valid_movies <= choice_list_length:
                        return user_input
                    else:
                        raise ValueError
                return user_input
            else:
                raise ValueError
        except (SystemExit, KeyboardInterrupt):
            exit()
        except (ValueError, EOFError):
            print 'invalid choice'

class LocalVideo:
    def __init__(self, path):
        # split pathname into useful things upon creation
        self.__abspath = os.path.abspath(path)
        self.__dirpath = os.path.split(self.__abspath)[0]
        self.__filename = os.path.splitext(os.path.split(self.__abspath)[1])
        self.basename = self.__filename[0]
        self.ext = self.__filename[1]
        self.title = split(self.basename)['title']
        self.year = split(self.basename)['year']
        # keep a dirty title for use in our exact-case-and-punctuation search
        self.dirty_title = re.sub(self.year, '', self.basename)
        self.full_title = self.title + ' (' + self.year + ')'
    def __get_possible_match_list(self):
        # get a list of matching movies from tmdb
        results = tmdb3.searchMovieWithYear(self.full_title)
        if len(results) == 0:
            results = tmdb3.searchMovie(self.title)
        return results
    def get_match(self, assume_match=False):
        possible_matches = self.__get_possible_match_list()
        if not possible_matches:
            raise common.ZeroMatchlist(self.basename)
            return
        if assume_match:
            if len(possible_matches) == 1:
                return possible_matches[0]
        for item in possible_matches:
            # if the year and title are the same, it is most likely a match
            if (item.is_title_match(self.title) and 
                item.is_year_match(self.year)):
                return item
        raise common.NonzeroMatchlistNoMatches(self.basename, 
                                               len(possible_matches))
        return
    def get_chosen_match(self, custom_title = ''):
        # ask user for name of movie to search for
        # display a list of matching movies from tmdb
        # allow user to choose a movie from the list that best matches theirs
        if custom_title != '':
            results = tmdb3.searchMovie(custom_title)
        else:
            results = tmdb3.searchMovie(self.title)
       
        while True:
            print_possible_match_table(results)
            if len(results) < MAXRESULTS:
                valid_movies = len(results) - 1
            else:
                valid_movies = MAXRESULTS - 1
            user_input = get_input('Which title matches ' + self.basename +
                                  '? (N=none/#m=more detail) ',
                                  '(^$)|(^(N|n)$)|(^(Q|q)$)|(^\d{1,2}(M||m)$)',
                                  valid_movies)
            if re.match('(^$)|(^(N|n)$)', user_input):
                return
            elif re.match('^(Q|q)$', user_input):
                exit()
            elif re.match('^\d{1,2}(m|M)$', user_input):
                option = re.search('.$', user_input).group(0)
                choice = re.search('^\d{1,2}', user_input).group(0)
                if int(choice) < MAXRESULTS and int(choice) < len(results):
                    item = results[int(choice)]
                else:
                    continue
                if re.match('^(m|M)$', option):
                    print ('Title: %s\n'
                          'Genres: %s\n'
                          'Initial Release: %s\n'
                          'Runtime: %s\n'
                          'IMDB id: %s\n'
                          'Overview: %s')%(item.title, item.get_genres(),
                                         str(item.earliest_releasedate()),
                                         str(item.runtime), item.imdb,
                                         item.overview)
                    user_input = get_input('Does this movie match yours? '
                                           '(yes/No) ', 
                                          '(^$)|(^(Y|y)$)|(^(N|n)$)|(^(Q|q)$)')
                    if re.match('^(y|Y)$', user_input):
                       return item
                    elif re.match('(^$)|(^(N|n)$)', user_input):
                       continue
                    elif re.match('^(q|Q)$', user_input):
                       exit()
            elif re.match('^\d{1,2}$', user_input):
                choice = int(user_input)
            break
        
        if int(choice) < len(results):
            return results[int(choice)]
        return

