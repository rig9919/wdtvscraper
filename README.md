wdtvscraper  
===========  

Prerequisites:
--------------
* Python. Tested on 2.7.2. Unknown if it works on Python 3.
* Imagemagick.
* Python Imaging Library. Available through your distribution's repository or
http://www.pythonware.com/products/pil/  

Fetching movie information:
---------------------------
Run in non-interactive mode while supressing messages of success to get the 
metadata of easy titles and display any titles that failed: 
    wdtvscraper --quiet --movie-path /path/to/movies 

Possible reasons of failure are misspellings or having the wrong year attached 
to a movie's filename.

If everything is correct, run in interactive-mode so when a title couldn't be
found it gives you some options.
    wdtvscraper --interactive --movie-path /path/to/movies

Fetching tv series information:
-------------------------------
Interactive mode for tv series fetching does not give a selection of partial 
matches of a series, instead if gives a choice of which cover to use for the 
series it finds. (this could change in the future)

You must supply the directory of the tv series itself, not a parent directory 
of all your tv series directories.
    wdtvscraper --tv-path /path/to/tvshows/<seriesname>

To get the same functionality as if specifying the tvshows directory directly 
use a loop for now. Below is an example for bash users.
    for d in /path/to/tvshows/*; do wdtvscraper --tv-path "$d"; done;

Assume option:
--------------
The assume option is useful in cases where your filename has a typo or wrong 
year attached to it thus ensuring no match will ever be found. Always make 
sure to review what was assumed, though, because it can lead to mismatches.

Language/country options:
-------------------------
The language and country options are for controlling what language the 
overview will be in and for deciding which title and poster to use.

<pre>
usage: wdtvscraper [options] -m movie-path
       wdtvscraper [options] -t tv-path

Scrape themoviedb.org and thetvdb.com for metadata of movies and tv series stored on a WDTV
device.

requirements:
  at least one is required

  -m , --movie-path     The path to the directory containing your movie files.
  -t , --tv-path        The path to the directory containing your tv series
                        directories.

global options:
  -l LN, --language LN  Where LN is a language code from ISO 639-1. Common
                        codes include en/de/nl/es/it/fr/pl
  -q, --quiet           Suppress unimportant messages.
  -f, --force-overwrite
                        Force overwrite of metadata and poster files.

movie scraping options:
  -c CN, --country CN   Where CN is a country code from ISO 3166-1 alpha-2.
                        Common codes include us/gb/de/nl/it/fr/pl
  -i, --interactive
  -a, --assume          Assume match on 1 result. Not recommended. This can
                        lead to mismatches.
  -T, --thumbnails      Set to include remote thumbnail urls in xml. This may
                        slow thumbnail loading.

informational arguments:
  -V, --version         show program's version number and exit
  -h, --help

</pre>
