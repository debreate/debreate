## \package dbr.language

# MIT licensing
# See: docs/LICENSE.txt


import os, gettext

from globals.strings import GS


TRANSLATION_DOMAIN = "debreate"
DIR_locale = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")

gettext.install(TRANSLATION_DOMAIN, DIR_locale)


## Ensure gettext
#
#  FIXME: deprecated?
#
#  This is a workaround for Python 2
#  \param str_value
#  \b \e str : String to be translated
def GT(str_value):
  return gettext.gettext(GS(str_value))


## Retrieves the path of gettext locale translations
def GetLocaleDir():
  global DIR_locale

  return DIR_locale


## Sets the path for the gettext locale translations
#
#  \param path
#  New directory location
def SetLocaleDir(path):
  global DIR_locale

  DIR_locale = path
