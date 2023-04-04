
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

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
  # FIXME: need platform independent method to get mimetypes
  cmd_file = paths.getExecutable("file")
  if not cmd_file:
    return __default
  code, output = execute(cmd_file, "--mime-type", "--brief", filepath)
  # 'file' command always returns 0
  if not output or "cannot open" in output:
    return __default
  return output


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
