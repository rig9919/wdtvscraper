#!/usr/bin/python

import os
import re
import argparse
import imp
from pytmdb3 import tmdb3
import movie_extensions
from local_video import LocalVideo
from tv_series import get_series_match, get_series_info, LocalEpisode
import common

__version__ = '0.2.6'


def main():
    try:
        imp.find_module('PIL')
    except ImportError:
        print 'Warning: Python Imaging Library is required.'
        print 'Warning: Check your distros repository for PIL.'
        print 'Warning: Continuing without ability to preview posters.'

    parser = argparse.ArgumentParser(prog='scraper.py',
                                     usage='%(prog)s [options] '
                                     '[-m movie-path] [-t tv-path]',
                                     description='Scrape themoviedb.org for '
                                     'metadata of movies stored on a WDTV '
                                     'device.')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-T', '--thumbnails', action='store_true',
                        help='Set to include remote thumbnail urls in xml. '
                             'This may slow thumbnail loading.')
    parser.add_argument('-l', '--language', default='', metavar='LN',
                        help='Where LN is a language code from ISO 639-1. '
                             'Common codes include en/de/nl/es/it/fr/pl')
    parser.add_argument('-c', '--country', default='', metavar='CN',
                        help='Where CN is a country code from '
                             'ISO 3166-1 alpha-2. '
                             'Common codes include us/gb/de/nl/it/fr/pl')
    parser.add_argument('-a', '--assume', action='store_true',
                        help='Assume match on 1 result. Not recommended '
                             'This can lead to mismatches.')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-m', '--movie-path', default='',
                         metavar='',
                         help='The path to the directory containing your '
                              'movie files.')
    parser.add_argument('-t', '--tv-path', default='',
                        metavar='',
                        help='The path to the directory containing your tv '
                             'series directories.')
    args = parser.parse_args()

    # configurations for tmdb api
    tmdb3.set_key('ae90cf3b0ab5da570880728198701ce0')
    if (not args.language) and (not args.country):
        tmdb3.set_locale(fallthrough=True)
    else:
        if args.language:
            tmdb3.set_locale(language=args.language, fallthrough=True)
        if args.country:
            tmdb3.set_locale(country=args.country, fallthrough=True)
    print 'Using locale: ' + str(tmdb3.get_locale())

    # if user specified a movie path, process movies
    if args.movie_path:
        process_movies(args.movie_path, args.thumbnails, args.assume,
                       args.interactive, args.verbose, args.debug)

    # if user specified a tv path, process tv shows
    if args.tv_path:
        process_tv(args.tv_path)

    if not args.movie_path and not args.tv_path:
        print 'Use -m and/or -t to specify paths to scrape. See help menu'


def process_movies(path, thumbnails, assume, interactive, verbose, debug):
    os.chdir(path)
    for f in os.listdir('./'):
        if not re.search('(\.avi|\.vob|\.iso|\.wmv|\.mkv|\.mov|\.dat|\.tp|'
                         '\.ts|\.m2t|\.m2ts|\.flv|.mp4)$', f):
            # not a format wdtv supports
            continue
        videofile = LocalVideo(f)
        if (os.path.isfile(videofile.basename + '.metathumb') and
            os.path.isfile(videofile.basename + '.xml') and (not debug)):
            # metathumb and xml already exists for this movie
            continue
        # first, assume user has named their videos something using a standard
        # format such as the-movie-title-and-year.ext
        match = None
        try:
            match = videofile.get_match(assume)
        except common.AssumedMatch as e:
            match = e.movie
            print e
        except common.NonzeroMatchlistNoMatches as e:
            print e
        except common.ZeroMatchlist as e:
            print e
        if not match:
            # no matches were found in non-interactive mode, continue to next
            if not interactive:
                continue
            # ask user for some help finding their movie if in interactive mode
            match = videofile.get_chosen_match()
            while not match:
                try:
                    # keep asking until user gives up or gets their title
                    user_typed_title = raw_input('Enter a possible alternative'
                                                 ' title (S=skip): ')
                    if (user_typed_title == '' or user_typed_title == 'S' or
                        user_typed_title == 's'):
                        # user decides to skip
                        break
                    elif user_typed_title == 'q' or user_typed_title == 'Q':
                        exit()
                    match = videofile.get_chosen_match(user_typed_title)
                except (SystemExit, KeyboardInterrupt):
                    exit()
                except (ValueError, EOFError):
                    print 'Error: invalid choice'
                    continue
        if match:
            if verbose:
                print 'Match for', videofile.basename, 'found:', \
                       match.full_title()
            if debug:
                continue
            if os.path.isfile(videofile.basename + '.metathumb'):
                print 'Did not save poster image:', videofile.basename + \
                      '.metathumb', 'already exists'
            else:
            # if there's any posters available, download w342 size
            # preferably. otherwise, get the smallest available.
                if match.poster:
                    if 'w342' in match.poster.sizes():
                        match.download_poster('w342', videofile.basename)
                    else:
                        match.download_poster(match.poster.sizes()[0],
                                              videofile.basename)
                else:
                    print 'Did not save poster image: no available ' \
                          'posters for', videofile.basename
            if os.path.isfile(videofile.basename + '.xml'):
                print 'Did not save metadata:', videofile.basename + '.xml', \
                      'already exists'
            else:
                match.write_metadata(videofile.basename, thumbnails)
        else:
            print 'No match found for', videofile.basename


def process_tv(path):
    os.chdir(path)
    for d in os.listdir('./'):
        if os.path.isdir(d):
            print d
            series_match = get_series_match(d)
            if not series_match:
                print 'No tv series found for:', d
                continue
            print 'Match for', d, 'found:', series_match.name
            series_info = get_series_info(series_match.tvdbId)
            print series_info
            os.chdir(d)
            for f in os.listdir('./'):
                if not re.search('(\.avi|\.vob|\.iso|\.wmv|\.mkv|\.mov|\.dat|'
                                 '\.tp|\.ts|\.m2t|\.m2ts|\.flv|.mp4)$', f):
                    continue
                # episode file found
                episode = LocalEpisode(f)
                print f, episode.season_num, episode.episode_num
            os.chdir('./..')
    print '*TV SCRAPING NOT IMPLEMENTED YET*'

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        exit()
