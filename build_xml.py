import unicodedata
import re
import codecs


def write_tvshow(series, episode, destination):
    xml = list()

    xml.append('<?xml version="1.0"?>'
                 '<!DOCTYPE note ['
                 '<!ELEMENT details (id, title, series_name, episode_name, '
                                    'season_number, episode_number, '
                                    'firstaired, genre, runtime, director, '
                                    'actor, overview)>'
                 '<!ELEMENT id (#PCDATA)>'
                 '<!ELEMENT title (#PCDATA)>'
                 '<!ELEMENT series_name (#PCDATA)>'
                 '<!ELEMENT episode_name (#PCDATA)>'
                 '<!ELEMENT season_number (#PCDATA)>'
                 '<!ELEMENT episode_number (#PCDATA)>'
                 '<!ELEMENT firstaired (#PCDATA)>'
                 '<!ELEMENT genre (#PCDATA)>'
                 '<!ELEMENT runtime (#PCDATA)>'
                 '<!ELEMENT director (#PCDATA)>'
                 '<!ELEMENT actor (#PCDATA)>'
                 '<!ELEMENT overview (#PCDATA)>'
                 ']>')

    xml.append('<details>')
    xml.append('  <id>' + unicode(episode.tvdbId) + '</id>')
    #title = '%s: S%sE%s %s' % (series.name, episode.seasonNumber.zfill(2),
    #                           episode.episodeNumber.zfill(2), episode.name)
    xml.append('  <title>' + unicode(episode.name) + '</title>') 
    xml.append('  <series_name>' + unicode(series.name) + '</series_name>')
    xml.append('  <episode_name>' + unicode(episode.name) + '</episode_name>')
    xml.append('  <firstaired>' + unicode(episode.firstAired) + '</firstaired>')
    # tv view does not give each genre its own item
    xml.append('  <genre>' + '/'.join(series.genres) + '</genre>')
    xml.append('  <runtime>' + 'N/A' + '</runtime>')
    xml.append('  <director>' + '/'.join(episode.director) + '</director>')
    # tv view does not give each actor their own item
    xml.append('  <actor>' + '/'.join(actor.name for actor in series.actors) + '</actor>')
    # overview is a list for some reason
    if len(episode.overview) > 0:
        xml.append('  <overview>' + episode.overview[0] + '</overview>')
    xml.append('</details>')

    f = codecs.open(destination, encoding='utf-8', mode='w')
    for line in xml:
        f.write(unicode(line) + u'\n')
    f.close()

def write_movie(mov, destination, thumbnails):
    '''
    write meta information to a file

    mov: tmdb3.Movie object to get info from
    destination: destination of file to write
    thumbnails: boolean describing whether to include thumbnail URLs or not
                this is included because on the WDTV if thumbnail URLs are
                known, it will try and use those before the local .metathumb
                files which slows movie browsing down
    '''

    xml = list()

    xml.append('<?xml version="1.0"?>'
                 '<!DOCTYPE note ['
                 '<!ELEMENT details (id, imdb_id, title, mpaa, year, runtime, '
                                    'rating, trailer, genre, studio, plot, '
                                    'overview, director, actor, thumbnail, '
                                    'backdrop)>'
                 '<!ELEMENT id (#PCDATA)>'
                 '<!ELEMENT imdb_id (#PCDATA)>'
                 '<!ELEMENT title (#PCDATA)>'
                 '<!ELEMENT mpaa (#PCDATA)>'
                 '<!ELEMENT year (#PCDATA)>'
                 '<!ELEMENT runtime (#PCDATA)>'
                 '<!ELEMENT rating (#PCDATA)>'
                 '<!ELEMENT trailer (#PCDATA)>'
                 '<!ELEMENT genre (#PCDATA)>'
                 '<!ELEMENT studio (#PCDATA)>'
                 '<!ELEMENT plot (#PCDATA)>'
                 '<!ELEMENT overview (#PCDATA)>'
                 '<!ELEMENT director (#PCDATA)>'
                 '<!ELEMENT actor (#PCDATA)>'
                 '<!ELEMENT thumbnail (#PCDATA)>'
                 '<!ELEMENT backdrop (#PCDATA)>'
                 ']>')

    xml.append('<details>')
    xml.append('  <id>' + unicode(mov.id) + '</id>')
    xml.append('  <imdb_id>' + unicode(mov.imdb) + '</imdb_id>')
    xml.append('  <title>' + mov.title + '</title>')
    if 'US' in mov.releases:
        xml.append('  <mpaa>' + mov.releases['US'].certification + '</mpaa>')
    xml.append('  <year>' + unicode(mov.releasedate) + '</year>')
    xml.append('  <runtime>' + unicode(mov.runtime) + '</runtime>')
    xml.append('  <rating>' + unicode(mov.userrating) + '</rating>')
    for trailer in mov.youtube_trailers:
        xml.append('  <trailer>' + trailer.geturl() + '</trailer>')
    for trailer in mov.apple_trailers:
        #best_quality = trailer.sizes()[len(trailer.sizes()) - 1]
        #xml += '<trailer>' + trailer.geturl(best_quality) + '</trailer>'
        if '480p' in trailer.sizes():
            xml.append('  <trailer>' + trailer.geturl('480p') + '</trailer>')
    for genre in mov.genres:
        xml.append('  <genre>' + genre.name + '</genre>')
    for studio in mov.studios:
        xml.append('  <studio>' + studio.name + '</studio>')
    xml.append('  <plot>' + mov.overview + '</plot>')
    xml.append('  <overview>' + mov.overview + '</overview>')
    for member in mov.crew:
        if member.job.lower() == 'director':
            xml.append('  <director>' + member.name + '</director>')
    for actor in mov.cast:
        xml.append('  <actor>\n'
                         '    <name>' + actor.name + '</name>\n'
                         '    <role>' + actor.character + '</role>\n'
                         '  </actor>')
    if thumbnails:
        for poster in mov.posters:
            xml.append('  <thumbnail>' + poster.geturl('w185') +
                                                                '</thumbnail>')
    for backdrop in mov.backdrops:
        xml.append('  <backdrop>' + backdrop.geturl('w780') + '</backdrop>')
    xml.append('</details>')

    f = codecs.open(destination + '.xml', encoding='utf-8', mode='w')
    for line in xml:
        line = re.sub(u'[&]', u'&amp;', line)
        f.write(unicode(line) + u'\n')
    f.close()
