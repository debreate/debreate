
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Command execution functions.
#
#  @module libdbr.bin

import errno
import os.path
import subprocess
import sys

from . import paths


## Creates a uniform agument list.
#
#  @param args
#    List of arguments.
#  @return
#    List of strings.
def __parseArgsList(args):
  args_list = []
  for a in args:
    a_type = type(a)
    if a_type in (list, tuple):
      args_list += __parseArgsList(a)
    elif a_type == str:
      args_list.append(a)
    else:
      raise TypeError("incompatible argument type passed to {} ({})"
          .format(__name__ + "." + execute.__name__, a_type))
  return args_list

## Executes a command.
#
#  @param cmd
#    File to be executed.
#  @param args
#    Arguments to pass to command.
#  @param check
#    Throw an error if command returned non-zero.
#  @param usestderr
#    Use output of stderr if stdout is empty.
#  @return
#    Program exit code & output.
def execute(cmd, *args, check=False, usestderr=False):
  res = subprocess.run([cmd] + __parseArgsList(args), check=check, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
  output = res.stdout
  if not output and usestderr:
    output = res.stderr
  if output != None:
    output = output.decode("utf-8").rstrip()
  return res.returncode, output


__cmd_trash = []

## Send a file to the trash/recycle bin.
#
#  @param files
#    File(s) to be moved.
#  @return
#    `True` if ___files___ no longer exist.
#  @todo
#    - Implement for win32.
#    - See: https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-itransfersource-recycleitem
def trash(files):
  if not __cmd_trash:
    if sys.platform == "win32":
      # TODO:
      print("WARNING: sending files to recycle bin not implemented yet on Windows")
    else:
      __cmd_trash.append(paths.getExecutable("gio"))
      __cmd_trash.append("trash")
  if __cmd_trash:
    execute(__cmd_trash[0], __cmd_trash[1:], files)
  if type(files) == str:
    return 0 if not os.path.lexists(files) else errno.EEXIST
  for f in files:
    if os.path.lexists(f):
      return errno.EEXIST
  return 0
