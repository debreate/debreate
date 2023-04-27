
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## @module libdebreate.appinfo

import os.path

from libdbr import fileio
from libdbr import paths
from libdbr import strings


__version = (0, 8)
__version_dev = 9
__dbr_standard = (1, 0)

## Retrieves app version.
#
#  @return
#    App version tuple.
def getVersion():
  return __version

## Retreives app development version.
#
#  @return
#    Development version integer.
def getVersionDev():
  return __version_dev

## Retrieves app version.
#
#  @return
#    App version string.
def getVersionString():
  ver = strings.toString(__version, sep=".")
  if __version_dev > 0:
    ver += "-dev{}".format(__version_dev)
  return ver

## Retrieves config version standard.
#
#  @return
#    Config standard tuple.
def getDBRStandard():
  return __dbr_standard


__cache = {
  "name": "Debreate",
  "home": "https://debreate.github.io/",
  "projects": (
    "https://github.com/debreate/debreate",
    "https://gitlab.com/AntumDeluge/debreate",
    "https://sourceforge.net/projects/debreate"
  ),
  "author": "Jordan Irwin",
  "email": "antumdeluge@gmail.com"
}

## Checks if app is running portably.
#
#  @return
#    True if not installed.
def isPortable():
  if "portable" in __cache:
    return __cache["portable"]

  # ~ __cache["portable"] = os.path.isfile(paths.join(paths.getAppDir(), "portable"))
  __cache["portable"] = not os.path.isfile(paths.join(paths.getAppDir(), "INSTALLED"))
  return __cache["portable"]

## Retrievies app installation prefix.
#
#  @return
#    Absolute path of installation directory prefix.
def getInstallPrefix():
  if "install_prefix" in __cache:
    return __cache["install_prefix"]

  if isPortable():
    return paths.getAppDir()
  prefix = ""
  install_file = paths.join(paths.getAppDir(), "INSTALLED")
  if os.path.isfile(install_file):
    # FIXME: use libdbr.config when it supports multiple config files
    for li in fileio.readFile(install_file).split("\n"):
      if "=" in li:
        tmp = li.split("=")
        key = tmp[0].strip().lower()
        value = tmp[1].strip()
        if key== "prefix":
          prefix = value
          break
  __cache["install_prefix"] = prefix
  return __cache["install_prefix"]

## Retrieves location where locale files are stored.
#
#  @return
#    Absolute path to locale directory prefix.
def getLocaleDir():
  if "dir_locale" in __cache:
    return __cache["dir_locale"]

  if isPortable():
    __cache["dir_locale"] = paths.join(getInstallPrefix(), "locale")
  else:
    __cache["dir_locale"] = paths.join(getInstallPrefix(), "share/locale")
  return __cache["dir_locale"]

## Retrieves application name.
def getName():
  return __cache["name"]

## Retrieves application homepage URL.
def getHomePage():
  return __cache["home"]

## Retrieves project pages.
def getProjectPages():
  return __cache["projects"]

## Retrieves author name.
def getAuthor():
  return __cache["author"]

## Retrieves author email.
def getEmail():
  return __cache["email"]
