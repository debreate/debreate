# -*- coding: utf-8 -*-

## \package wxcustom.cursor

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from globals.paths import ConcatPaths
from globals.paths import PATH_app


PATH_cursors = u'{}/bitmaps/cursor'.format(PATH_app)

def GetCursor(name, size=16):
    global PATH_cursors
    
    cursor_bitmap = ConcatPaths((PATH_cursors, str(size), u'{}.png'.format(name)))
    
    if not os.path.isfile(cursor_bitmap):
        return None
    
    return wx.Cursor(cursor_bitmap, wx.BITMAP_TYPE_PNG)


CUR_FOLDER = GetCursor(u'folder')
