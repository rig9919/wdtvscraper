import unicodedata, re, urllib
from datetime import date
from pytmdb3 import tmdb3
from common import split

def extend_init(self):
    self.year = self._get_year()
    self.full_title = self._get_full_title()
    self.genre_string = self._get_genres()

def is_title_match(self, possible_matching_title):
    '''
    compare object's title with <possible_matching_title>
    '''

    # see if the movie title matches exactly
    if self.title.lower() == possible_matching_title.lower():
        return True
    # check to see if a Movie object's clean title matches with ours
    if split(self.title)['title'].lower() == possible_matching_title.lower():
        return True
    # see if the original language title matches with ours
    if (split(self.originaltitle)['title'].lower() == 
                                              possible_matching_title.lower()):
        return True
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

def get_year(self):
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

    if self.year == possible_matching_year:
        return True
    return False

def get_full_title(self):
    '''
    return object's title in the form 'Movie Title (YYYY)'
    example: 'X-Men Origins: Wolverine (2009)
    '''

    return self.title + ' (' + str(self.year) + ')'

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

def build_xml(self, destination, thumbnails):
    '''
    write meta information to a file

    destination: destination of file to write
    thumbnails: boolean describing whether to include thumbnail URLs or not
                this is included because on the WDTV if thumbnail URLs are
                known, it will try and use those before the local .metathumb
                files which slows movie browsing down
    '''

    xmlstring = '<details>'
    xmlstring += '<id>' + str(self.id) + '</id>'
    xmlstring += '<imdb_id>' + str(self.imdb) + '</imdb_id>'
    xmlstring += '<title>' + self.title + '</title>'
    if 'US' in self.releases:
        xmlstring += '<mpaa>' + self.releases['US'].certification + '</mpaa>'
    xmlstring += '<year>' + str(self.releasedate) + '</year>'
    xmlstring += '<runtime>' + str(self.runtime) + '</runtime>'
    xmlstring += '<rating>' + str(self.userrating) + '</rating>'
    for trailer in self.youtube_trailers:
        xmlstring += '<trailer>' + trailer.geturl() + '</trailer>'
    for trailer in self.apple_trailers:
        #best_quality = trailer.sizes()[len(trailer.sizes()) - 1]
        #xmlstring += '<trailer>' + trailer.geturl(best_quality) + '</trailer>'
        if '480p' in trailer.sizes():
            xmlstring += '<trailer>' + trailer.geturl('480p') + '</trailer>'
    for genre in self.genres:
        xmlstring += '<genre>' + genre.name + '</genre>'
    for studio in self.studios:
        xmlstring += '<studio>' + studio.name + '</studio>'
    xmlstring += '<plot>' + self.overview + '</plot>'
    xmlstring += '<overview>' + self.overview + '</overview>'
    for member in self.crew:
        if member.job.lower() == 'director':
            xmlstring += '<director>' + member.name + '</director>'
    for actor in self.cast:
        xmlstring += ('<actor>'
                     '<name>' + actor.name + '</name>'
                     '<role>' + actor.character + '</role>'
                     '</actor>')
    if thumbnails:
        for poster in self.posters:
            xmlstring += '<thumbnail>' + poster.geturl('w185') + '</thumbnail>'
    for backdrop in self.backdrops:
        xmlstring += '<backdrop>' + backdrop.geturl('w780') + '</backdrop>'
    xmlstring += '</details>'
    xmlstring = unicodedata.normalize('NFKD', unicode(xmlstring)).encode(
                                                              'ascii','ignore')
    xmlstring = re.sub('[&]', '&amp;', xmlstring)

    f = open(destination + '.xml', 'w')
    f.write(xmlstring)
    f.close()


# generate the extended attributes upon initialization
# FIXME: this is bad practice because if tmdb3.Movie is given a __init__
# function in the future it will be overriden by this one
tmdb3.Movie.__init__ = extend_init
# give the tmdb3.Movie class our new methods
tmdb3.Movie.is_title_match = is_title_match
tmdb3.Movie._earliest_releasedate = earliest_releasedate
tmdb3.Movie._get_year = get_year
tmdb3.Movie.is_year_match = is_year_match
tmdb3.Movie._get_full_title = get_full_title
tmdb3.Movie.download_poster = download_poster
tmdb3.Movie._get_genres = get_genres
tmdb3.Movie.build_xml = build_xml

