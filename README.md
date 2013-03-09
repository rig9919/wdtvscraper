wdtvscraper  
===========  

Prerequisites:
* Python. Tested on 2.7.2. Unknown if it works on Python 3.
* Imagemagick.

Optional:
* Python Imaging Library. Available through your distribution's repository or
http://www.pythonware.com/products/pil/  

Suggested use:
Run in non-interactive mode. Review what couldn't be found. Then run in 
interactive mode. The assume option is useful in cases where your filename has 
a typo or wrong year attached to it. Always make sure to review what was 
assumed, though, because it can lead to mismatches. If there was a mismatch 
you will need to delete the .metathumb and .xml files of the movie directly 
and re-run it with the interactive option. This program will not overwrite 
them. The language and country options are for controlling what language the 
overview will be in and for deciding which title and poster to use.

<pre>
usage: scraper.py [options] -m movie-path
       scraper.py [options] -t tv-path

Scrape themoviedb.org for metadata of movies and tv series stored on a WDTV
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
