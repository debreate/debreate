
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## App initialization checks.
#
#  @module startup.startup

import os

from libdbr      import config
from libdbr      import fileio
from libdbr      import logger
from libdbr      import paths
from libdebreate import appinfo


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

  conf_root = paths.getUserConfigRoot()
  file_cfg_legacy = paths.join(conf_root, "debreate", "config")
  file_cfg = paths.join(paths.join(conf_root, "debreate.conf"))

  if os.path.isfile(file_cfg_legacy) and not os.path.exists(file_cfg):
    __logger.debug("moving old config '{}' to '{}'".format(file_cfg_legacy, file_cfg))
    fileio.moveFile(file_cfg_legacy, file_cfg)
    # clean up old directory
    dir_cfg_legacy = os.path.dirname(file_cfg_legacy)
    if len(os.listdir(dir_cfg_legacy)) == 0:
      fileio.deleteDir(dir_cfg_legacy)

  if os.path.isfile(file_cfg):
    __logger.info("loading config from '{}'".format(file_cfg))
    first_run = False
  # initialize configuration file
  cfg_user = config.add("user", file_cfg)

  global initialized
  initialized = True

  if appinfo.isPortable():
    __logger.info("running in portable mode")
    cfg_user.setValue("portable", True)

  return first_run
