heWiki Replace bot is a python script for site wide replacements in Hebrew Wikipedia. 

See:
https://he.wikipedia.org/wiki/ויקיפדיה:בוט/בוט_החלפות

The script is based on pywikibot core.

Install
=======
* install pywikipedia. 
   see: http://www.mediawiki.org/wiki/Manual:Pywikipediabot/Installation
   important: be sure core and scripts directory in pywikibot are in your PYTHONPATH
* Download the latest database dump:
   http://dumps.wikimedia.org/hewiki/
   ( hewiki-YYYYMMDD-pages-articles.xml )

Use
=======
python hewikiReplacebot -xml:DUMPNAME

License
=======
Distributed under the terms of the MIT license.

