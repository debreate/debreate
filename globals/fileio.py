## \package globals.fileio
#
#  File I/O operations

# MIT licensing
# See: docs/LICENSE.txt


import codecs, os

from globals.strings import GS
from libdbr.logger   import Logger


logger = Logger(__name__)


## Retrieves a list of all files from the given path
#
#  \param path
#  Directory to search for license templates
#  \param flag
#  Filter files with given permission flags
def GetFiles(path, flag=None):
  logger.deprecated(__name__, GetFiles.__name__, "os.listdir")

  file_list = []

  for PATH, DIRS, FILES in os.walk(path):
    for F in FILES:
      file_path = os.path.join(path, F)

      if os.path.isfile(file_path):
        # Don't add files that do not match 'flag' attributes
        if flag:
          if not os.access(file_path, flag):
            continue

        file_list.append(F)

  return sorted(file_list, key=GS.lower)


## Retrieve's a file's timestamp
#
#  \param path
#  Absolute path of file to read
#  \return
#  \b \e Float formatted timestamp
def GetTimestamp(path):
  logger.deprecated(__name__, GetTimestamp.__name__, "libdbr.fileio.checkTimestamp")

  return os.stat(path).st_mtime


## Checks if a file has been modified via timestamp
#
#  \param path
#  Absolute path of file to read
#  \param prevStamp
#  The previously saved timestamp
#  \return
#  \b \e True if timestamps are not the same
def TimestampChanged(path, prevStamp):
  logger.deprecated(__name__, TimestampChanged.__name__, "libdbr.fileio.checkTimestamp")

  return GetTimestamp(path) != prevStamp
