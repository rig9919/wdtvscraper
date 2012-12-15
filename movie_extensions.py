import re, urllib
from datetime import date
from pytmdb3 import tmdb3
import build_xml
from common import split

def is_title_match(self, possible_matching_title):
    '''
    compare object's title with <possible_matching_title>
    '''

    # <original title with punc> == <possible matching title> ?
    if self.originaltitle.lower() == possible_matching_title.lower():
        return True

    # <title with punc> == <possible matching title> ?
    if self.title.lower() == possible_matching_title.lower():
        return True

    # <original title, no punc> == <possible matching title> ?
    if (split(self.originaltitle)['title'].lower() == 
                                              possible_matching_title.lower()):
        return True
    # ... without unicode
    if (split(self.originaltitle, False)['title'].lower() == 
                                              possible_matching_title.lower()):
        return True

    # <title, no punc> == <possible matching title> ?
    if split(self.title)['title'].lower() == possible_matching_title.lower():
        return True
    # ... without unicode
    if (split(self.title, False)['title'].lower() == 
                                              possible_matching_title.lower()):
        return True

    # nothing matches
    return False

def earliest_releasedate(self):
    '''
    return the initial release date known to tmdb, regardless of country
    if there's no release date information, return None
    '''

    earliest = date(9999,12,31)
    for release in self.releases.iteritems():
        if release[1].releasedate < earliest:
            earliest = release[1].releasedate
    if earliest == date(9999,12,31):
        return
    return earliest


# TODO: decide whether or not to allow matches based on local release date
#def loc_releasedate(self):
#    country = str(get_locale().country)
#    print self.releases
#    default_country_key = str(self.releases.keys()[0])
#    default_country_release = self.releases.get(default_country_key)
#    #print default_country_release
#    releasedate = self.releases.get(country, default_country_release).releasedate
#    return releasedate

def year(self):
    '''
    return the year of the object based on it's earliest release date
    if no release date or year is found, return '????'
    '''

    # get the year of the earliest release date
    earliest_available = self._earliest_releasedate()
    if earliest_available:
        year_found = re.search('\d\d\d\d', str(earliest_available))
    else:
        year_found = None
    # if there was a year found, return it
    if year_found:
        return year_found.group(0)
    return '????'

def is_year_match(self, possible_matching_year):
    '''
    return true if object's year and <possible_matching_year> are the same
    '''

    if self.year() == possible_matching_year:
        return True
    return False

def full_title(self):
    '''
    return object's title in the form 'Movie Title (YYYY)'
    example: 'X-Men Origins: Wolverine (2009)
    '''

    return self.title + ' (' + str(self.year()) + ')'

def download_poster(self, size, name):
    '''
    download object's associated movie poster
    
    size: w92, w154, w185, w342, w500, or original
          see http://help.themoviedb.org/kb/api/configuration
    name: name to save it as
    '''

    poster_url = self.poster.geturl(size)
    urllib.urlretrieve(poster_url, name + '.metathumb')

def get_genres(self):
    '''
    return a string listing all the genres of the object
    '''

    genre_names = list()
    for item in self.genres:
        genre_names.append(item.name)
    return ', '.join(genre_names)

def write_metadata(self, dest, use_thumbnails):
    build_xml.write(self, dest, use_thumbnails)



# give the tmdb3.Movie class our new methods
tmdb3.Movie.is_title_match = is_title_match
tmdb3.Movie._earliest_releasedate = earliest_releasedate
tmdb3.Movie.year = year
tmdb3.Movie.is_year_match = is_year_match
tmdb3.Movie.full_title = full_title
tmdb3.Movie.download_poster = download_poster
tmdb3.Movie.get_genres = get_genres
tmdb3.Movie.write_metadata = write_metadata

