import re
import os
import sys
import urllib
import unicodedata
from PIL import Image
from pytmdb3 import tmdb3
from pytvdb import shortsearch


def uni(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj

class NoSeriesException(Exception):

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return '%s: matches no series' % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')


class NoEpisodeException(Exception):

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return '%s: matches no episodes' % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')


class NonzeroMatchlistNoMatches(Exception):

    def __init__(self, name, results):
        self.name = name
        self.results = uni(results)

    def __unicode__(self):
        return ('%s: %s results found but none matched'
                % (self.name, self.results))

    def __str__(self):
        return unicode(self).encode('utf-8')

    #def __str__(self):
    #    return ('%s: %s results found but none matched'
    #            % (self.name, self.results))


class ZeroMatchlist(Exception):

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return '%s: no results' % (self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

def notify(identity, message, stream=sys.stdout):
    print >> stream, identity.encode('utf-8') + ':', message.encode('utf-8')

def remove_punc(name, preserve_encoding=True):
    '''
    remove the punctuation from <name>
    returns a list of words in <name>

    preserve_encoding: determines if the accents and other unicode characters
                       should be preserved or instead replaced with similar
                       looking ascii characters
    '''

    # get rid of any accents and other unicode characters if told
    if not preserve_encoding:
        if isinstance(name, str):
            name = name.decode('utf-8')
        name = unicodedata.normalize('NFKD',
                                      unicode(name)).encode('ascii', 'ignore')
    name = re.sub('&', 'and', name)
    name = re.sub('\'', '', name)
    # get the list of words
    words = re.findall('\w+', name)
    return words


def split_full_title(title, preserve_encoding=True):
    '''
    get the title and year from the full title
    returns a dict consisting of the title and year

    title: the full title as a string
    '''

    words = remove_punc(title, preserve_encoding)

    # if there's no words, return empty dict
    if len(words) == 0:
        return {'title': '', 'year': ''}
    # if the words list contains only a number, treat it as title
    if len(words) == 1:
        if words[0].isdigit():
            return {'title': words[0], 'year': ''}
    # look at the last item in the words list
    if words[len(words) - 1].isdigit():
        # if it's digits, then it represents the year and the
        # second-to-last item is the end of the title
        return {'title': ' '.join(words[0:len(words) - 1]),
                'year': words[len(words) - 1]}
    else:
        # if it's not, then the year is not in the name so we make one up
        # and give title the entire contents of the word list
        return {'title': ' '.join(words),
                'year': ''}

def get_input(prompt, valid_choice_pattern, choice_list_length=-1):
    '''
    use <prompt> to ask for input from a user
    validate their input with <valid_choice_pattern> and <choice_list_length>

    prompt: message used to ask user for input
    valid_choice_pattern: regex used to match user input against
    choice_list_length: number used validate movie choice because regex
                        can't match number ranges
    '''

    prompt = prompt.encode('utf-8')

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
            notify('error', 'invalid choice')

def print_possible_match_table(mlist, max_results=20):
    '''
    print summarized information of everything contained in <mlist>

    list: a list of possible matches gotten from the search results
    '''

    if not mlist:
        return

    for i, item in enumerate(mlist[0:max_results]):
        if isinstance(item, shortsearch.ShortSeriesData):
            title = item.name
            if item.overview:
                overview = item.overview[0]
            else:
                overview = 'no overview available'
        else:
            title = item.full_title()
            overview = item.overview
        s = unicode(i) + ') ' + title + ' # ' + overview
        print s[0:80]

def get_chosen_match(basename, results, max_results=20):
    '''
    allow user to choose from a list of results that were retrieved with
       by searching for the object's title
    '''

    if not results:
        print 'no search results'
        return

    while True:
        # display the search results
        print_possible_match_table(results)
        if len(results) < max_results:
            valid_movies = len(results) - 1
        else:
            valid_movies = max_results - 1

        # ask user to decide which title matches
        user_input = get_input('Which title matches ' + basename +
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
            if int(choice) < max_results and int(choice) < len(results):
                item = results[int(choice)]
            else:
                # their choice was invalid, start from the top
                continue

            # show more information if they chose option m
            if re.match('^(m|M)$', option):
                # give user a preview of the poster
                preview_available = False
                tmp = '/tmp/wdpreview'
                if os.path.isfile(tmp):
                    os.remove(tmp)
                if isinstance(item, tmdb3.Movie):
                    item.download_poster('w342', tmp)
                elif isinstance(item, shortsearch.ShortSeriesData):
                    if item.bannerUrl:
                        urllib.urlretrieve(item.bannerUrl, tmp)
                if os.path.isfile(tmp):
                    preview_available = True
                    img = Image.open(tmp)
                    img.show(tmp)
                    os.remove(tmp)

                # print some summary information
                if isinstance(item, tmdb3.Movie):
                    print 'Title:', item.title, '\n' \
                          'Genres:', item.get_genres(), '\n' \
                          'Initial Release:', str(item.year()), '\n' \
                          'Runtime:', str(item.runtime), '\n' \
                          'IMDB id:', item.imdb, '\n' \
                          'Overview:', item.overview, '\n' \
                          'Preview available:', preview_available
                elif isinstance(item, shortsearch.ShortSeriesData):
                    if item.overview:
                        overview = item.overview[0]
                    else:
                        overview = 'no overview available'
                    print 'Title:', item.name, '\n' \
                          'Airdate:', item.firstAiredDate, '\n' \
                          'TVDB id:', item.tvdbId, '\n' \
                          'Overview:', overview, '\n' \
                          'Preview available:', preview_available

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

def ask_alternative():
    try:
        user_typed_title = raw_input('Enter a possible alternative'
                                     ' title (S=skip): ')
        if user_typed_title in 'Ss' or not user_typed_title:
            return
        elif user_typed_title in 'Qq':
            exit()
        return user_typed_title
    except (SystemExit, KeyboardInterrupt):
        exit()
    except (ValueError, EOFError):
        notify('error', 'invalid choice')
        return

