
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import os
import sys

from libdbr import fileinfo
from libdbr import paths
from libdbr import sysinfo


__os_name = sysinfo.getOSName()

def init():
  checkPathSeparator()
  checkSystemRoot()
  checkExecutables()

def checkPathSeparator():
  msys = os.getenv("MSYSTEM")
  if msys and msys.lower() in sysinfo.__msys:
    assert __os_name == "msys"
  elif sys.platform == "win32":
    assert __os_name == "win32"

  if sys.platform == "win32":
    if __os_name == "msys":
      assert os.sep == "/"
    else:
      assert os.sep == "\\"
  else:
    assert os.sep == "/"

def checkSystemRoot():
  sys_root = paths.getSystemRoot()
  if __os_name == "win32":
    assert sys_root == os.getenv("SystemDrive") + "\\"
  else:
    assert paths.getSubSystemRoot() == "/"

def checkExecutables():
  # check for common system dependent executable files
  shell = paths.normalize("/usr/bin/shell")
  if __os_name == "win32":
    shell = paths.join(paths.getSystemRoot(), "Windows", "System32", "cmd.exe")
  elif not os.path.exists(shell) or os.path.isdir(shell):
    shell = paths.normalize("/bin/shell")
  assert os.path.exists(shell) and not os.path.isdir(shell)
  assert fileinfo.isExecutable(shell)
