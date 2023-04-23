
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.workingdir

import os

from libdbr        import config
from libdbr        import paths
from libdbr.logger import Logger


logger = Logger(__name__)

## Changes working directory & writes to config
#
#  This method should be called in code instead of os.chdir
#  unless there is an explicit reason to do otherwise.
#  \param target_dir
#  	\b \e str : Path to set as new working directory
def ChangeWorkingDirectory(target_dir):
  if logger.debugging():
    logger.debug("ChangeWorkingDirectory: {}".format(target_dir), newline=True)
    print("  Working dir before: {}".format(os.getcwd()))

  success = False

  try:
    os.chdir(target_dir)
    cfg_user = config.get("user")
    config_dir = cfg_user.getValue("workingdir", default=os.getcwd())

    if config_dir != target_dir:
      cfg_user.setValue("workingdir", target_dir)
      cfg_user.save()
      success = True

  except OSError:
    # Default to the user's home directory
    dir_home = paths.getUserHome()
    if os.path.isdir(dir_home):
      os.chdir(dir_home)

  if logger.debugging():
    print("  Working dir after:  {}\n".format(os.getcwd()))

  return success
