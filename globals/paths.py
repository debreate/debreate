## \package globals.paths
#
#  Global paths used in the app

# MIT licensing
# See: docs/LICENSE.txt


import os, sys

from globals.strings import GS
from globals.strings import IsString


def getSystemRoot():
  sys_root = "/"
  if sys.platform == "win32":
    sys_root = os.getenv("SystemDrive") or "C:"
    sys_root += "\\"
  return sys_root

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
