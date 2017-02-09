# -*- coding: utf-8 -*-

## \package dbr.language

# MIT licensing
# See: docs/LICENSE.txt


import os, gettext

from globals.strings import GS


TRANSLATION_DOMAIN = u'debreate'
DIR_locale = os.path.join(os.path.dirname(os.path.dirname(__file__)), u'locale')

gettext.install(TRANSLATION_DOMAIN, DIR_locale, unicode=True)


## Ensure gettext 
#  
#  This is a workaround for Python 2
#  \param str_value
#    \b \e unicode|str : String to be converted to unicode & translated
def GT(str_value):
    return _(GS(str_value))


## Retrieves the path of gettext locale translations
def GetLocaleDir():
    global DIR_locale
    
    return DIR_locale


## Sets the path for the gettext locale translations
#
#  \param path
#    New directory location
def SetLocaleDir(path):
    global DIR_locale
    
    DIR_locale = path
