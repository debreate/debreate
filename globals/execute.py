
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
import ui.app

from dbr.language  import GT
from libdbr        import paths


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
  main_window = ui.app.getMainWindow()
  # disable input to main window while processing
  main_window.Enable(False)
  cmd_line = "echo {} | {}".format(pword, " ".join(["sudo -S", cmd] + args))
  # FIXME: should this be done with subprocess module?
  res = os.popen(cmd_line).read()
  main_window.Enable(True)
  return 0, res


__installers = ("gdebi-gtk", "gdebi-kde", "qapt-deb-installer")

## Retrieves a list of recognized .deb installing applications.
#
#  @todo
#    Move to different package.
def getDebInstallerList():
  return __installers


## Retrieves a usable GUI .deb installer application.
#
#  @return
#    Path to installer executable or `None` if not available.
#  @todo
#    Move to different package.
def getDebInstaller():
  for inst in __installers:
    cmd = paths.getExecutable(inst)
    if cmd:
      return cmd
  return None
