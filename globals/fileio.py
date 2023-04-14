
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.fileio
#
#  File I/O operations

import codecs
import os

from libdbr          import fileinfo
from libdbr.logger   import Logger


__logger = Logger(__name__)


## Retrieves a list of all files from the given path.
#
#  @param path
#    Directory to search for license templates.
#  @param flag
#    Filter files with given permission flags.
#  @return
#    List of files found under `path`.
#  @deprecated
#    Use `libdbr.fileinfo.getFileList`.
def GetFiles(path, flag=None):
  __logger.deprecated(GetFiles, alt=fileinfo.getFileList)

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

  return sorted(file_list, key=str.lower)


## Retrieve's a file's timestamp.
#
#  @param path
#    Absolute path of file to read.
#  @return
#    Float formatted timestamp.
#  @deprecated
#    Use `libdbr.fileinfo.checkTimestamp`.
def GetTimestamp(path):
  __logger.deprecated(GetTimestamp, alt=fileinfo.checkTimestamp)

  return os.stat(path).st_mtime


## Checks if a file has been modified via timestamp.
#
#  @param path
#    Absolute path of file to read
#  @param prevStamp
#    The previously saved timestamp
#  @return
#    `True` if timestamps are not the same.
#  @deprecated
#    Use `libdbr.fileinfo.checkTimestamp`.
def TimestampChanged(path, prevStamp):
  __logger.deprecated(TimestampChanged, alt=fileinfo.checkTimestamp)

  return GetTimestamp(path) != prevStamp
