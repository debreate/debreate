
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.application

import os.path

from globals.paths import getBitmapsDir
from libdbr        import fileio
from libdbr        import paths


__cache = {}

## Checks if app is running portably.
#
#  @return
#    True if not installed.
def isPortable():
  # ~ return os.path.isfile(paths.join(paths.getAppDir(), "portable"))
  return not os.path.isfile(paths.join(paths.getAppDir(), "INSTALLED"))

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
  if isPortable():
    return paths.join(getInstallPrefix(), "locale")
  return paths.join(getInstallPrefix(), "share/locale")


# *** Application information *** #
## Debreate's main homepage
APP_homepage = "https://debreate.github.io/"

## The old SF homepage
APP_homepage_sf = "http://debreate.sourceforge.net/"

## GitHub project page
APP_project_gh = "https://github.com/debreate/debreate"

## GitLab project page
APP_project_gl = "https://gitlab.com/AntumDeluge/debreate"

## SourceForge project page
APP_project_sf = "https://sourceforge.net/projects/debreate"

## Name of application
APP_name = "Debreate"


# *** Version information *** #

VERSION_maj = 0
VERSION_min = 8
VERSION_rev = 0
VERSION_tuple = [VERSION_maj, VERSION_min]
VERSION_string = "{}.{}".format(VERSION_maj, VERSION_min)
if VERSION_rev > 0:
    VERSION_tuple.append(VERSION_rev)
    VERSION_string += ".{}".format(VERSION_rev)
VERSION_tuple = tuple(VERSION_tuple)

# Development version: Increment for every development release
VERSION_dev = 6
if VERSION_dev:
  VERSION_string = "{}-dev{}".format(VERSION_string, VERSION_dev)


# *** Author information *** #

## Author's email
AUTHOR_email = "antumdeluge@gmail.com"

## Application's author
AUTHOR_name = "Jordan Irwin"
