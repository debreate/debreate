## \package globals.paths
#
#  Global paths used in the app

# MIT licensing
# See: docs/LICENSE.txt


import os, sys

from globals.strings import GS
from globals.strings import IsString


def getAppDir():
  ## Directory where app is installed
  #  HACK: test
  #  HACK: Call os.path.dirname twice to get root directory.
  #    This is necessary because this variable is
  #    declared from a sub-directory.
  return GS(os.path.dirname(os.path.dirname(__file__)))

def getHomeDir():
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

## Joints multiple strings into a single path
#
#  \deprecated
#    Just use os.path.join & os.path.normpath
#
#  \param pathList
#  <b><i>List</i></b> of strings to be concatenated
#  \param tail
#  Strings to be concatenated to root argument (pathList)
def ConcatPaths(pathList, *tail):
  # ~ logger.deprecated(__name__, ConcatPaths.__name__, "os.path.join and os.path.normpath")
  print("WARNING: " + __name__ + "." + ConcatPaths.__name__ + " is deprecated, use os.path.join and os.pathnormpath instead")

  # Convert string arg to list
  if IsString(pathList):
    pathList = [pathList,]

  # Make sure we are working with a list instance
  pathList = list(pathList)

  # Append tail arguments
  if tail:
    pathList += tail

  for idx in range(len(pathList)):
    pathList[idx] = os.path.normpath(pathList[idx])

  return os.path.join(*pathList)
