import re, unicodedata

class NonzeroMatchlistNoMatches(Exception):
    def __init__(self, name, results):
        self.name = name
        self.results = results
    def __str__(self):
        return ('Failed: There were ' + str(self.results) + ' results ' 
                'but no matches for ' + self.name)

class ZeroMatchlist(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return 'Failed: There were zero results for ' + self.name

def split(title):
    # get rid of any accents and other unicode characters
    title = unicodedata.normalize('NFKD', 
                                   unicode(title)).encode('ascii','ignore')
    title = re.sub('&', 'and', title)
    # split a complete title into the title and the year
    words = re.findall('\w+', title)
    # if there's no words, return empty dict
    if len(words) == 0:
        return {'title': '', 'year': ''}
    # look at the last item in the words list
    if words[len(words)-1].isdigit():
        # if it's digits, then it represents the year and the
        # second-to-last item is the end of the title
        return {'title': ' '.join(words[0:len(words)-1]), 
                'year': words[len(words)-1]}
    else:
        # if it's not, then the year is not in the name so we make one up
        # and give title the entire contents of the word list
        return {'title': ' '.join(words), 
                'year': ''}
