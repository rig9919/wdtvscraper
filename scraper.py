import Movie_extensions
from local_video import Local_video
from tmdb3 import set_key, set_locale, get_locale, set_cache
import os, re, argparse
# filenames MUST be named the-movie-title-<year>.ext
# and should be named using your language, not necessarily the original title

def main():
    parser = argparse.ArgumentParser(description='Scrape themoviedb.org for ' 
                                      'metadata of movies stored on a WDTV ' 
                                      'Live Hub.')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-t', '--thumbnails', action='store_true',
                        help='Set to include remote thumbnail urls in xml. '
                             'This may slow thumbnail loading.')
    parser.add_argument('-l', '--language', default='None',
                        help='Two letter abbrev. Such as \'en\' or \'de\'')
    parser.add_argument('-c', '--country', default='None',
                        help='Two letter abbrev. Such as \'fi\' or \'tk\'')
    parser.add_argument('path', help='The path to the directory containing '
                        'your movie files.')
    args = parser.parse_args()
    
    # configurations for tmdb api
    set_key('ae90cf3b0ab5da570880728198701ce0')
    if args.language == 'None' and args.country == 'None':
        set_locale(fallthrough=True)
    else:
        if args.language != 'None':
            set_locale(language=args.language, fallthrough=True)
        if args.country != 'None':
            set_locale(country=args.country, fallthrough=True)
    print 'Using locale: ' + str(get_locale())

    # set up a list for storing failed matches
    failed = list()
    
    # move to the directory containing the movies and process it
    os.chdir(args.path)
    for f in os.listdir('./'):
        if not re.search('(\.avi|\.vob|\.iso|\.wmv|\.mkv|\.mov|\.dat|\.tp|'
                         '\.ts|\.m2t|\.m2ts|\.flv|.mp4)$', f):
            # not a format wdtv supports
            continue
        videofile = Local_video(f)
        if (os.path.isfile(videofile.basename + '.metathumb') and
            os.path.isfile(videofile.basename + '.xml')):
            # metathumb and xml already exists for this movie
            continue
        match = videofile.get_match()
        if match is None:
            # no perfect matches were found
            if args.interactive == False:
                failed.append('Failed to find match for: ' + 
                              videofile.basename)
                continue
            # ask user for some help finding their movie
            match = videofile.get_chosen_match()
            while match is None:
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
            print 'Match for %s found: %s'%(videofile.basename, 
                                            match.full_title())
            if os.path.isfile(videofile.basename + '.metathumb'):
                print 'Did not save poster image: %s already exists'%(
                        videofile.basename + '.metathumb')
            else:
                match.download_poster('w342', videofile.basename)
            if os.path.isfile(videofile.basename + '.xml'):
                print 'Did not save metadata: %s already exists'%(
                        videofile.basename + '.xml')
            else:
                match.build_xml(videofile.basename, args.thumbnails)
        else:
            print 'No match found for %s'%(videofile.basename)
    
    print '\n'.join(failed)
    if len(failed) > 0:
        print 'Run in interactive mode to fix any failures manually.'

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        exit()
