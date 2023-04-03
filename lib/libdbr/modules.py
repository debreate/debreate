
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

# Python module handling

import errno
import subprocess
import sys

from libdbr.logger import getLogger


logger = getLogger()
installed = {}

def installModule(name, package=None):
  if package == None:
    package = name
  if name in installed:
    logger.warn("not re-installing module: {}".format(name))
    return 0
  try:
    installed[name] = __import__(name)
    logger.warn("not re-installing module: {}".format(name))
    return 0
  except ModuleNotFoundError:
    pass
  logger.info("installing module: {}".format(name))
  subprocess.run((sys.executable, "-m", "pip", "install", package))
  res = 0
  try:
    installed[name] = __import__(name)
  except ModuleNotFoundError:
    logger.error("unable to install module: {}".format(name))
    res = errno.ENOENT
  return res

def getModule(name):
  if name not in installed:
    try:
      installed[name] = __import__(name)
    except ModuleNotFoundError:
      logger.warn("module not available: {}".format(name))
      return None
  return installed[name]
