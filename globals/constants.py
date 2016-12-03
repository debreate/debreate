# -*- coding: utf-8 -*-

## \package globals.constants
#  
#  Global variables used throughout the application & should remain constant.
#  TODO: Rename or delete


import os
import wx

from dbr.language   import GT
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
    
    FILE = open(u'{}/INSTALLED'.format(PATH_app))
    lines = FILE.read().split(u'\n')
    FILE.close()
    
    for L in lines:
        if u'=' in L:
            key = L.split(u'=')
            value = key[1]
            key = key[0]
            
            if key.lower() == u'prefix':
                return value
    
    return PATH_app


PREFIX = GetPrefix()



## Location of common licenses installed on the system
system_licenses_path = u'/usr/share/common-licenses'


# *** Default *** #
DEFAULT_SIZE = (800, 650)
DEFAULT_POS = (0, 0)


# *** File Types *** #
FTYPE_EXE = wx.NewId()

file_types_defs = {
    FTYPE_EXE: GT(u'script/executable'),
}


# *** Colors *** #
COLOR_ERROR = wx.Colour(255, 143, 115)
