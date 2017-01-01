# -*- coding: utf-8 -*-

## \package dbr.image

# MIT licensing
# See: docs/LICENSE.txt


import os

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
#    \b \e string : Either pathname of image or None if file not found
def GetImage(name, size=16, img_type=u'png'):
    image = ConcatPaths((PATH_bitmaps, str(size), u'{}.{}'.format(name, img_type)))
    
    if not os.path.isfile(image):
        return None
    
    return image
