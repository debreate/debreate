
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.paths
#
#  Global paths used in the app

import os, sys

import libdbr.paths

from globals.strings import GS
from globals.strings import IsString
from libdbr.logger   import Logger


logger = Logger(__name__)

# ~ def getAppDir():
  # ~ logger.deprecated(__name__, getAppDir.__name__, "libdbr.paths.getAppDir")

  # ~ ## Directory where app is installed
  # ~ #  HACK: test
  # ~ #  HACK: Call os.path.dirname twice to get root directory.
  # ~ #    This is necessary because this variable is
  # ~ #    declared from a sub-directory.
  # ~ return GS(os.path.dirname(os.path.dirname(__file__)))

def getHomeDir():
  logger.deprecated(__name__, getHomeDir.__name__, "libdbr.paths.getHomeDir")

  # ~ if sys.platform == "win32":
    # ~ return os.getenv("USERPROFILE")
  # ~ else:
    # ~ return os.getenv("HOME")

  return libdbr.paths.getHomeDir()

def getLocalDir():
  return os.path.join(libdbr.paths.getHomeDir(), os.path.normpath(".local/share/debreate"))

def getCacheDir():
  return os.path.join(getLocalDir(), "cache")

def getLogsDir():
  return os.path.join(getLocalDir(), "logs")

def getBitmapsDir():
  return os.path.join(libdbr.paths.getAppDir(), "bitmaps")
