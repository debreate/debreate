
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import os

from libdbr import fileio
from libdbr import paths


## Checks if app is running portably.
#
#  @return
#    True if not installed.
def isPortable():
  # ~ return os.path.isfile(paths.join(paths.getAppDir(), "portable"))
  return not os.path.isfile(paths.join(paths.getAppDir(), "INSTALLED"))

## Retrievies app installation prefix.
#
#  @return
#    Absolute path of installation directory prefix.
def getInstallPrefix():
  if isPortable():
    return paths.getAppDir()
  prefix = ""
  install_file = paths.join(paths.getAppDir(), "INSTALLED")
  if os.path.isfile(install_file):
    # FIXME: use libdbr.config when it supports multiple config files
    for li in fileio.readFile(install_file).split("\n"):
      if "=" in li:
        tmp = li.split("=")
        key = tmp[0].strip().lower()
        value = tmp[1].strip()
        if key== "prefix":
          prefix = value
          break
  return prefix

## Retrieves location where locale files are stored.
#
#  @return
#    Absolute path to locale directory prefix.
def getLocaleDir():
  if isPortable():
    return paths.join(getInstallPrefix(), "locale")
  return paths.join(getInstallPrefix(), "share/locale")
