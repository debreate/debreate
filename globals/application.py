
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.application

from libdbr.logger import Logger
from libdebreate   import appinfo


__logger = Logger(__name__)
__logger.deprecated(__name__, alt=appinfo)

## Checks if app is running portably.
#
#  @return
#    True if not installed.
def isPortable():
  __logger.deprecated(isPortable, alt=appinfo.isPortable)

  return appinfo.isPortable()

## Retrievies app installation prefix.
#
#  @return
#    Absolute path of installation directory prefix.
def getInstallPrefix():
  __logger.deprecated(getInstallPrefix, alt=appinfo.getInstallPrefix)

  return appinfo.getInstallPrefix()

## Retrieves location where locale files are stored.
#
#  @return
#    Absolute path to locale directory prefix.
def getLocaleDir():
  __logger.deprecated(getLocaleDir, alt=appinfo.getLocaleDir)

  return appinfo.getLocaleDir()


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

VERSION_tuple = appinfo.getVersion()
VERSION_dev = appinfo.getVersionDev()
VERSION_string = appinfo.getVersionString()


# *** Author information *** #

## Author's email
AUTHOR_email = "antumdeluge@gmail.com"

## Application's author
AUTHOR_name = "Jordan Irwin"
