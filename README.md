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
```wdtvscraper --quiet --movie-path /path/to/movies```

Possible reasons of failure are misspellings or having the wrong year attached 
to a movie's filename. 

If everything is correct, run in interactive-mode so when a title couldn't be 
found it gives you some options. 
```wdtvscraper --interactive --movie-path /path/to/movies```

Multiple movie-paths are acceptable.
```wdtvscraper -m /path/to/movies1 /path/to/movies2 /media/wdtvlivehub```

Fetching tv series information:
-------------------------------
You must supply the directory of the tv series itself, not a parent directory 
of all your tv series directories. 
```wdtvscraper --tv-path /path/to/tvshows/<seriesname>```

If you want to fetch several tv series' information, use wildcards.
```wdtvscraper --tv-path /path/to/tvshows/*```

Interactive mode:
-----------------
In interactive mode you are given a chance to select a match for anything that 
could not be found by looking at your file/directory names.

Assume option: 
--------------
The assume option is useful in cases where your filename matches something so 
closely that there is only one result returned but it doesn't match exactly. 
Always make sure to review what was assumed, though, because it can lead to 
mismatches. 

Language/country options: 
-------------------------
The language and country options are for controlling what language the 
overview will be in and for deciding which title and poster to use. 

Choose cover option:
--------------------
When using the choose-cover option a mosaic of all the available covers for 
that series will be shown so you can select which one you want to be used.

<pre>
usage: wdtvscraper [options] -m movie-paths... -t tv-paths...

Scrape themoviedb.org and thetvdb.com for of movies and tv series stored on a
WDTV device.

requirements:
  at least one is required

  -m  [ ...], --movie-paths  [ ...]
                        The paths to the directories containing your movie
                        files.
  -t  [ ...], --tv-paths  [ ...]
                        The paths to the directories containing your tv series
                        files.

global options:
  -l LN, --language LN  Where LN is a language code from ISO 639-1. Common
                        codes include en/de/nl/es/it/fr/pl. TVDB languages are
                        more restrictive.
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

tv scraping options:
  -g, --choose-cover    Choose which cover to use.

informational arguments:
  -V, --version         show program's version number and exit
  -h, --help

</pre>
