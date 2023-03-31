## \package dbr.workingdir

# MIT licensing
# See: docs/LICENSE.txt


import os

import util

from dbr.config    import ReadConfig
from dbr.config    import WriteConfig
from globals       import paths


logger = util.getLogger()

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
    config_dir = ReadConfig("workingdir")

    if config_dir != target_dir:
      WriteConfig("workingdir", target_dir)
      success = True

  except OSError:
    # Default to the user's home directory
    dir_home = paths.getHomeDir()
    if os.path.isdir(dir_home):
      os.chdir(dir_home)

  if logger.debugging():
    print("  Working dir after:  {}\n".format(os.getcwd()))

  return success
