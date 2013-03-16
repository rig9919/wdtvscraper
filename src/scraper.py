#!/usr/bin/env python

import sys
import os
import re
import argparse
import PIL
import urllib
from pytmdb3 import tmdb3
import movie_extensions
from local_video import LocalVideo
from tv_series import LocalSeries, LocalEpisode
from common import notify
import common
import build_xml

__version__ = '1.2.4'


def main():
    parser = argparse.ArgumentParser(prog='wdtvscraper', add_help=False,
                       usage='%(prog)s [options] -m movie-path\n'
                      '       %(prog)s [options] -t tv-path',
                                     description='Scrape themoviedb.org and'
                                     ' thetvdb.com for metadata of movies and'
                                     ' tv series stored on a WDTV device.')
    required_args = parser.add_argument_group('requirements',
                                              'at least one is required')
    required_args.add_argument('-m', '--movie-path', default='', metavar='',
                         help='The path to the directory containing your '
                              'movie files.')
    required_args.add_argument('-t', '--tv-path', default='', metavar='',
                        help='The path to the directory containing your tv '
                             'series directories.')
    global_opts = parser.add_argument_group('global options')
    global_opts.add_argument('-l', '--language', default='', metavar='LN',
                        help='Where LN is a language code from ISO 639-1. '
                             'Common codes include en/de/nl/es/it/fr/pl')
    global_opts.add_argument('-q', '--quiet', action='store_true',
                        help='Suppress unimportant messages.')
    global_opts.add_argument('-f', '--force-overwrite', action='store_true',
                        help='Force overwrite of metadata and poster files.')
    movie_opts = parser.add_argument_group('movie scraping options')
    movie_opts.add_argument('-c', '--country', default='', metavar='CN',
                        help='Where CN is a country code from '
                             'ISO 3166-1 alpha-2. '
                             'Common codes include us/gb/de/nl/it/fr/pl')
    movie_opts.add_argument('-i', '--interactive', action='store_true')
    movie_opts.add_argument('-a', '--assume', action='store_true',
                        help='Assume match on 1 result. Not recommended. '
                             'This can lead to mismatches.')
    movie_opts.add_argument('-T', '--thumbnails', action='store_true',
                        help='Set to include remote thumbnail urls in xml. '
                             'This may slow thumbnail loading.')
    info_opts = parser.add_argument_group('informational arguments')
    info_opts.add_argument('-V', '--version', action='version',
                        version=__version__)
    info_opts.add_argument('-h', '--help', action='help')
    args = parser.parse_args()

    # if user didn't specify a tv path or movie path, tell them
    if not args.movie_path and not args.tv_path:
        print 'Must use -m and/or -t option. See help menu'

    # if user specified a movie path, process movies
    if args.movie_path:
        args.movie_path = os.path.join(os.getcwd(), args.movie_path)
        process_movies(args.movie_path, args.thumbnails, args.assume,
                       args.interactive, args.quiet, args.force_overwrite,
                       args.language, args.country)

    # if user specified a tv path, process tv shows
    if args.tv_path:
        args.tv_path = os.path.join(os.getcwd(), args.tv_path)
        process_tv(args.tv_path, args.interactive, args.quiet,
                   args.force_overwrite, args.language)


def process_movies(path, thumbnails, assume, interactive, quiet, force_overwrite,
                   language, country):
    # configurations for tmdb api
    tmdb3.set_key('ae90cf3b0ab5da570880728198701ce0')
    if (not language) and (not country):
        tmdb3.set_locale(fallthrough=True)
    else:
        if language:
            tmdb3.set_locale(language=language, fallthrough=True)
        if country:
            tmdb3.set_locale(country=country, fallthrough=True)
    if not quiet:
        print 'Using locale: ' + str(tmdb3.get_locale())

    # change to the movie path and process each movie file
    orig_path = os.getcwd()
    os.chdir(path)
    for f in os.listdir('./'):
        if not re.search('(\.avi|\.vob|\.iso|\.wmv|\.mkv|\.m4v|\.mov|\.dat|\.tp|'
                         '\.ts|\.m2t|\.m2ts|\.flv|.mp4)$', f):
            # not a format wdtv supports
            continue
        # create a new LocalVideo object using the movie file
        videofile = LocalVideo(f)
        if (os.path.isfile(videofile.basename + '.metathumb') and
            os.path.isfile(videofile.basename + '.xml') and (not force_overwrite)):
            # metathumb and xml already exists for this movie
            notify(videofile.basename, 'skipped poster/metadata', sys.stderr)
            continue
        # find a matching title from tmdb
        try:
            videofile.get_match(assume)
            if videofile.is_assumed:
                notify(videofile.basename, 'assumed only result matched')
        except common.NonzeroMatchlistNoMatches as e:
            print >> sys.stderr, e
        except common.ZeroMatchlist as e:
            print >> sys.stderr, e

        # if no matches are found, either ask user for help or continue
        if not videofile.tmdb_data:
            # no matches were found in non-interactive mode, continue to next
            if not interactive:
                continue
            # ask user for some help finding their movie if in interactive mode
            videofile.tmdb_data = videofile.get_chosen_match()
            while not videofile.tmdb_data:
                try:
                    # keep asking until user gives up or gets their title
                    user_typed_title = raw_input('Enter a possible alternative'
                                                 ' title (S=skip): ')
                    if user_typed_title in 'Ss' or not user_typed_title:
                        # user decides to give up
                        break
                    elif user_typed_title in 'Qq':
                        exit()
                    videofile.tmdb_data = videofile.get_chosen_match(
                                                              user_typed_title)
                except (SystemExit, KeyboardInterrupt):
                    exit()
                except (ValueError, EOFError):
                    print 'Error: invalid choice'
                    continue

        if videofile.tmdb_data:
            if not quiet:
                notify(videofile.basename,
                       'matches ' + videofile.tmdb_data.full_title())

            # deal with poster
            if (os.path.isfile(videofile.basename + '.metathumb')
               and not force_overwrite):
                notify(videofile.basename, 'skipped poster', sys.stderr)
            else:
            # if there's any posters available, download w342 size
            # preferably. otherwise, get the smallest available.
                if videofile.tmdb_data.poster:
                    if 'w342' in videofile.tmdb_data.poster.sizes():
                        videofile.tmdb_data.download_poster('w342',
                                                            videofile.basename)
                    else:
                        videofile.tmdb_data.download_poster(
                                         videofile.tmdb_data.poster.sizes()[0],
                                         videofile.basename)
                else:
                    notify(videofile.basename,
                           'skipped poster, none available', sys.stderr)

            # deal with metadata
            if (os.path.isfile(videofile.basename + '.xml')
               and not force_overwrite):
                notify(videofile.basename, 'skipped metadata', sys.stderr)
            else:
                videofile.tmdb_data.write_metadata(videofile.basename,
                                                   thumbnails)
        else:
            notify(videofile.basename, 'not found', sys.stderr)
    # go back to original path we started with
    os.chdir(orig_path)


def process_tv(path, interactive, quiet, force_overwrite, language):
    series_cover = path + '/00aa-series-cover.metathumb'
    if not language:
        language = 'en'
    # process each directory in path
    orig_path = os.getcwd()
    os.chdir(path)
    dirname = os.path.basename(os.getcwd())
    # for d in os.listdir('./'):
    if os.path.isdir(path):
        # assume the directory name is a tv show name and create a
        # LocalSeries object using it
        try:
            series = LocalSeries(dirname, language)
        except common.NoSeriesException as e:
            print >> sys.stderr, e
            return
            # continue

        if not quiet:
            notify(dirname, 'matches ' + series.series_data.name)

        try:
            if os.path.isfile(series_cover) and not force_overwrite:
                notify(dirname, 'skipped cover', sys.stderr)
            else:
                series.save_poster(series_cover, interactive)
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
                episode = LocalEpisode(f, series.series_data)
            except common.NoEpisodeException as e:
                print >> sys.stderr, e
                continue

            # check to see if a poster and metadata file already exist
            if (os.path.isfile(path + '/' + episode.basename +
                '.metathumb') and
                os.path.isfile(path + '/' + episode.basename + '.xml') and
                (not force_overwrite)):
                notify(episode.basename, 'skipped screenshot/metadata',
                       sys.stderr)
                continue

            if not quiet:
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
                                      '.xml')
            except IOError as e:
                print >> sys.stderr, e
    # go back to original path we started with
    os.chdir(orig_path)

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        exit()
