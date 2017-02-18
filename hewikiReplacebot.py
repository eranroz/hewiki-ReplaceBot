#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
ReplaceRobotHe is extension of ReplaceRobot.
It is used in Hebrew Wikipedia for doing common replacements according to defintions in a wiki page

These command line parameters can be used to specify which pages to work on:

&params;

-xml              Retrieve information from a local XML dump (pages-articles
                  or pages-meta-current, see http://download.wikimedia.org).
                  Argument can also be given as "-xml:filename".
-summary:XYZ      Set the summary message text for the edit to XYZ, bypassing
                  the predefined message texts with original and replacements
                  inserted.
-xmlstart         (Only works with -xml) Skip all articles in the XML dump
                  before the one specified (may also be given as
                  -xmlstart:Article).
-titlecheck       A page name to list all pages which their titles violates replacement rules.
                The bot will avoid replacements which change titles of existing pages.
"""
#
# (C) Eran Roz
# Distributed under the terms of the MIT license.
#
import re
from collections import OrderedDict

import pywikibot
from pywikibot import i18n
import pywikibot.pagegenerators

try:
    import replace
except ImportError:
    # usually both scripts directory and pywikibot core should be in PYTHONPATH but if not
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(pywikibot.__file__, os.pardir, os.pardir, 'scripts')))
    import scripts.replace as replace

import replaceConfig

NO_BOT_REGEX = re.compile(replaceConfig.nobotRgx)


class XmlDumpReplacePageGeneratorHe(replace.XmlDumpReplacePageGenerator):
    def __init__(self, replace_dict, xml_filename, xml_start, exceptions, site):
        self.replace_dict = replace_dict
        replace.XmlDumpReplacePageGenerator.__init__(self, xml_filename, xml_start, replace_dict.values(),
                                                     exceptions, site)

    def isTextExcepted(self, text):
        """
        This is some hack. changing the replacements HERE,
        assuming this check is called before replacement for each page
        """
        self.replacements = list(getReplacements(self.replace_dict, text))
        return super(XmlDumpReplacePageGeneratorHe, self).isTextExcepted(text)


class HeWikiReplacement(replace.Replacement):
    def __init__(self, old, new, exceptions=None):
        super(HeWikiReplacement, self).__init__(old, new, use_regex=True, exceptions=exceptions)


class ReplaceRobotHe(replace.ReplaceRobot):
    """ Robot for common replacement in Hebrew Wikipedia according to known replace page """

    def __init__(self, gen, replace_dict, exceptions, edit_summary):
        self.replaceDict = replace_dict  # replacement dictionary
        self.summaryPrefix = edit_summary
        replace.ReplaceRobot.__init__(self, gen, self.replaceDict.values(), exceptions, always=True)

    """ override regular do replacements by removing disabled replacements according to template,
        than the  method is the same as the super, but is with specifying specific summary """
    def apply_replacements(self, original_text, applied, page=None):
        """
        Returns the text which is generated by applying all replacements to
        the given text.
        """

        self.replacements = list(getReplacements(self.replaceDict, original_text))
        return super(ReplaceRobotHe, self).apply_replacements(original_text, applied, page)

    def generate_summary(self, applied_replacements):
        actucal_replacements = [rep.new.strip() for rep in applied_replacements]
        return self.summaryPrefix + ', '.join(actucal_replacements)


def getReplacements(replace_dict, text):
    """
    filters disabled replacements from dictionary
    """
    disabled = NO_BOT_REGEX.findall(text)
    for repId, repRgx in replace_dict.items():
        if repId not in disabled:
            yield repRgx


def fillReplementsDict():
    """
    fills replacement dictionary according to replace page
    """
    site = pywikibot.getSite()
    page = pywikibot.Page(site, replaceConfig.replacementsPage)
    text = page.get()
    replaceDict = dict()
    if page.lastNonBotUser() not in replaceConfig.whitelist_editors:
        raise Exception('Non authorized user edited the replace list. Please verify')

    for x in re.findall(
            "\\|([0-9]+)\n\\|<nowiki>(.*)</nowiki>\n\\|<nowiki>(.*)</nowiki>\n\\|(?:<nowiki>)?(.*?)(?:\n|</nowiki>)",
            text):
        try:
            # compile the regex to check if it is support by python

            if x[3] == '':
                replacement = HeWikiReplacement(x[1], re.sub('\\$([0-9])', '\\\\\\1', x[2]))
            else:
                replacement = HeWikiReplacement(x[1], re.sub('\\$([0-9])', '\\\\\\1', x[2]), {'inside': [x[3]]})
            replacement.compile(use_regex=True, flags=re.UNICODE)
            replaceDict[x[0]] = replacement
        except:
            # some regexs are written for c# and are ignored by this bot
            pywikibot.output('Non supported replacement. ID: %s' % x[0])
            pass
    return replaceDict


def check_titles(site, report_page_name, replacements):
    """
    To avoid breaking links, adds page titles that will be changed to exception list
    :param site: site where the bot will run
    :param report_page_name: a page name to list of titles adds to exception
    :param replacements: dictionary of replacements
    """
    from pywikibot import textlib
    from pywikibot.tools import itergroup
    all_pages = site.allpages(namespace=0, filterredir=False, content=False)
    evaluation_progress = 0
    exceptions_dict = {}
    for titles_group in itergroup(all_pages, all_pages.query_limit):
        titles_group_t = [p.title(asLink=True) for p in titles_group]
        old_titles = titles_group_t
        evaluation_progress += len(titles_group_t)
        if evaluation_progress % 20000 == 0: print('\r%i page titles processed' % evaluation_progress)
        old_text = ' \n '.join(titles_group_t)
        for replacement_key, replacement in replacements.items():
            replacement_exceptions = replacement.exceptions or {}
            replacement_exceptions_inside = replacement_exceptions.get('inside', [])
            new_text = textlib.replaceExcept(
                old_text, replacement.old_regex, replacement.new,
                replacement_exceptions_inside,
                site=site)

            # replacement change valid title
            changed_titles = ((old_title, new_title) for old_title, new_title in zip(old_titles, new_text.split(' \n '))
                              if old_title != new_title and
                              old_title != '[[%s' % pywikibot.tools.first_upper(new_title[2:]))  # breaks link
            # no special treat for link
            changed_titles = ((old_title, new_title) for old_title, new_title in changed_titles
                              if replacement.old_regex.sub(replacement.new, ' %s ' % old_title[2:-2]) != ' %s ' % old_title[2:-2])
            # valid title is not disambig
            changed_titles = [old_title[2:-2] for old_title, new_title in changed_titles
                              if not pywikibot.Page(site, old_title[2:-2]).isDisambig()
                              ]
            if len(changed_titles) > 0:
                replacement_exceptions['inside'] = replacement_exceptions_inside + changed_titles
                replacement.exceptions = replacement_exceptions
                if replacement_key not in exceptions_dict:
                    exceptions_dict[replacement_key] = []
                exceptions_dict[replacement_key] += changed_titles

    exceptions_dict = OrderedDict(sorted((int(k), v) for k, v in exceptions_dict.items()))
    report_page = pywikibot.Page(site, report_page_name)
    exception_report = ''
    for replace_key, replaced_titles in exceptions_dict.items():
        exception_report += '\n* %i\n%s' % (replace_key, '\n'.join(['** [[%s]]' % t for t in replaced_titles]))
    report_page.put(exception_report, summary='עדכון')


def main(*args):
    pywikibot.output('Starting hewiki-replacebot')
    editSummary = replaceConfig.defaultSummary
    xmlFilename = None
    xmlStart = None
    title_check_page = None
    gen = None
    gen_factory = pywikibot.pagegenerators.GeneratorFactory()
    local_args = pywikibot.handle_args(args)
    for arg in local_args:
        if gen_factory.handleArg(arg):
            continue
        elif arg.startswith('-summary:'):
            editSummary = arg[9:]
        elif arg.startswith('-xmlstart'):
            if len(arg) == 9:
                xmlStart = pywikibot.input('Please enter the dumped article to start with:')
            else:
                xmlStart = arg[10:]
        elif arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = i18n.input('pywikibot-enter-xml-filename')
            else:
                xmlFilename = arg[5:]
        elif arg.startswith('-titlecheck'):
            title_check_page = arg[12:]

    replaceDict = fillReplementsDict()

    safe_templates = replaceConfig.safeTemplates
    # add external links templates
    site = pywikibot.Site()
    for safeCategory in replaceConfig.safeTemplatesCategories:
        cite_templates = pywikibot.Category(site, safeCategory).articles(namespaces=10, recurse=True)
        cite_templates = [page.title(withNamespace=False) for page in cite_templates]
        safe_templates += cite_templates

    file_usage_rgx = re.compile(replaceConfig.fileUsageRgx, re.I)
    yiRgx = re.compile('\[\[yi:.*?\]\]')
    safeTemplatesRgx = re.compile('\{\{(' + '|'.join(safe_templates, ) + ').*?\}\}', re.I)
    exceptions = {
        'title': [],
        'text-contains': [re.compile(replaceConfig.redirectRgx, re.I)],
        'inside': [file_usage_rgx, safeTemplatesRgx, yiRgx],
        'inside-tags': ['nowiki', 'math', 'comment', 'pre', 'source', 'hyperlink', 'gallery'],
        'require-title': [],
    }

    # avoid searching in other namespaces in the xml
    exceptions_with_title_ns = dict(exceptions)
    exceptions_with_title_ns['title'] = [re.compile('^' + re.escape(ns_name) + ':') for ns_index, ns
                                         in site.namespaces.items() if ns_index not in replaceConfig.namespaces
                                         for ns_name in ns]
    if title_check_page:
        site.login()
        check_titles(site, title_check_page, replaceDict)
    if xmlFilename:
        gen = XmlDumpReplacePageGeneratorHe(replaceDict, xmlFilename, xmlStart, exceptions_with_title_ns, site)

    gen = gen_factory.getCombinedGenerator(gen)
    if not gen:
        pywikibot.output('no xml dump specified. please fill -xml and the xml file to be used, or other generator')
        pywikibot.bot.suggest_help(missing_generator=True)
        return False

    gen = pywikibot.pagegenerators.NamespaceFilterPageGenerator(gen, replaceConfig.namespaces, site)
    gen = pywikibot.pagegenerators.PreloadingGenerator(gen)
    pywikibot.output('starting replace')
    bot = ReplaceRobotHe(gen, replaceDict, exceptions, editSummary)
    site.login()
    bot.run()
    pywikibot.output('finished all replacements')


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
