# -*- coding: utf-8 -*-

## \package globals.system

# MIT licensing
# See: docs/LICENSE.txt


import sys
import wx


# *** Python Info *** #

PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = u'{}.{}.{}'.format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


# *** wxWidgets Info *** #

WX_VER_STRING = u'{}.{}.{}'.format(wx.MAJOR_VERSION, wx.MINOR_VERSION, wx.RELEASE_VERSION)
