
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.language

import gettext
import os

import libdbr.bin

from libdbr        import paths
from libdbr.logger import Logger
from libdebreate   import appinfo


__logger = Logger(__name__)

__domain = appinfo.getName().lower()
__translator = None
__native_code = "en_US"
__current_code = ""

## Stores locale code.
def __cacheLocale():
  global __current_code
  # set to 'None' to fallback to let gettext try to parse locale if user lookup fails
  __current_code = None
  cmd_locale = paths.getExecutable("locale")
  if cmd_locale:
    # try to parse current user's locale
    err, msg = libdbr.bin.execute(cmd_locale)
    if err == 0:
      for li in msg.split("\n"):
        if len(li) > 5 and li.startswith("LANG="):
          __current_code = li[5:].split(".")[0]
          return
  __logger.debug("defaulting to system locale")

## Retrieves the current locale code.
def getLocale():
  if __current_code == "":
    __cacheLocale()
  return __current_code

## Formats translatable strings.
#
#  @param str_value
#    \b \e str : String to be translated.
#  @fixme
#    Use `str` function as default translator.
def GT(str_value):
  if not __translator:
    return str_value
  return __translator(str_value)


## Retrieves the path of gettext locale translations.
#
#  @deprecated
#    Use `libdebreate.appinfo.getLocaleDir`.
def GetLocaleDir():
  __logger.deprecated(GetLocaleDir, alt=appinfo.getLocaleDir)

  return appinfo.getLocaleDir()


## Sets locale translator.
#
#  @param path
#    Directory to search for gettext locale translations.
def setTranslator(path):
  global __translator
  l_code = getLocale()
  __logger.debug("locale code: {}".format(l_code))
  __logger.debug("locale directory: {}".format(path))
  if l_code != __native_code:
    try:
      __translator = gettext.translation(__domain, path, [l_code]).gettext
    except FileNotFoundError:
      __logger.warn("translation for locale '{}' unavailable".format(l_code))
