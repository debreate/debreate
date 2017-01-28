# -*- coding: utf-8 -*-

## \package dbr.image

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from globals.paths      import ConcatPaths
from globals.paths      import PATH_bitmaps
from globals.strings    import GS


## Retrieves an image from bitmaps dir & creates a wx.Cursor
#  
#  \param name
#    \b \e string : Base filename of the image
#  \param size
#    \b \e int : Image size (denotes subfolder to search)
#  \param cat
#    Sub-directory to search for images
#  \param img_type
#    \b \e string : Image type / filename suffix
#  \return
#    \b \e string : Either pathname of image or None if file not found
def GetImagePath(name, size=16, cat=None, img_type=u'png'):
    name = u'{}.{}'.format(name, img_type)
    
    if cat:
        paths = (PATH_bitmaps, cat, GS(size), name)
    
    else:
        paths = (PATH_bitmaps, GS(size), name)
    
    image_path = ConcatPaths(paths)
    
    # Attempt to use failsafe image if file does not exists
    if not os.path.isfile(image_path):
        image_path = ConcatPaths((PATH_bitmaps, GS(size), u'failsafe.png'))
    
    # Last resort is to retrun None if a failsafe image was not found
    if not os.path.isfile(image_path):
        return None
    
    return image_path


## Retrieves an image from bitmaps dir & creates a wx.Cursor
#  
#  \param name
#    \b \e string : Base filename of the image
#  \param size
#    \b \e int : Image size (denotes subfolder to search)
#  \param cat
#    Sub-directory to search for images
#  \param img_type
#    \b \e string : Image type / filename suffix
#  \return
#    \b \e wx.Cursor : Either a new cursor using the retrieved image, or wx.NullCursor
def GetCursor(name, size=16, cat=None, img_type=u'png'):
    image_path = GetImagePath(name, size, cat, img_type)
    
    if not image_path:
        return wx.NullCursor
    
    return wx.Cursor(image_path, wx.BITMAP_TYPE_PNG)


## Retrieves an image from bitmaps dir & creates a wx.Bitmap
#  
#  \param name
#    \b \e string : Base filename of the image
#  \param size
#    \b \e int : Image size (denotes subfolder to search)
#  \param cat
#    Sub-directory to search for images
#  \param img_type
#    \b \e string : Image type / filename suffix
#  \return
#    Either a new \b \e wx.Bitmap using the retrieved image, or \b \e wx.NullBitmap
def GetBitmap(name, size=16, cat=None, img_type=u'png'):
    image_path = GetImagePath(name, size, cat, img_type)
    
    if not image_path:
        #return wx.NullBitmap
        return wx.Bitmap(ConcatPaths((PATH_bitmaps, u'24', u'failsafe.png')))
    
    return wx.Bitmap(image_path, wx.BITMAP_TYPE_PNG)
