
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## App initialization checks.
#
#  @package startup.startup

import os

from libdbr import config
from libdbr import logger
from libdbr import paths


__logger = logger.Logger(__name__)

initialized = False

## Sets log file.
def initLogging():
  __logger.startLogging(paths.join(paths.getUserDataRoot(), "debreate/logs"))
  __logger.info("logging to file '{}'".format(__logger.getLogFile()))

## Sets configuration file.
#
#  @return
#    `True` if new config file must be created.
def initConfig():
  first_run = True

  file_cfg = paths.join(paths.getUserConfigRoot(), "debreate", "config")
  config.setFile(file_cfg)
  if os.path.isfile(file_cfg):
    __logger.info("loading config from '{}'".format(file_cfg))
    config.load()
    first_run = False

  global initialized
  initialized = True

  file_portable = paths.join(paths.getAppDir(), "portable")
  if os.path.isfile(file_portable):
    __logger.info("running in portable mode")
    config.setValue("portable", True)

  return first_run
