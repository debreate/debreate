# -*- coding: utf-8 -*-

## \package dbr.language

# MIT licensing
# See: docs/LICENSE.txt


import os, gettext

from globals.strings import GS


TRANSLATION_DOMAIN = u'debreate'
LOCALE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), u'locale')

gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR, unicode=True)


## Ensure gettext 
#  
#  This is a workaround for Python 2
#  \param str_value
#    \b \e unicode|str : String to be converted to unicode & translated
def GT(str_value):
    return _(GS(str_value))
