
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Executable commands available from the system.
#
#  @module globals.execute

import errno
import os
import subprocess

from subprocess import PIPE
from subprocess import STDOUT

import libdbr.bin

from dbr.language  import GT
from libdbr        import paths
from libdbr.logger import Logger
from wiz.helper    import GetMainWindow


__logger = Logger(__name__)

## Executes a command with elevated privileges.
#
#  @param cmd
#    File to be executed.
#  @param args
#    Arguments to pass to command.
#  @return
#    Program exit code & command output.
def elevated(cmd, *args, pword, check=False):
  if not pword.strip():
    return 1, GT("Empty password")
  sudo = paths.getExecutable("sudo")
  if not sudo:
    return errno.ENOENT, GT("Super user command (sudo) not available")
  main_window = GetMainWindow()
  # disable input to main window while processing
  main_window.Enable(False)
  cmd_line = "echo {} | {}".format(pword, " ".join(["sudo -S", cmd] + args))
  # FIXME: should this be done with subprocess module?
  res = os.popen(cmd_line).read()
  main_window.Enable(True)
  return 0, res

## @deprecated
#    Use `globals.elevated`.
def ExecuteCommand(cmd, args=[], elevate=False, pword=""):
  __logger.deprecated(__name__, ExecuteCommand.__name__, "globals.elevated")

  if elevate and pword.strip(" \t\n") == "":
    return (None, GT("Empty password"))

  CMD_sudo = paths.getExecutable("sudo")

  if not CMD_sudo:
    return (None, GT("Super user command (sudo) not available"))

  main_window = GetMainWindow()

  if isinstance(args, str):
    cmd_line = [args,]

  else:
    cmd_line = list(args)

  cmd_line.insert(0, cmd)

  main_window.Enable(False)

  # FIXME: Better way to execute commands
  if elevate:
    cmd_line.insert(0, "sudo")
    cmd_line.insert(1, "-S")

    cmd_line = " ".join(cmd_line)

    cmd_output = os.popen("echo {} | {}".format(pword, cmd_line)).read()

  else:
    cmd_output = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
    cmd_output.wait()

  main_window.Enable(True)

  stdout = ""

  if isinstance(cmd_output, subprocess.Popen):
    if cmd_output.stdout:
      stdout = cmd_output.stdout

    if cmd_output.stderr:
      if stdout == "":
        stdout = cmd_output.stderr

      else:
        stdout = "{}\n{}".format(stdout, cmd_output.stderr)

    returncode = cmd_output.returncode

  else:
    stdout = cmd_output
    returncode = 0

  return (returncode, stdout)


## @todo Doxygen
def GetCommandOutput(cmd, args=[]):
  __logger.deprecated(__name__, GetCommandOutput.__name__, "libdbr.bin.execute")

  code, output = libdbr.bin.execute(cmd, args)
  return output


## @todo Doxygen
def GetSystemInstaller():
  system_installer = paths.getExecutable("gdebi-gtk")

  if not system_installer:
    system_installer = paths.getExecutable("gdebi-kde")

  return system_installer
