heWiki Replace bot is a python script for site wide replacements in Hebrew Wikipedia. 

See:
https://he.wikipedia.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%A4%D7%93%D7%99%D7%94:%D7%91%D7%95%D7%98/%D7%91%D7%95%D7%98_%D7%94%D7%97%D7%9C%D7%A4%D7%95%D7%AA

The script is based on pywikipediabot.

==Install=
1. install pywikipedia. 
   see: http://www.mediawiki.org/wiki/Manual:Pywikipediabot/Installation
2. Download the latest database dump:
   http://dumps.wikimedia.org/hewiki/
   ( hewiki-YYYYMMDD-pages-articles.xml )
3. place the hewiki-ReplaceBot directory within pywikipedia directory
4. in pywikipedia/pywikibot/text.lib, function replaceExcept, change
                        replacement = replacement[:groupMatch.start()] + \
                                      match.group(groupID) + \
                                      replacement[groupMatch.end():]
   To:
                        replacement = replacement[:groupMatch.start()] + \
									  ('' if match.group(groupID)==None else match.group(groupID)) + \
                                      replacement[groupMatch.end():]

   
   This should allow empty matching groups (eg for /ab(.?)d/ in abd \\1='')

==Use==
python hewikiReplacebot -xml:DUMPNAME

==License==
Distributed under the terms of the MIT license.

