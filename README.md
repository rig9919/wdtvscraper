<pre>
wdtvscraper  
===========  
  
usage: scraper.py [-h] [-i] [-t] [-l LN] [-c CN] [-a] [-d] [path]  
  
Scrape themoviedb.org for metadata of movies stored on a WDTV device.  
  
positional arguments:  
  path                  The path to the directory containing your movie files.  
  
optional arguments:  
  -h, --help            show this help message and exit  
  -i, --interactive  
  -t, --thumbnails      Set to include remote thumbnail urls in xml. This may  
                        slow thumbnail loading.  
  -l LN, --language LN  Where LN is a language code from ISO 639-1. Common  
                        codes include en/de/nl/es/it/fr/pl  
  -c CN, --country CN   Where CN is a country code from ISO 3166-1 alpha-2.  
                        Common codes include us/gb/de/nl/it/fr/pl  
  -a, --assume          Assume match on 1 result. Not recommended This can  
                        lead to mismatches.  
  -d, --debug  
  
</pre>
