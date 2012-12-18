import unicodedata
import re
import codecs


def write(mov, destination, thumbnails):
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
    xml.append('  <id>' + str(mov.id) + '</id>')
    xml.append('  <imdb_id>' + str(mov.imdb) + '</imdb_id>')
    xml.append('  <title>' + mov.title + '</title>')
    if 'US' in mov.releases:
        xml.append('  <mpaa>' + mov.releases['US'].certification + '</mpaa>')
    xml.append('  <year>' + str(mov.releasedate) + '</year>')
    xml.append('  <runtime>' + str(mov.runtime) + '</runtime>')
    xml.append('  <rating>' + str(mov.userrating) + '</rating>')
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
