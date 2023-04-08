
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import os
import sys

from libdbr import fileinfo
from libdbr import sysinfo
from libdbr import userinfo


__cache = {}

## Normalizes path strings.
#
#  @param path
#    String to be normalized.
#  @return
#    Path with system dependent prefix & node delimiters.
def normalize(path):
  if sys.platform == "win32" and path.startswith(os.sep):
    path = os.path.join(getSystemRoot(), path.lstrip(os.sep))
  return os.path.normpath(path)

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
    if type(p) in (list, tuple):
      # ensure list is mutable
      p = list(p)
      while len(p) > 0:
        path = join(path, p.pop(0))
    else:
      path += p
  return normalize(path)

## Retrieves executed script.
#
#  @return
#    Absolute path to script filename.
def getAppPath():
  return os.path.realpath(sys.argv[0])

## Retrieves directory of executed script.
#
#  @return
#    Absolute path to script parent directory.
def getAppDir():
  return os.path.dirname(getAppPath())

## Retrieves current user's home directory.
#
#  @return
#    Absolute path to home directory.
def getHomeDir():
  if sysinfo.getOSName() == "win32":
    return os.getenv("USERPROFILE")
  else:
    return os.getenv("HOME")

## Retrieves root directory for current system.
#
#  @return
#    System root node string.
def getSystemRoot():
  # check cache first
  if "sys_root" in __cache:
    return __cache["sys_root"]

  os_name = sysinfo.getOSName()
  __cache["sys_root"] = os.sep
  if os_name == "win32":
    __cache["sys_root"] = os.getenv("SystemDrive", "C:")
    __cache["sys_root"] += "\\"
  elif os_name == "msys":
    msys_prefix = os.path.dirname(os.getenv("MSYSTEM_PREFIX", ""))
    if sysinfo.getCoreName() == "msys":
      msys_prefix = os.path.dirname(msys_prefix)
    if msys_prefix:
      __cache["sys_root"] = msys_prefix + os.sep
  return __cache["sys_root"]

## Retrieves the relative root for a subsystem such as MSYS.
def getSubSystemRoot():
  sys_root = getSystemRoot()
  if sys_root and sysinfo.getOSName() == "msys":
    sys_root = sys_root[len(sys_root)-1:]
  return sys_root

## Retrieves directory to be used for temporary storage.
#
#  @return
#    System or user temporary directory.
def getTempDir():
  # check cache first
  if "dir_temp" in __cache:
    return __cache["dir_temp"]

  tmp = None
  if sysinfo.getOSName() == "win32":
    if userinfo.isAdmin():
      tmp = join(getSystemRoot(), "Windows", "Temp")
    else:
      tmp = os.getenv("TEMP")
      if not tmp:
        tmp = os.getenv("TMP")
  # cache for faster subsequent calls
  __cache["dir_temp"] = tmp or "/tmp"
  return __cache["dir_temp"]

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
    if fileinfo.isExecutable(filepath):
      return filepath
    for ext in path_ext:
      filepath = filepath + "." + ext
      if fileinfo.isExecutable(filepath):
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


__terminals = (
  ("x-terminal-emulator", "-e"),
  ("xterm", "-e"),
  ("qterminal", "-e"),
  ("xfce4-terminal", "-x"),
  ("lxterminal", "-e"),
  ("rxvt", "-e"),
  ("xvt", "-e"),
  # FIXME: app does not launch after successfully installing wxPython with input from gnome-terminal
  ("gnome-terminal", "--"),
  ("mate-terminal", "--")
)

## Attempts to retrieve a usable terminal emulator for the system.
#
#  @return
#    Terminal executable & parameter to execute a sub-command.
def getSystemTerminal():
  if sys.platform == "win32":
    return getExecutable("cmd"), None
  for pair in __terminals:
    texec = getExecutable(pair[0])
    if texec:
      return texec, pair[1]
  return None, None
