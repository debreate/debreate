
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import os, sys

def _isExecutable(filepath):
  if not os.path.exists(filepath) or os.path.isdir(filepath):
    return False
  if sys.platform == "win32":
    return True
  return os.access(filepath, os.X_OK)

def getExecutable(cmd):
  path = os.get_exec_path()
  path_ext = os.getenv("PATHEXT") or []
  if type(path_ext) == str:
    path_ext = path_ext.split(";") if sys.platform == "win32" else path_ext.split(":")

  for _dir in path:
    filepath = os.path.join(_dir, cmd)
    if _isExecutable(filepath):
      return filepath
    for ext in path_ext:
      filepath = filepath + "." + ext
      if _isExecutable(filepath):
        return filepath
  return None
