# -*- coding: utf-8 -*-

## \package globals.constants
#  
#  Global variables used throughout the application & should remain constant.
#  TODO: Rename or delete

# MIT licensing
# See: docs/LICENSE.txt


import os
import wx

from dbr.language   import GT
from globals.fileio import ReadFile
from globals.paths  import PATH_app


# Local modules
# *** Debreate Information *** #
## Determins if the application is running as portable or installed
INSTALLED = False
if os.path.isfile(u'{}/INSTALLED'.format(PATH_app)):
    INSTALLED = True

def GetPrefix():
    global PATH_app, INSTALLED
    
    if not INSTALLED:
        return PATH_app
    
    lines = ReadFile(u'{}/INSTALLED'.format(PATH_app), split=True)
    
    for L in lines:
        if u'=' in L:
            key = L.split(u'=')
            value = key[1]
            key = key[0]
            
            if key.lower() == u'prefix':
                return value
    
    return PATH_app


PREFIX = GetPrefix()

# *** Default *** #
DEFAULT_SIZE = (800, 650)
DEFAULT_POS = (0, 0)


# *** File Types *** #
FTYPE_EXE = wx.NewId()

file_types_defs = {
    FTYPE_EXE: GT(u'script/executable'),
}
