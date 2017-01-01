# -*- coding: utf-8 -*-

## \package wxcustom.cursor

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from globals.bitmaps    import PATH_bitmaps
from globals.paths      import ConcatPaths


## Retrieves an image from bitmaps dir & creates a wx.Cursor
#  
#  \param name
#    \b \e string : Base filename of the image
#  \param size
#    \b \e int : Image size (denotes subfolder to search)
#  \param img_type
#    \b \e string : Image type / filename suffix
#  \return
#    \b \e wx.Cursor : Either a new cursor using the retrieved image, or wx.NullCursor
def GetCursor(name, size=16, img_type=u'png'):
    cursor_bitmap = ConcatPaths((PATH_bitmaps, str(size), u'{}.{}'.format(name, img_type)))
    
    if not os.path.isfile(cursor_bitmap):
        return wx.NullCursor
    
    return wx.Cursor(cursor_bitmap, wx.BITMAP_TYPE_PNG)
