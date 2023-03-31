
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import subprocess
import sys

import util.logger


logger = util.logger.getLogger()
modules = {}

def installModule(name, package=None):
  if package == None:
    package = name
  if name in modules:
    logger.warn("not re-installing module: {}".format(name))
    return 0
  try:
    modules[name] = __import__(name)
    logger.warn("not re-installing module: {}".format(name))
    return 0
  except ModuleNotFoundError:
    pass
  logger.info("installing module: {}".format(name))
  subprocess.run((sys.executable, "-m", "pip", "install", package))
  res = 0
  try:
    modules[name] = __import__(name)
  except ModuleNotFoundError:
    logger.error("unable to install module: {}".format(name))
    res = errno.ENOENT
  return res

def getModule(name):
  if name not in modules:
    try:
      modules[name] = __import__(name)
    except ModuleNotFoundError:
      logger.warn("module not available: {}".format(name))
      return None
  return modules[name]

def checkWx():
  wx = getModule("wx")
  wx_min = [4, 1, 1]
  wx_ver = []
  for v in wx.__version__.split("."):
    wx_ver.append(int(v))
  if wx_ver < wx_min:
    tmp = ".".join(str(wx_min).strip("[]").split(", "))
    logger.error("wxPython minimum required version is {}, found {}".format(tmp, wx.__version__))
    sys.exit(1)
