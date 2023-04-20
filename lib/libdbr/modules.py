
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Python module handling.
#
#  @module libdbr.modules

import errno
import importlib
import subprocess
import sys

from .logger import Logger


__logger = Logger(__name__)
installed = {}

## Installs a Python module.
#
#  If module is not installed on system, attempts to download & install using pip. Module is then
#  cached.
#
#  @param name
#    Canonical name of module to be imported.
#  @param package
#    Optional package name which contains module.
#  @return
#    0 for success.
def installModule(name, package=None):
  if package == None:
    package = name
  if name in installed:
    __logger.warn("not re-installing module: {}".format(name))
    return 0
  try:
    installed[name] = importlib.import_module(name)
    __logger.warn("not re-installing module: {}".format(name))
    return 0
  except ModuleNotFoundError:
    pass
  __logger.info("installing module: {}".format(name))
  subprocess.run((sys.executable, "-m", "pip", "install", package))
  res = 0
  try:
    installed[name] = importlib.import_module(name)
  except ModuleNotFoundError:
    __logger.error("unable to install module: {}".format(name))
    res = errno.ENOENT
  return res

## Attempts to retrieve an installed module.
#
#  @param name
#    Canonical name of module.
#  @return
#    Imported module object or `None`.
def getModule(name):
  if name not in installed:
    try:
      installed[name] = importlib.import_module(name)
    except ModuleNotFoundError:
      __logger.warn("module not available: {}".format(name))
      return None
  return installed[name]
