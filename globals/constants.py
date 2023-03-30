## \package globals.constants
#
#  Global variables used throughout the application & should remain constant.
#  TODO: Rename or delete

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.language   import GT
from globals        import paths
from globals.fileio import ReadFile


# Local modules
# *** Debreate Information *** #
## Determins if the application is running as portable or installed
INSTALLED = False
if os.path.isfile("{}/INSTALLED".format(paths.getAppDir())):
  INSTALLED = True

def GetPrefix():
  global INSTALLED

  dir_app = paths.getAppDir()
  if not INSTALLED:
    return dir_app

  lines = ReadFile("{}/INSTALLED".format(dir_app), split=True)

  for L in lines:
    if "=" in L:
      key = L.split("=")
      value = key[1]
      key = key[0]

      if key.lower() == "prefix":
        return value

  return dir_app


PREFIX = GetPrefix()

# *** Default *** #
DEFAULT_SIZE = (800, 650)
DEFAULT_POS = (0, 0)


# *** File Types *** #
FTYPE_EXE = wx.NewId()

file_types_defs = {
  FTYPE_EXE: GT("script/executable"),
}
