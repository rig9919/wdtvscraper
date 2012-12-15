#!/usr/bin/python

import os, re, argparse
from pytmdb3 import tmdb3
import movie_extensions
from local_video import LocalVideo
import common

VERSION = '0.1.5'

def main():
    parser = argparse.ArgumentParser(description='Scrape themoviedb.org for ' 
                                     'metadata of movies stored on a WDTV '
                                     'device.') 
    parser.add_argument('-V', '--version', action='version', version=VERSION)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-t', '--thumbnails', action='store_true',
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
    parser.add_argument('path', nargs='?', default=os.getcwd(), 
                         help='The path to the directory containing your '
                              'movie files.')
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

    # move to the directory containing the movies and process it
    os.chdir(args.path)
    for f in os.listdir('./'):
        if not re.search('(\.avi|\.vob|\.iso|\.wmv|\.mkv|\.mov|\.dat|\.tp|'
                         '\.ts|\.m2t|\.m2ts|\.flv|.mp4)$', f):
            # not a format wdtv supports
            continue
        videofile = LocalVideo(f)
        if (os.path.isfile(videofile.basename + '.metathumb') and
            os.path.isfile(videofile.basename + '.xml') and (not args.debug)):
            # metathumb and xml already exists for this movie
            continue
        # first, assume user has named their videos something using a standard
        # format such as the-movie-title-and-year.ext
        match = None
        try:
            match = videofile.get_match(args.assume)
        except common.AssumedMatch as e:
            match = e.movie
            print e
        except common.NonzeroMatchlistNoMatches as e:
            print e
        except common.ZeroMatchlist as e:
            print e
        if not match:
            # no matches were found in non-interactive mode, continue to next
            if not args.interactive:
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
            if args.verbose:
                print 'Match for %s found: %s'%(videofile.basename, 
                                                match.full_title())
            if args.debug: 
                continue
            if os.path.isfile(videofile.basename + '.metathumb'):
                print 'Did not save poster image: %s already exists'%(
                        videofile.basename + '.metathumb')
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
                    print ('Did not save poster image: no available '
                           'posters for %s'%(videofile.basename))
            if os.path.isfile(videofile.basename + '.xml'):
                print 'Did not save metadata: %s already exists'%(
                        videofile.basename + '.xml')
            else:
                match.write_metadata(videofile.basename, args.thumbnails)
        else:
            print 'No match found for %s'%(videofile.basename)

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        exit()
