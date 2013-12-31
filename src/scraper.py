#!/usr/bin/env python

import sys
import os
import re
import argparse
import PIL
import urllib
import sqlite3
import time
import xml.etree.ElementTree as ET
from pytmdb3 import tmdb3
import movie_extensions
from local_video import LocalVideo
from tv_series import LocalSeries, LocalEpisode
from common import notify, get_chosen_match, ask_alternative, uni
import common
import build_xml

__version__ = '1.3.1'


def main():
    args = init_parser()
    # if user didn't specify a tv path or movie path, tell them
    if not args.movie_paths and not args.tv_paths \
                            and not args.media_library:
        print '-m/-t/-L option is necessary.'

    # repair library if requested
    if args.media_library and not args.movie_paths and not args.tv_paths:
        if not os.path.isfile(args.media_library):
            notify('error', 'media library file does not exist')
            exit()
        modify_db(args.media_library, args.verbose, None, True)

    # process all the movie paths
    for path in args.movie_paths:
        path = parse_path(path)
        v=process_movies(path, args.thumbnails, args.assume, args.interactive,
                       args.verbose, args.force_overwrite, args.language,
                       args.country, int(args.max_results), args.choose_image)
        if args.media_library:
            modify_db(args.media_library, args.verbose, v)

    # process all the tv series paths
    if not args.language in 'en sv no da fi nl de it es fr pl hu el ' \
                            'tr ru he ja pt zh cs sl hr ko':
        notify('error', 'invalid language')
        exit()
    for path in args.tv_paths:
        path = parse_path(path)
        v=process_tv(path, args.interactive, args.verbose, args.force_overwrite,
                   args.language, args.choose_image, int(args.max_results),
                   args.dvd_ordering)
        if args.media_library:
            modify_db(args.media_library, args.verbose, v)

def parse_path(path):
    if path == '.' or path == './':
        return uni(os.getcwd())
    return uni(os.path.join(os.getcwd(), path))

def init_parser():
    parser = argparse.ArgumentParser(prog='wdtvscraper', add_help=False,
             usage='%(prog)s [options] -L db -m movie-paths... -t tv-paths...',
             description='Scrape themoviedb.org and thetvdb.com for '
                          'of movies and tv series stored on a WDTV device.')
    required_args = parser.add_argument_group('requirements',
                                              'at least one is required')
    required_args.add_argument('-m', '--movie-paths', default='', metavar='',
                               nargs='+', help='The paths to the directories '
                              'containing your movie files.')
    required_args.add_argument('-t', '--tv-paths', default='', metavar='',
                               nargs='+', help='The paths to the directories '
                              'containing your tv series files.')
    required_args.add_argument('-L', '--media-library', default='',
                               metavar='', help='The path to the sqlite3 '
                               'database file. When used in conjuction with '
                               'the -m or -t option, all new metadata found '
                               'is added to the database. With neither option '
                               'used, incomplete database records are updated '
                               'with any new metadata found on the device')
    global_opts = parser.add_argument_group('global options')
    global_opts.add_argument('-r', '--max-results', default=0, metavar='RS',
                        help='Where RS is the number of results to be '
                             'displayed in interactive mode.')
    global_opts.add_argument('-i', '--interactive', action='store_true',
                        help='Display search results for movies/series that '
                             'could not be matched automatically.')
    global_opts.add_argument('-g', '--choose-image', action='store_true',
                         help='Choose which image to use.')
    global_opts.add_argument('-l', '--language', default='', metavar='LN',
                        help='Where LN is a language code from ISO 639-1. '
                             'Common codes include en/de/nl/es/it/fr/pl. '
                             'TVDB languages are more restrictive.')
    global_opts.add_argument('-v', '--verbose', default=0, action='count',
                        help='Increase level of information up to 3 levels.')
    global_opts.add_argument('-f', '--force-overwrite', action='store_true',
                        help='Force overwrite of metadata and poster files.')
    movie_opts = parser.add_argument_group('movie scraping options')
    movie_opts.add_argument('-c', '--country', default='', metavar='CN',
                        help='Where CN is a country code from '
                             'ISO 3166-1 alpha-2. '
                             'Common codes include us/gb/de/nl/it/fr/pl')
    movie_opts.add_argument('-a', '--assume', action='store_true',
                        help='Assume match on 1 result. Not recommended. '
                             'This can lead to mismatches.')
    movie_opts.add_argument('-T', '--thumbnails', action='store_true',
                        help='Set to include remote thumbnail urls in xml. '
                             'This may slow thumbnail loading.')
    tv_opts = parser.add_argument_group('tv scraping options')
    tv_opts.add_argument('-d', '--dvd-ordering', action='store_true',
                        help='Series episodes are named in the same order as '
                             'they are on the DVD.')
    info_opts = parser.add_argument_group('informational arguments')
    info_opts.add_argument('-V', '--version', action='version',
                        version=__version__)
    info_opts.add_argument('-h', '--help', action='help')
    args = parser.parse_args()
    return args

def modify_db(db_file, verbose, videos, repair=False):
    wdtv_dir = os.path.dirname(os.path.dirname(db_file))
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    mlib_name = c.execute("SELECT name FROM folder WHERE filepath = './'").fetchone()[0]
    if verbose >= 3:
        notify('modifying media library', mlib_name)
    if not repair:
        broken = [ os.path.split(video) + ('new',) for video in videos ]
    else:
        broken = c.execute('''SELECT filepath, name, id FROM video 
                              WHERE title = name''').fetchall()
    for b in broken:
        b_filepath = b[0]
        b_name = b[1]
        b_id = b[2]
        b_fullpath = b_filepath + '/' + b_name
        b_fullpath_real = b_fullpath.replace('./' + mlib_name, wdtv_dir)
        b_dirname, b_filename = os.path.split(b_fullpath_real)
        b_basename, b_ext = os.path.splitext(b_filename)
        b_xml = (b_dirname + '/' + b_basename + '.xml')
        if not os.path.isfile(b_xml):
            if verbose >= 2:
                notify(os.path.basename(b_fullpath_real) + ' (' + str(b_id) + ')', 
                   'could not repair record in media library, no matching xml',
                   sys.stderr)
            continue
        tree = ET.parse(b_xml)
        director = tree.find('director')
        actors = tree.findall('actor/name')
        if director is not None:
            director = director.text
        else:
            director = ''
        if actors is not None:
            actors = [actor.text for actor in actors]
            actor = ' / '.join(actors)
        else:
            actor = ''
        if b_id == 'new':
            c.execute('SELECT * FROM video WHERE filepath = ? AND name = ?',
                       (b_filepath.replace(wdtv_dir, './' + mlib_name), b_name))
            record_exists = c.fetchall()
            if record_exists:
                notify(b_basename, 'record exists, not adding to db')
                continue
            c.execute('SELECT id FROM video ORDER BY id DESC LIMIT 1')
            rec_id = c.fetchone()[0] + 1
            _, ino, _, _, _, _, size, _, mtime, ctime = os.stat(b_fullpath_real)
            mtime_date = time.strftime('%Y/%m/%d', time.gmtime(mtime))
            season_name = episode_num = None
            series_name = tree.find('series_name')
            if series_name is not None:
                series_name = series_name.text
                season_num = tree.find('season_number').text
                season_name = 'Season %d' % (int(season_num))
                episode_num = tree.find('episode_number').text
            c.execute('INSERT INTO video VALUES (' + ','.join(35*'?') + ')',
                       (rec_id, 0, b_filename, b_filepath.replace(wdtv_dir, mlib_name),
                       tree.find('title').text, tree.find('genre').text,
                       mtime_date, season_name, series_name, episode_num,
                       0, size, ino, 0, 0, 0, mtime, ctime, 0, 0, 0, '', 0,
                       0, 0, 0, 0, -1, -1, 'Unknown', director, actor,
                       '', '', ''))
        else:
            c.execute('''UPDATE video
                         SET title = ?,
                             genre = ?,
                             director = ?,
                             actor = ?
                         WHERE name = ?
                         AND filepath = ?''',
                      (tree.find('title').text, tree.find('genre').text,
                       director, actor, b[1], b[0] ))
            if tree.find('series_name') is not None:
                c.execute('''UPDATE video
                             SET series_name = ?,
                                 season_name = ?,
                                 episode_num = ?
                             WHERE name = ?
                             AND filepath = ?''',
                          (tree.find('series_name').text,
                           'Season %d' % (int(tree.find('season_number').text)),
                           tree.find('episode_number').text, b[1], b[0]))
        conn.commit()
        if verbose >= 1:
            notify(b_basename + ' (' + str(b_id) + ')', 
                   'successfully repaired record')
        #print tree.find('id').text
    conn.close() 

def process_movies(path, thumbnails, assume, interactive, verbose,
                   force_overwrite, language, country, max_results,
                   choose_image):
    successful = []
    # configurations for tmdb api
    tmdb3.set_key('ae90cf3b0ab5da570880728198701ce0')

    # set language and country
    if (not language) and (not country):
        tmdb3.set_locale(fallthrough=True)
    else:
        if language:
            tmdb3.set_locale(language=language, fallthrough=True)
        if country:
            tmdb3.set_locale(country=country, fallthrough=True)

    if verbose >= 3:
        notify('processing', path)
        notify('locale', str(tmdb3.get_locale()))

    if not os.path.isdir(path):
        notify('warning', '\'' + path + '\' is not a directory', sys.stderr)
        return

    # process each file in path
    for f in os.listdir(path):
        # check if file is in a format that wdtv supports
        if not re.search('(\.avi|\.vob|\.iso|\.wmv|\.mkv|\.m4v|\.mov|\.dat|'
                          '\.tp|\.ts|\.m2t|\.m2ts|\.flv|.mp4)$', f):
            continue

        # create a new LocalVideo object using the movie file
        videofile = LocalVideo(f)

        if (os.path.isfile(path + '/' + videofile.basename + '.metathumb') and
            os.path.isfile(path + '/' + videofile.basename + '.xml') and 
            (not force_overwrite)):
            # metathumb and xml already exists for this movie
            if verbose >= 2:
                notify(videofile.basename, 'poster and metadata already exist', sys.stderr)
            continue

        # find a matching title from tmdb
        try:
            videofile.get_match(assume)
        except common.NonzeroMatchlistNoMatches as e:
            print >> sys.stderr, e
        except common.ZeroMatchlist as e:
            print >> sys.stderr, e

        if not videofile.tmdb_data:
            if not interactive:
                continue
            videofile.tmdb_data = manually_search_movie(videofile.basename,
                                                        videofile.uni_title,
                                                        max_results)

        if not videofile.tmdb_data:
            notify(videofile.basename, 'not found', sys.stderr)
            continue
    
        if verbose >= 1:
            if videofile.matched_method == 'assumed':
                notify(videofile.basename,
                       'assuming matches ' + videofile.tmdb_data.full_title())
            else:
                notify(videofile.basename,
                       'matches ' + videofile.tmdb_data.full_title())
    
        # deal with poster
        if (os.path.isfile(path + '/' + videofile.basename + '.metathumb')
           and not force_overwrite):
            if verbose >= 2:
                notify(videofile.basename, 'poster already exists', sys.stderr)
        else:
        # if there's any posters available, download w185 size
        # preferably. otherwise, get the smallest available.
            if videofile.tmdb_data.poster:
                if 'w342' in videofile.tmdb_data.poster.sizes():
                    videofile.tmdb_data.download_poster('w185',
                             path + '/' + videofile.basename + '.metathumb',
                             choose_image)
                else:
                    videofile.tmdb_data.download_poster(
                             videofile.tmdb_data.poster.sizes()[0],
                             path + '/' + videofile.basename + '.metathumb',
                             choose_image)
            else:
                notify(videofile.basename,
                       'no poster available', sys.stderr)
    
        # deal with metadata
        if (os.path.isfile(path + '/' + videofile.basename + '.xml')
           and not force_overwrite):
            if verbose >= 2:
                notify(videofile.basename, 'metadata already exists', sys.stderr)
        else:
            videofile.tmdb_data.write_metadata(
                                   path + '/' + videofile.basename + '.xml',
                                   thumbnails)
            successful.append(path + '/' + videofile.basename + videofile.ext)
    return successful



def manually_search_movie(basename, title, max_results):
    # ask user for some help finding their movie if in interactive mode
    results = tmdb3.searchMovie(title)
    tmdb_data = get_chosen_match(basename, results, max_results)
    while not tmdb_data:
        users_title = ask_alternative()
        if not users_title:
            return
        results = tmdb3.searchMovie(users_title)
        tmdb_data = get_chosen_match(users_title, results, max_results)
    return tmdb_data


def process_tv(path, interactive, verbose, force_overwrite, language,
               choose_image, max_results, dvd_ordering):
    successful = []
    # chop off trailing backslash if found
    if path[-1:] == '/':
        path = path[0:-1]

    series_image = path + '/00aa-series-cover.metathumb'
    if not language:
        language = 'en'
    if verbose >= 3:
        notify('processing', path)

    if not os.path.isdir(path):
        notify('warning', '\'' + path + '\' is not a directory', sys.stderr)
        return
    dirname = os.path.basename(path)
    basename = dirname

    if os.path.isdir(path):
        # assume the directory name is a tv show name and create a
        # LocalSeries object using it
        try:
            series = LocalSeries(basename, language, interactive, max_results)
        except common.NoSeriesException as e:
            print >> sys.stderr, e
            return
        except common.ZeroMatchlist as e:
            print >> sys.stderr, e
            return

        if verbose >= 1:
            notify(dirname, 'matches ' + series.series_data.name)

        try:
            if os.path.isfile(series_image) and (not force_overwrite):
                if verbose >= 2:
                    notify(dirname, 'series poster already exists', sys.stderr)
            else:
                series.save_poster(series_image, choose_image)
        except IOError as e:
            print >> sys.stderr, e

        # process each video in the directory
        for f in os.listdir(path):
            if not re.search('(\.avi|\.vob|\.iso|\.wmv|\.mkv|\.m4v|'
                             '\.mov|\.dat|\.tp|\.ts|\.m2t|\.m2ts|'
                             '\.flv|.mp4)$', f):
                continue

            # make a LocalEpisode object using the video's information
            try:
                episode = LocalEpisode(f, series.series_data, dvd_ordering)
            except common.NoEpisodeException as e:
                print >> sys.stderr, e
                continue

            # check to see if a poster and metadata file already exist
            if (os.path.isfile(path + '/' + episode.basename +
                '.metathumb') and
                os.path.isfile(path + '/' + episode.basename + '.xml') and
                (not force_overwrite)):
                if verbose >= 2:
                    notify(episode.basename, 'screenshot and metadata already exist',
                           sys.stderr)
                continue

            if verbose >= 1:
                if not episode.episode_data:
                    raise common.NoEpisodeException(episode.basename)
                notify(episode.basename, 'matches ' + episode.episode_data.name)

            # these are separate try blocks because if one fails
            # the other should still be completed
            try:
                episode.save_poster(path + '/' + episode.basename +
                                    '.metathumb')
            except IOError as e:
                print >> sys.stderr, e
            try:
                episode.save_metadata(path + '/' + episode.basename +
                                      '.xml', dvd_ordering)
                successful.append(path + '/' + episode.basename + episode.ext)
            except IOError as e:
                print >> sys.stderr, e
    return successful

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        exit()
