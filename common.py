import re
import unicodedata


class AssumedMatch(Exception):

    def __init__(self, name, movie):
        self.name = name
        self.movie = movie

    def __str__(self):
        return ('Assumed match for ' + self.name + ' found: ' +
                self.movie.full_title())


class NonzeroMatchlistNoMatches(Exception):

    def __init__(self, name, results):
        self.name = name
        self.results = results

    def __str__(self):
        return 'No matches in ' + str(self.results) + ' results: ' + self.name


class ZeroMatchlist(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'No results: ' + self.name


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
    words: the full title split into a list
    '''

    words = remove_punc(title, preserve_encoding)

    # if there's no words, return empty dict
    if len(words) == 0:
        return {'title': '', 'year': ''}
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
