
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.functions
#
#  Global functions used throughout Debreate

import os
import re
import traceback
import subprocess

from urllib.error   import URLError
from urllib.request import urlopen

import wx

import libdbr.bin

from dbr.language       import GT
from globals.errorcodes import dbrerrno
from globals.strings    import IsString
from globals.strings    import StringIsNumeric
from globals.system     import PY_VER_STRING
from libdbr             import paths
from libdbr             import strings
from libdbr.logger      import Logger
from libdebreate        import appinfo


__logger = Logger(__name__)

## Get the current version of the application.
#
#  @param remote
#    Website URL to parse for update.
#  @return
#    Application's version tuple.
def GetCurrentVersion(remote=appinfo.getProjectPages()[0]):
  try:
    version = os.path.basename(urlopen("{}/releases/latest".format(remote)).geturl())

    if "-" in version:
      version = version.split("-")[0]
    version = version.split(".")

    cutoff_index = 0
    for C in version[0]:
      if not C.isdigit():
        cutoff_index += 1
        continue

      break

    version[0] = version[0][cutoff_index:]
    for V in version:
      if not V.isdigit():
        return "Cannot parse release: {}".format(tuple(version))

      version[version.index(V)] = int(V)

    return tuple(version)

  except URLError as err:
    return err


## TODO: Doxygen
def GetContainerItemCount(container):
  if wx.MAJOR_VERSION > 2:
    return container.GetItemCount()

  return len(container.GetChildren())


## TODO: Doxygen
def GetLongestLine(lines):
  if isinstance(lines, str):
    lines = lines.split("\n")

  longest = 0

  for LI in lines:
    l_length = len(LI)
    if l_length > longest:
      longest = l_length

  return longest


## Checks if the system is using a specific version of Python.
#
#  @fixme
#    This function is currently not used anywhere in the code.
#  @param version
#    The minimal version that should be required.
#  @deprecated
def RequirePython(version):
  __logger.deprecated(RequirePython)

  error = "Incompatible python version"
  t = type(version)
  if t == type(""):
    if version == PY_VER_STRING[0:3]:
      return

    raise ValueError(error)

  elif t == type([]) or t == type(()):
    if PY_VER_STRING[0:3] in version:
      return

    raise ValueError(error)

  raise ValueError("Wrong type for argument 1 of RequirePython(version)")


## Checks if a string contains any alphabetic characters.
#
#  @param value
#    \b \e str : String to check.
#  @return
#    \b \e bool : Alphabet characters found.
#  @deprecated
#    Use `libdbr.strings.hasAlpha`.
def HasAlpha(value):
  __logger.deprecated(HasAlpha, alt=strings.hasAlpha)

  # ~ return (re.search("[a-zA-Z]", strings.toString(value)) != None)
  return strings.hasAlpha(value)


## Finds integer value from a string, float, tuple, or list.
#
#  @param value
#    Value to be checked for integer equivalent.
#  @return
#    `int` or `None`.
def GetInteger(value):
  if isinstance(value, (int, float,)):
    return int(value)

  # Will always use the very first value, even for nested items
  elif isinstance(value,(tuple, list,)):
    # Recursive check lists & tuples
    return GetInteger(value[0])

  elif value and IsString(value):
    # Convert because of unsupported methods in str class
    value = strings.toString(value)

    if HasAlpha(value):
      return None

    # Check for negative
    if value[0] == "-":
      if value.count("-") <= 1:
        i_value = GetInteger(value[1:])

        if type(i_value) == int:
          return -int(i_value)

    # Check for tuple
    elif "." in value:
      value = value.split(".")[0]
      return GetInteger(value)

    elif StringIsNumeric(value):
      return int(value)

  return None


## Finds a boolean value from a string, integer, float, or boolean.
#
#  @param value
#    Value to be checked for boolean equivalent.
#  @return
#    `bool` or `None`.
def GetBoolean(value):
  v_type = type(value)

  if v_type == bool:
    return value

  elif v_type in (int, float):
    return bool(value)

  elif v_type == str:
    int_value = GetInteger(value)
    if int_value != None:
      return bool(int_value)

    if value in ("True", "False"):
      return value == "True"

  return None


## Finds a tuple value from a string, tuple, or list.
#
#  @param value
#    Value to be checked for tuple equivalent.
#  @return
#   `tuple` or `None`.
def GetIntTuple(value):
  if isinstance(value, (tuple, list,)):
    if len(value) > 1:
      # Convert to list in case we need to make changes
      value = list(value)

      for I in value:
        t_index = value.index(I)

        if isinstance(I, (tuple, list)):
          I = GetIntTuple(I)

        else:
          I = GetInteger(I)

        if I == None:
          return None

        value[t_index] = I

      return tuple(value)

  elif IsString(value):
    # Remove whitespace & braces
    value = value.strip(" ()")
    value = "".join(value.split(" "))

    value = value.split(",")

    if len(value) > 1:
      for S in value:
        v_index = value.index(S)

        S = GetInteger(S)

        if S == None:
          return None

        value[v_index] = S

      # Convert return value from list to tuple
      return tuple(value)

  return None


## Checks if a value is an integer.
#
#  @param value
#    Value to be checked.
#  @return
#    `True` if value represents an integer.
def IsInteger(value):
  return GetInteger(value) != None


## Checks if a value is a boolean.
#
#  @param value
#    Value to be checked.
#  @return
#    `True` if value represents a boolean.
def IsBoolean(value):
  return GetBoolean(value) != None


## Checks if a value is an integer tuple.
#
#  @param value
#    Value to be checked.
#  @return
#    `True` if value represents an integer tuple.
def IsIntTuple(value):
  return GetIntTuple(value) != None


## Checks if file is binary & needs stripped.
#
#  @param file_name
#    Path to file.
#  @todo
#    FIXME: not platform independent
def fileUnstripped(file_name):
  CMD_file = paths.getExecutable("file")
  if not CMD_file:
    __logger.error("'file' executable not found, cannot check if file '{}' is stripped".format(file_name))
    return False
  err, output = libdbr.bin.execute(CMD_file, file_name)
  if err != 0:
    __logger.error("'file' command returned error '{}'".format(err))
    return False
  return "not stripped" == output.split(", ")[-1]


## Builds a .deb package from a pre-formatted directory tree.
#
#  @param root_dir
#    Directory containing files & meta data for package.
#  @param filename
#    Filename for constructed package.
#  @deprecated
#    Dead code. Use `BuildDebPackage`.
def BuildBinaryPackageFromTree(root_dir, filename):
  __logger.deprecated(BuildBinaryPackageFromTree, alt=BuildDebPackage)

  if not os.path.isdir(root_dir):
    return dbrerrno.ENOENT

  # DEBUG
  cmd = "fakeroot dpkg-deb -v -b \"{}\" \"{}\"".format(root_dir, filename)
  print("DEBUG: Issuing command: {}".format(cmd))

  #res = subprocess.run([cmd])
  #output = (res.returncode, res.stdout)

  return 0


## Checks if this is a development version.
#
#  @return
#    `True` if development version integer is not 0.
def UsingDevelopmentVersion():
  return appinfo.getVersionDev() != 0


## Builds a .deb package from a pre-formatted directory tree.
#
#  @param stage_dir
#    Directory containing files & meta data for package.
#  @param target_file
#    Filename for constructed package.
def BuildDebPackage(stage_dir, target_file):
  packager = paths.getExecutable("dpkg-deb")
  fakeroot = paths.getExecutable("fakeroot")

  if not fakeroot or not packager:
    return (dbrerrno.ENOENT, GT("Cannot run \"fakeroot dpkg\""))

  packager = os.path.basename(packager)

  try:
    output = subprocess.check_output([fakeroot, packager, "-b", stage_dir, target_file], stderr=subprocess.STDOUT)

  except:
    return (dbrerrno.EAGAIN, traceback.format_exc())

  return (dbrerrno.SUCCESS, output)


## Check if mouse is within the rectangle area of a window.
#
#  @param window
#    `wx.Window` instance.
#  @return
#    `True` if mouse positions is within `window` rectangle.
def MouseInsideWindow(window):
  # Only need to find size because ScreenToClient method gets mouse pos
  # relative to window.
  win_size = window.GetSize().Get()
  mouse_pos = window.ScreenToClient(wx.GetMousePosition())

  # Subtracting from width & height compensates for visual boundaries
  inside_x = 0 <= mouse_pos[0] <= win_size[0]-4
  inside_y = 0 <= mouse_pos[1] <= win_size[1]-3

  return inside_x and inside_y
