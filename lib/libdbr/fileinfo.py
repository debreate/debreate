
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import mimetypes
import os
import re
import sys

from libdbr     import paths
from libdbr.bin import execute


__default = "application/octet-stream"

## Retrieve MimeType info for file.
#
#  @param filepath
#    Path to file.
#  @return
#    MimeType ID string.
def getMimeType(filepath):
  f_info = None

  cmd_file = paths.getExecutable("file")
  f_exists = os.path.isfile(filepath)
  if f_exists and cmd_file:
    code, output = execute(cmd_file, "--mime-type", "--brief", filepath)
    f_info = output

  if not f_info:
    # fallback to checking by file extension
    f_info = mimetypes.guess_type(filepath)[0]
    if not f_info and f_exists:
      f_info = __default

  return f_info


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
