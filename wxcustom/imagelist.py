# -*- coding: utf-8 -*-

## \package wxcustom.imagelist

# MIT licensing
# See: docs/LICENSE.txt


import wx


class DirectoryImageList(wx.ImageList):
    def __init__(self, width, height, mask=True, initial_count=1):
        wx.ImageList.__init__(self, width, height, mask, initial_count)
        
        directory_images = [
            (wx.ART_FOLDER, u'folder'),
            (wx.ART_FOLDER_OPEN, u'folder open'),
            (wx.ART_HARDDISK, u'harddisk'),
            (wx.ART_CDROM, u'cdrom'),
            (wx.ART_FLOPPY, u'floppy'),
            (wx.ART_REMOVABLE, u'removable'),
            (wx.ART_NORMAL_FILE, u'normal file'),
            (wx.ART_EXECUTABLE_FILE, u'executable file'),
            ]
        
        aliases = (
            (u'normal file', (u'file',)),
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
            
            self.Add(wx.ArtProvider.GetBitmap(IMAGE, wx.ART_CMN_DIALOG, wx.Size(width, height)))
    
    
    ## Retrieves image index for setting in dbr.tree.DirectoryTree
    #  
    #  \param description
    #    \b \e String name/description for image
    def GetImageIndex(self, description):
        if description in self.Images:
            return self.Images[description]


## Image list used for dbr.tree.DirectoryTree
#  
#  NOTE: dbr.tree module will be moving to wxcustom package
sm_DirectoryImageList = DirectoryImageList(16, 16)
