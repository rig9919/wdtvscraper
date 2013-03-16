import re
import sys
import unicodedata

class NoSeriesException(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s: matches no series' % (self.name)


class NoEpisodeException(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s: matches no episodes' % (self.name)


class NonzeroMatchlistNoMatches(Exception):

    def __init__(self, name, results):
        self.name = name
        self.results = str(results)

    def __str__(self):
        return ('%s: %s results found but none matched'
                % (self.name, self.results))


class ZeroMatchlist(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '%s: no results' % (self.name)

def notify(identity, message, stream=sys.stdout):
    print >> stream, identity + ':', message

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

