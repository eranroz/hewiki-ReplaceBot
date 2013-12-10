heWiki Replace bot is a python script for site wide replacements in Hebrew Wikipedia. 

See:
https://he.wikipedia.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%A4%D7%93%D7%99%D7%94:%D7%91%D7%95%D7%98/%D7%91%D7%95%D7%98_%D7%94%D7%97%D7%9C%D7%A4%D7%95%D7%AA

The script is based on pywikipediabot.

Install
=======
* install pywikipedia. 
   see: http://www.mediawiki.org/wiki/Manual:Pywikipediabot/Installation
* Download the latest database dump:
   http://dumps.wikimedia.org/hewiki/
   ( hewiki-YYYYMMDD-pages-articles.xml )
* place the hewiki-ReplaceBot directory within pywikipedia directory

Use
=======
python hewikiReplacebot -xml:DUMPNAME

License
=======
Distributed under the terms of the MIT license.

