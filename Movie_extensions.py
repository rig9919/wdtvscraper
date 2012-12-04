from types import MethodType
from tmdb3 import Movie
import unicodedata, re, string, urllib
from datetime import date

def clean_title(self, is_original_title = False):
    # return the Movie object's title with all punctuation removed
    # and replaced with a single space or nulled
    if is_original_title:
        s = self.originaltitle
    else:
        s = self.title
    # replace en-dash and em-dash with a regular minus-dash
    s = s.replace( u'\u2013', '-')
    s = s.replace( u'\u2014', '-')
    # get rid of accents and use the closest english letter
    s = unicodedata.normalize('NFKD', unicode(s)).encode('ascii','ignore')
    s = s.replace( '&', 'and')
    s = s.replace( ' III', ' 3')
    s = s.replace( ' II', ' 2')
    s = s.replace( '\'', '')
    s = s.replace( ' - ', ' ')
    s = s.replace( '-', ' ')
    s = s.replace( '/', ' ')
    s = s.replace( '. ', ' ')
    s = s.replace( '.', ' ')
    s = s.replace( ': ', ' ')
    s = s.replace( ':', ' ')
    s = re.sub('[%s]' % re.escape(string.punctuation), '', s)
    return str(s)

def is_title_match(self, possible_matching_title):
    # check to see if a Movie object's clean title matches with ours
    if self.clean_title().lower() == possible_matching_title.lower():
        return True
    # see if the original language title matches with ours
    if self.clean_title(True).lower() == possible_matching_title.lower():
        return True
    return False

def earliest_releasedate(self):
    earliest = date(9999,12,31)
    for release in self.releases.iteritems():
        if release[1].releasedate < earliest:
            earliest = release[1].releasedate
    if earliest == date(9999,12,31):
        earliest = '????'
    return earliest


#def loc_releasedate(self):
#    country = str(get_locale().country)
#    print self.releases
#    default_country_key = str(self.releases.keys()[0])
#    default_country_release = self.releases.get(default_country_key)
#    #print default_country_release
#    releasedate = self.releases.get(country, default_country_release).releasedate
#    return releasedate

def year(self):
    # return year of the Movie object based on it's releasedate
    # if no releasedate listed, return '????'
    year_found = re.search('\d\d\d\d', str(self.earliest_releasedate()))
    if year_found:
        return year_found.group(0)
    return '????'

def is_year_match(self, possible_matching_year):
    # see if the Movie object's year matches with ours
    if self.year() == possible_matching_year:
        return True
    return False

def full_title(self):
    # return title in the form 'X-Men Origins: Wolverine (2009)'
    return self.title + ' (' + str(self.year()) + ')'

def download_poster(self, size, name):
    poster_url = self.poster.geturl(size)
    urllib.urlretrieve(poster_url, name + '.metathumb')

def get_genres(self):
    genre_names = list()
    for item in self.genres:
        genre_names.append(item.name)
    return ', '.join(genre_names)

def build_xml(self, destination, thumbnails):
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

Movie.clean_title = MethodType(clean_title, None, Movie)
Movie.is_title_match = MethodType(is_title_match, None, Movie)
Movie.earliest_releasedate = MethodType(earliest_releasedate, None, Movie)
Movie.year = MethodType(year, None, Movie)
Movie.is_year_match = MethodType(is_year_match, None, Movie)
Movie.full_title = MethodType(full_title, None, Movie)
Movie.download_poster = MethodType(download_poster, None, Movie)
Movie.get_genres = MethodType(get_genres, None, Movie)
Movie.build_xml = MethodType(build_xml, None, Movie)
