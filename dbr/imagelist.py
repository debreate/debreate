# -*- coding: utf-8 -*-

## \package dbr.imagelist

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.image import GetBitmap
from dbr.log import Logger


## List of images used by dbr.tree.DirectoryTree
class DirectoryImageList(wx.ImageList):
    def __init__(self, width, height, mask=True, initial_count=1):
        wx.ImageList.__init__(self, width, height, mask, initial_count)
        
        directory_images = []
        
        custom_images = (
            u'computer',
            u'failsafe',
            u'folder',
            u'folder-home',
            u'folder-open',
            u'file',
            u'hard-disk',
            )
        
        for I in custom_images:
            directory_images.append((GetBitmap(I), I))
        
        stock_images = (
            (wx.ART_CDROM, u'cdrom'),
            (wx.ART_FLOPPY, u'floppy'),
            (wx.ART_REMOVABLE, u'removable'),
            (wx.ART_EXECUTABLE_FILE, u'executable file'),
            )
        
        for I in stock_images:
            directory_images.append(I)
        
        aliases = (
            (u'file', (u'normal file',)),
            (u'hard-disk', (u'harddisk',)),
            )
        
        self.Images = {}
        
        for I in range(len(directory_images)):
            # Keys are set by index value
            self.Images[directory_images[I][1]] = I
        
        for ORIG, ALIST in aliases:
            for ALIAS in ALIST:
                self.Images[ALIAS] = self.Images[ORIG]
        
        for IMAGE in directory_images:
            IMAGE = IMAGE[0]
            
            if isinstance(IMAGE, wx.Bitmap):
                Logger.Debug(__name__, u'Adding wx.Bitmap to image list')
                
                self.Add(IMAGE)
            
            else:
                Logger.Debug(__name__, u'Adding bitmap from wx.ArtProvider')
                
                self.Add(wx.ArtProvider.GetBitmap(IMAGE, wx.ART_CMN_DIALOG, wx.Size(width, height)))
    
    
    ## Retrieves image index for setting in dbr.tree.DirectoryTree
    #  
    #  \param description
    #    \b \e String name/description for image
    #  \return
    #    \b \e Integer index of image or index of failsafe image if description doesn't exist
    def GetImageIndex(self, description):
        if description in self.Images:
            return self.Images[description]
        
        return self.Images[u'failsafe']


## Image list used for dbr.tree.DirectoryTree
sm_DirectoryImageList = DirectoryImageList(16, 16)
