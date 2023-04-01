
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import os
import sys


## Normalizes & joins path names.
#
#  @param paths
#    Path names to normalize.
#  @return
#    Formatted string
def join(*paths):
  path = ""
  for p in paths:
    if path:
      path += os.sep
    path += p
  return os.path.normpath(path)

## Retrieves root directory for current system.
#
#  @return
#    System root node string.
def getSystemRoot():
  sys_root = "/"
  if sys.platform == "win32":
    sys_root = os.getenv("SystemDrive") or "C:"
    sys_root += "\\"
  return sys_root

## Checks if a file is marked as executable for the current user.
#
#  @param filepath
#    Path to file to check.
#  @return
#    True if current user can execute file.
def __isExecutable(filepath):
  if not os.path.exists(filepath) or os.path.isdir(filepath):
    return False
  if sys.platform == "win32":
    return True
  return os.access(filepath, os.X_OK)

## Retrieves an executable from PATH environment variable.
#
#  @param cmd
#    Command basename.
#  @return
#    String path to executable or None if file not found.
def getExecutable(cmd):
  path = os.get_exec_path()
  path_ext = os.getenv("PATHEXT") or []
  if type(path_ext) == str:
    path_ext = path_ext.split(";") if sys.platform == "win32" else path_ext.split(":")

  for _dir in path:
    filepath = os.path.join(_dir, cmd)
    if __isExecutable(filepath):
      return filepath
    for ext in path_ext:
      filepath = filepath + "." + ext
      if __isExecutable(filepath):
        return filepath
  return None

## Checks if an executable is available from PATH environment variable.
#
#  @param cmd
#    Command basename.
#  @return
#    True if file found.
def commandExists(cmd):
  return getExecutable(cmd) != None
