import os
import sys
import re
from datetime import date
from pytmdb3 import tmdb3
import build_xml
from common import split_full_title, draw_mosaic, download_file, get_input, \
                   show_images_retrieved, reduce_size, notify

'''
This is a set of helper methods for the tmdb3.Movie class.
'''

# FIXME: Ideally, these additions to the tmdb3.Movie class would not be needed.
# LocalVideo should be a child of tmdb3.Movie and should contain these methods
# itself. Unfortunately, due to the way tmdb3.Movie objects are created, it is
# unknown at this time how to proceed.

def is_title_match(self, possible_matching_title):
    '''
    compare title with <possible_matching_title>
    returns method that matched:
        *
        orig = original title it was released with
        local = localized title
        *
        exact = titles match exactly
        words = some extra punctuation in one of the titles but all words match
        *
        ascii = all accents and non-ascii characters have been replaced
        uni = accents and special characters included
    '''

    if self.originaltitle.lower() == possible_matching_title.lower():
        return 'orig_exact_uni'

    if self.title.lower() == possible_matching_title.lower():
        return 'local_exact_uni'

    if (split_full_title(self.originaltitle)['title'].lower() ==
        possible_matching_title.lower()):
        return 'orig_words_uni'
    if (split_full_title(self.originaltitle, False)['title'].lower() ==
        possible_matching_title.lower()):
        return 'orig_words_ascii'

    if (split_full_title(self.title)['title'].lower() ==
        possible_matching_title.lower()):
        return 'local_words_uni'
    if (split_full_title(self.title, False)['title'].lower() ==
        possible_matching_title.lower()):
        return 'local_words_ascii'

    # nothing matches
    return False


def earliest_releasedate(self):
    '''
    return the initial release date known to tmdb, regardless of country
    if there's no release date information, return None
    '''

    earliest = date(9999, 12, 31)
    for release in self.releases.iteritems():
        if release[1].releasedate < earliest:
            earliest = release[1].releasedate
    if earliest == date(9999, 12, 31):
        return
    return earliest


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
    return true if the year and <possible_matching_year> are the same
    '''

    if self.year() == possible_matching_year:
        return True
    return False


def full_title(self):
    '''
    return title in the form 'Movie Title (YYYY)'
    example: 'X-Men Origins: Wolverine (2009)
    '''

    return self.title + ' (' + str(self.year()) + ')'


def download_poster(self, size, destination, choose):
    '''
    download associated movie poster

    size: w92, w154, w185, w342, w500, or original
          see http://help.themoviedb.org/kb/api/configuration
    name: name to save it as
    '''

    if choose:
        print 'Creating image selection palette(s)...'
        posters = _get_all_posters(self.posters, size)
        poster_qty = len(posters)
        if poster_qty <= 1:
            print 'No palette created,', poster_qty, 'image(s) available'
            return download_file(self.poster.geturl(size), destination)
        draw_mosaic(posters)
        choice = get_input('Choose an image to use for movie poster: ',
                           '(^$)|(^(Q|q)$)|(^\d{1,2}$)',
                           1, poster_qty)
        if re.match('^(Q|q)$', choice):
            exit()
        if not choice:
            poster_url = self.poster.geturl(size)
        else:
            poster_url = self.posters[int(choice)-1].geturl(size)
    else:
        poster_url = self.poster.geturl(size)
    image = download_file(poster_url, destination)
    if destination == 'temp':
        return image
    is_reduced = reduce_size(destination, 90)
    if is_reduced:
        notify('warning', 'image quality reduced and useless data removed for '
                + os.path.splitext(os.path.basename(destination))[0], sys.stderr)


def _get_all_posters(poster_list, size):
    poster_files = []
    for i,poster in enumerate(poster_list):
        show_images_retrieved(i, len(poster_list))
        poster_url = poster.geturl(size)
        poster_files.append(download_file(poster_url, 'temp'))
    return poster_files


def get_genres(self):
    '''
    return a string listing all the genres
    '''

    genre_names = list()
    for item in self.genres:
        genre_names.append(item.name)
    return ', '.join(genre_names)


def write_metadata(self, dest, use_thumbnails):
    build_xml.write_movie(self, dest, use_thumbnails)


# give the tmdb3.Movie class our new methods
tmdb3.Movie.is_title_match = is_title_match
tmdb3.Movie._earliest_releasedate = earliest_releasedate
tmdb3.Movie.year = year
tmdb3.Movie.is_year_match = is_year_match
tmdb3.Movie.full_title = full_title
tmdb3.Movie.download_poster = download_poster
tmdb3.Movie.get_genres = get_genres
tmdb3.Movie.write_metadata = write_metadata
