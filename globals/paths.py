
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Global paths used in the app.
#
#  @module globals.paths

import os
import sys

import libdbr.paths

from globals.strings import IsString
from libdbr.logger   import Logger


__logger = Logger(__name__)

# ~ def getAppDir():
  # ~ __logger.deprecated(__name__, getAppDir.__name__, "libdbr.paths.getAppDir")

  # ~ ## Directory where app is installed
  # ~ #  HACK: test
  # ~ #  HACK: Call os.path.dirname twice to get root directory.
  # ~ #    This is necessary because this variable is
  # ~ #    declared from a sub-directory.
  # ~ return os.path.dirname(os.path.dirname(__file__))

## Retrieves user's home directory.
#
#  @return
#    Path to user home.
#  @deprecated
#    Use `libdbr.paths.getHomeDir`.
def getHomeDir():
  __logger.deprecated(getHomeDir, alt=libdbr.paths.getHomeDir)

  # ~ if sys.platform == "win32":
    # ~ return os.getenv("USERPROFILE")
  # ~ else:
    # ~ return os.getenv("HOME")

  return libdbr.paths.getUserHome()

## Retrieves user's local data directory.
def getLocalDir():
  return os.path.join(libdbr.paths.getUserHome(), os.path.normpath(".local/share/debreate"))

## Retrieves user's local cache directory.
def getCacheDir():
  return os.path.join(getLocalDir(), "cache")

## Retrieves Debreate's logs directory.
def getLogsDir():
  return os.path.join(getLocalDir(), "logs")

## Retrieves Debreate's bitmaps directory.
def getBitmapsDir():
  return os.path.join(libdbr.paths.getAppDir(), "bitmaps")
