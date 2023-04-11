
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import mimetypes
import os
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
