
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## File & directory information.
#
#  @module libdbr.fileinfo

import mimetypes
import os
import re
import subprocess
import sys

from . import paths


__default = "application/octet-stream"
__directory = "inode/directory"

__mimecmd = []

## Parses command used for checking file type.
def __check_cmd():
  if len(__mimecmd) > 0:
    return
  cmd = paths.getExecutable("file")
  if cmd:
    __mimecmd.append(cmd)
    __mimecmd.append("--mime-type")
    __mimecmd.append("--brief")
    return
  # NOTE: 'mimetype' command is much slower
  cmd = paths.getExecutable("mimetype")
  if cmd:
    __mimecmd.append(cmd)
    __mimecmd.append("--brief")

## Retrieve MimeType info for file.
#
#  @param filepath
#    Path to file.
#  @return
#    MimeType ID string.
def getMimeType(filepath):
  if os.path.isdir(filepath):
    return __directory

  f_info = None
  __check_cmd()

  f_exists = os.path.isfile(filepath)
  if f_exists and __mimecmd:
    res = subprocess.run(__mimecmd + [filepath], stdout=subprocess.PIPE)
    f_info = res.stdout.decode("utf-8").strip() if res.stdout else None

  if not f_info:
    # fallback to checking by file extension
    f_info = mimetypes.guess_type(filepath)[0]
    if not f_info and f_exists:
      f_info = __default

  return f_info or "unknown"


## Checks if a file is marked as executable for the current user.
#
#  @param filepath
#    Path to file to check.
#  @return
#    True if current user can execute file.
def isExecutable(filepath):
  if not os.path.exists(filepath) or os.path.isdir(filepath):
    return False
  # FIXME: how to check for executable status on win32
  if sys.platform == "win32":
    return True
  return os.access(filepath, os.X_OK)

## Retrieves a list of files under a directory.
#
#  @param _dir
#    Directory to search.
#  @param recursive
#    Include sub-directories.
#  @param absolute
#    Return absolute paths.
#  @param include
#    Pattern to include files.
#  @param exclude
#    Pattern to exclude files.
def getFileList(_dir, recursive=True, absolute=True, include="", exclude=""):
  file_list = []
  if os.path.isfile(_dir):
    file_list.append(_dir)
  elif os.path.isdir(_dir):
    if recursive:
      for ROOT, DIRS, FILES in os.walk(_dir):
        for f in FILES:
          if re.match(include, f) and not (re.match(exclude, f) if exclude else False):
            if absolute:
              f = paths.join(ROOT, f)
            file_list.append(f)
    else:
      for obj in os.listdir(_dir):
        abspath = paths.join(_dir, obj)
        if os.path.isdir(abspath):
          continue
        if re.match(include, obj) and not (re.match(exclude, obj) if exclude else False):
          if absolute:
            file_list.append(abspath)
          else:
            file_list.append(obj)
  return file_list


## Timestamps cache.
__timestamps = {}

## Checks a files timestamp information.
#
#  @param filepath
#    Path to file to be checked.
#  @return
#    Timestamp string & flag denoting change from a previous timestamp.
def checkTimestamp(filepath):
  changed = False
  ts = os.stat(filepath).st_mtime
  if filepath in __timestamps:
    changed = ts != __timestamps[filepath]
  __timestamps[filepath] = ts
  return ts, changed
