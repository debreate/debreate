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
            u'audio-generic',
            u'computer',
            u'drive-fixed',
            u'drive-floppy',
            u'drive-removable',
            u'failsafe',
            u'folder',
            u'folder-home',
            u'folder-home-open',
            u'folder-open',
            u'file',
            u'image-generic',
            )
        
        for I in custom_images:
            directory_images.append((GetBitmap(I), I))
        
        stock_images = (
            (wx.ART_CDROM, u'cdrom'),
            (wx.ART_EXECUTABLE_FILE, u'file-executable'),
            (wx.ART_FLOPPY, u'drive-floppy'),
            (wx.ART_FOLDER, u'folder'),
            (wx.ART_FOLDER_OPEN, u'folder-open'),
            (wx.ART_HARDDISK, u'drive-fixed'),
            (wx.ART_NORMAL_FILE, u'file'),
            (wx.ART_REMOVABLE, u'drive-removable'),
            )
        
        # Use available stock images if a custom image has not been defined
        for SI in stock_images:
            add_stock = True
            for DI in directory_images:
                if SI[1] == DI[1]:
                    add_stock = False
                    break
            
            if add_stock:
                directory_images.append(SI)
        
        aliases = (
            (u'audio-generic', (u'audio', u'audio-file', u'file-audio',)),
            (u'file', (u'normal file',)),
            (u'drive-floppy', (u'floppy', u'floppy-drive',)),
            (u'drive-fixed', (u'hard-disk', u'harddisk', u'hard-drive', u'fixed-drive', u'drive',)),
            (u'drive-removable', (u'removable', u'removable-drive',)),
            (u'image-generic', (u'image',)),
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
