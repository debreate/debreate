## \package globals.execute
#
#  Executable commands available from the system

# MIT licensing
# See: docs/LICENSE.txt

import errno
import os
import subprocess
import wx

from subprocess import PIPE
from subprocess import STDOUT

import libdbr.bin

from dbr.language  import GT
from libdbr.logger import getLogger
from libdbr.paths  import getExecutable
from wiz.helper    import GetMainWindow


__logger = getLogger()

## TODO: Doxygen
def ExecuteCommand(cmd, args=[], elevate=False, pword=wx.EmptyString):
  __logger.deprecated(__name__, ExecuteCommand.__name__, "globals.executeElevated")

  if elevate and pword.strip(" \t\n") == wx.EmptyString:
    return (None, GT("Empty password"))

  CMD_sudo = GetExecutable("sudo")

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

  stdout = wx.EmptyString

  if isinstance(cmd_output, subprocess.Popen):
    if cmd_output.stdout:
      stdout = cmd_output.stdout

    if cmd_output.stderr:
      if stdout == wx.EmptyString:
        stdout = cmd_output.stderr

      else:
        stdout = "{}\n{}".format(stdout, cmd_output.stderr)

    returncode = cmd_output.returncode

  else:
    stdout = cmd_output
    returncode = 0

  return (returncode, stdout)


## TODO: Doxygen
def GetCommandOutput(cmd, args=[]):
  __logger.deprecated(__name__, GetCommandOutput.__name__, "libdbr.bin.execute")

  code, output = libdbr.bin.execute(cmd, args)
  return output

## Retrieves executable it exists on system
def GetExecutable(cmd):
  __logger.deprecated(__name__, GetExecutable.__name__, "libdbr.paths.getExecutable")

  alternatives = {
    "fakeroot": "fakeroot-sysv",
    }

  found_command = getExecutable(cmd)

  if not found_command and cmd in alternatives:
    if isinstance(alternatives[cmd], str):
      found_command = alternatives[cmd]

    else:
      for ALT in alternatives[cmd]:
        found_command = getExecutable(ALT)
        if found_command:
          break

  return found_command


def GetSystemInstaller():
  system_installer = GetExecutable("gdebi-gtk")

  if not system_installer:
    system_installer = GetExecutable("gdebi-kde")

  return system_installer
