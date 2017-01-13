# -*- coding: utf-8 -*-

## \package dbr.icon

# MIT licensing
# See: docs/LICENSE.txt


import wx


## TODO: Doxygen
class Icon(wx.Icon):
    def __init__(self, name, desiredWidth=-1, desiredHeight=-1):
        bm_type = self.GetBitmapType(name)
        
        wx.Icon.__init__(self, name, bm_type, desiredWidth, desiredHeight)
    
    
    ## TODO: Doxygen
    def GetBitmapType(self, filename):
        if filename:
            bm_types = {
                u'png': wx.BITMAP_TYPE_PNG,
                }
            
            suffix = filename.split(u'.')[-1]
            if suffix in bm_types:
                return bm_types[suffix]
        
        if wx.MAJOR_VERSION > 2:
            return wx.BITMAP_DEFAULT_TYPE
        
        return wx.BITMAP_TYPE_ANY
