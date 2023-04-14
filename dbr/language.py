
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.language

import gettext
import os

from libdbr.logger   import Logger


__logger = Logger(__name__)

TRANSLATION_DOMAIN = "debreate"
DIR_locale = ""

__translator = None


## Ensure gettext
#
#  FIXME: deprecated?
#
#  This is a workaround for Python 2
#  \param str_value
#  \b \e str : String to be translated
def GT(str_value):
  if not __translator:
    return str_value
  return __translator(str_value)


## Retrieves the path of gettext locale translations
def GetLocaleDir():
  __logger.deprecated(__name__, GetLocaleDir.__init__)

  return DIR_locale


## Sets locale translator.
#
#  @param path
#    Directory to search for gettext locale translations.
def setTranslator(path):
  global __translator, DIR_locale
  DIR_locale = path
  try:
    __translator = gettext.translation(TRANSLATION_DOMAIN, path).gettext
  except FileNotFoundError:
    __translator = None

  __logger.debug("locale directory: {}".format(path))
