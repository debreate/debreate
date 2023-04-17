
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
#  @todo
#    Move to `libdbr`.
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


## Retrieves a usable GUI .deb installer application.
#
#  @todo
#    Use a list of whitelisted executables
def GetSystemInstaller():
  system_installer = paths.getExecutable("gdebi-gtk")
  if not system_installer:
    system_installer = paths.getExecutable("gdebi-kde")
  return system_installer
