
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## System paths handling.
#
#  @module libdbr.paths

import os
import sys
import typing

from . import fileinfo
from . import sysinfo
from . import userinfo


__cache: typing.Dict[str, typing.Any] = {
  "executables": {}
}

## Normalizes path strings.
#
#  @param path
#    String to be normalized.
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Path with system dependent prefix & node delimiters.
def normalize(path, strict=False):
  sep = os.sep
  if strict and sys.platform == "win32":
    sep = "\\"
  # clean up node delimiters
  path = path.replace("/", sep).replace("\\", sep)
  if path.startswith(sep):
    if strict and sys.platform == "win32" and sysinfo.getOSName() != "win32":
      path = getSubSystemRoot() + path.lstrip(sep)
    else:
      path = getSystemRoot() + path.lstrip(sep)
  # ~ return os.path.normpath(path)
  if not path.strip():
    path = "."
  return path.replace("{0}{0}".format(sep), sep)

## Normalizes & joins path names.
#
#  @param paths
#    Path names to normalize.
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Formatted string
def join(*paths, strict=False):
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
  return normalize(path, strict=strict)

## Retrieves executed script.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Absolute path to script filename.
def getAppPath(strict=False):
  if "path_app" in __cache:
    return __cache["path_app"]
  __cache["path_app"] = os.path.realpath(sys.argv[0])
  return __cache["path_app"]

## Retrieves directory of executed script.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Absolute path to script parent directory.
def getAppDir(strict=False):
  if "dir_app" in __cache:
    return __cache["dir_app"]
  dir_app = getAppPath(strict=strict)
  if not os.path.isdir(dir_app):
    dir_app = os.path.dirname(dir_app)
  __cache["dir_app"] = dir_app
  return __cache["dir_app"]

## Retrieves current user's home directory.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Absolute path to home directory.
def getUserHome(strict=False):
  if sysinfo.getOSName() == "win32":
    return os.getenv("USERPROFILE")
  else:
    return normalize(os.getenv("HOME"), strict=strict)

## Retrieves current user's home directory.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Absolute path to home directory.
#  @deprecated
#    Use `libdbr.paths.getUserHome`.
def getHomeDir(strict=False):
  print("WARNING: {} is deprecated, use {} instead" \
      .format(__name__ + "." + getHomeDir.__name__, __name__ + "." + getUserHome.__name__))

  return getUserHome(strict=strict)

## Retrieves user's local data storage directory.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Path to data directory.
def getUserDataRoot(strict=False):
  if sysinfo.getOSName() == "win32":
    return os.getenv("APPDATA")
  return join(getUserHome(), ".local/share", strict=strict)

## Retrieves user's local configuration directory.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    Path to config directory.
def getUserConfigRoot(strict=False):
  if sysinfo.getOSName() == "win32":
    # FIXME: is this correct?
    return os.getenv("APPDATA")
  return join(getUserHome(), ".config", strict=strict)

## Retrieves root directory for current system.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    System root node string.
def getSystemRoot(strict=False):
  # check cache first
  if not strict and "sys_root" in __cache:
    return __cache["sys_root"]

  sep = os.sep
  if strict and sys.platform == "win32":
    sep = "\\"

  os_name = sysinfo.getOSName()
  # ~ __cache["sys_root"] = sep
  sys_root = sep
  if os_name == "win32":
    sys_root = os.getenv("SystemDrive", "C:") + sep
  elif os_name == "msys":
    msys_prefix = os.path.dirname(os.getenv("MSYSTEM_PREFIX", ""))
    if sysinfo.getCoreName() == "msys":
      msys_prefix = os.path.dirname(msys_prefix)
    if msys_prefix:
      sys_root = normalize(msys_prefix, strict=strict) + sep

  # don't cache if using strict
  if not strict:
    __cache["sys_root"] = sys_root

  return sys_root

## Retrieves the relative root for a subsystem such as MSYS.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    SubSystem root node string.
def getSubSystemRoot(strict=False):
  # check cache first
  if not strict and "subsys_root" in __cache:
    return __cache["subsys_root"]

  subsys_root = getSystemRoot(strict=strict)
  if subsys_root and sysinfo.getOSName() == "msys":
    subsys_root = subsys_root[len(subsys_root)-1:]

  # don't cache if using strict
  if not strict:
    __cache["subsys_root"] = subsys_root

  return subsys_root

## Retrieves directory to be used for temporary storage.
#
#  @param strict
#    If `True`, don't use Posix-style paths under MSYS.
#  @return
#    System or user temporary directory.
def getTempDir(strict=False):
  # check cache first
  if not strict and "dir_temp" in __cache:
    return __cache["dir_temp"]

  dir_temp = None
  if sysinfo.getOSName() == "win32":
    if userinfo.isAdmin():
      dir_temp = join(getSystemRoot(strict=strict), "Windows", "Temp")
    else:
      dir_temp = os.getenv("TEMP")
      if not dir_temp:
        dir_temp = os.getenv("TMP")
  # default to Posix temp directory
  dir_temp = dir_temp or "/tmp"

  # don't cache if using strict
  if not strict:
    __cache["dir_temp"] = dir_temp

  return dir_temp

## Retrieves an executable from PATH environment variable.
#
#  @param cmd
#    Command basename.
#  @return
#    String path to executable or None if file not found.
def getExecutable(cmd):
  if cmd in __cache["executables"]:
    return __cache["executables"][cmd]

  path = os.get_exec_path()
  path_ext = os.getenv("PATHEXT") or []
  if type(path_ext) == str:
    path_ext = path_ext.split(";") if sys.platform == "win32" else path_ext.split(":")

  for _dir in path:
    filepath = join(_dir, cmd)
    if fileinfo.isExecutable(filepath):
      __cache["executables"][cmd] = filepath
      return filepath
    for ext in path_ext:
      ext_filepath = filepath + ext
      if fileinfo.isExecutable(ext_filepath):
        __cache["executables"][cmd] = ext_filepath
        return ext_filepath
  return None

## Retrieves a cached executable instead of searching the system.
#
#  @param _id
#    String identifier.
#  @return
#    String path to executable or None if not cached.
def getCachedExecutable(_id):
  if _id in __cache["executables"]:
    return __cache["executables"][_id]
  return None

## Caches executable path.
#
#  Useful for using a custom identifier.
#
#  @param _id
#    String identifier.
#  @param path
#    Path to executable.
def setExecutable(_id, path):
  __cache["executables"][_id] = path

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
