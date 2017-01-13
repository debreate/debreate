# -*- coding: utf-8 -*-

## \package dbr.filedrop

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.dialogs        import TextOverwriteDialog
from dbr.language       import GT
from globals            import ident
from globals.strings    import TextIsEmpty


## Object for drag-&-drop text files
class SingleFileTextDropTarget(wx.FileDropTarget):
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj
    
    
    ## Defines actions to take when a file is dropped on object
    #  
    #  \param x
    #        ???
    #  \param y
    #        ???
    #  \param filenames
    #        ???
    def OnDropFiles(self, x, y, filenames):
        if len(filenames) > 1:
            raise ValueError(GT(u'Too many files'))
        
        text = open(filenames[0]).read()
        try:
            if not TextIsEmpty(self.obj.GetValue()):
                overwrite = TextOverwriteDialog(self.obj, message = GT(u'The text area is not empty!'))
                ID = overwrite.ShowModal()
                if ID == ident.OVERWRITE:
                    self.obj.SetValue(text)
                
                elif ID == ident.APPEND:
                    self.obj.SetInsertionPoint(-1)
                    self.obj.WriteText(text)
            
            else:
                self.obj.SetValue(text)
        
        except UnicodeDecodeError:
            wx.MessageDialog(None, GT(u'Error decoding file'), GT(u'Error'), wx.OK).ShowModal()
