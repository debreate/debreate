## \package globals.paths
#
#  Global paths used in the app

# MIT licensing
# See: docs/LICENSE.txt


import os, sys

from globals.strings import GS
from globals.strings import IsString
from libdbr.logger   import getLogger


logger = getLogger()

def getAppDir():
  logger.deprecated(__name__, getAppDir.__name__, "libdbr.paths.getAppDir")

  ## Directory where app is installed
  #  HACK: test
  #  HACK: Call os.path.dirname twice to get root directory.
  #    This is necessary because this variable is
  #    declared from a sub-directory.
  return GS(os.path.dirname(os.path.dirname(__file__)))

def getHomeDir():
  logger.deprecated(__name__, getHomeDir.__name__, "libdbr.paths.getHomeDir")

  if sys.platform == "win32":
    return os.getenv("USERPROFILE")
  else:
    return os.getenv("HOME")

def getLocalDir():
  return os.path.join(getHomeDir(), os.path.normpath(".local/share/debreate"))

def getCacheDir():
  return os.path.join(getLocalDir(), "cache")

def getLogsDir():
  return os.path.join(getLocalDir(), "logs")

def getBitmapsDir():
  return os.path.join(getAppDir(), "bitmaps")
