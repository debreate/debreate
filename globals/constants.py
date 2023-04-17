
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Global variables used throughout the application & should remain constant.
#
#  @module globals.constants
#  @deprecated

import os, wx

from dbr.language  import GT
from libdbr        import paths
from libdbr.fileio import readFile
from libdbr.logger import Logger


__logger = Logger(__name__)
__logger.deprecated(__name__)

# Local modules
# *** Debreate Information *** #
## Determines if the application is running as portable or installed
INSTALLED = False
if os.path.isfile("{}/INSTALLED".format(paths.getAppDir())):
  INSTALLED = True

# ~ def GetPrefix():
  # ~ __logger.deprecated(__name__, GetPrefix.__name__, "util.appinfo.getInstallPrefix")

  # ~ global INSTALLED

  # ~ dir_app = paths.getAppDir()
  # ~ if not INSTALLED:
    # ~ return dir_app

  # ~ lines = readFile("{}/INSTALLED".format(dir_app)).split("\n")

  # ~ for L in lines:
    # ~ if "=" in L:
      # ~ key = L.split("=")
      # ~ value = key[1]
      # ~ key = key[0]

      # ~ if key.lower() == "prefix":
        # ~ return value

  # ~ return dir_app


# ~ PREFIX = appinfo.getInstallPrefix()

# *** Default *** #
DEFAULT_SIZE = (800, 650)
DEFAULT_POS = (0, 0)


# *** File Types *** #
FTYPE_EXE = wx.NewId()

file_types_defs = {
  FTYPE_EXE: GT("script/executable"),
}
