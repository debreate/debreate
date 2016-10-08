# -*- coding: utf-8 -*-

## \package dbr.dialogs


import wx, os
# FIXME: Can't import Logger
#from dbr import Logger
from dbr.language import GT



class OverwriteDialog(wx.MessageDialog):
    def __init__(self, parent, path):
        wx.MessageDialog.__init__(self, parent, wx.EmptyString,
                style=wx.ICON_QUESTION|wx.YES_NO|wx.YES_DEFAULT)
        
        self.SetYesNoLabels(GT(u'Replace'), GT(u'Cancel'))
        
        filename = os.path.basename(path)
        dirname = os.path.basename(os.path.dirname(path))
        
        self.SetMessage(
            GT(u'A file named "{}" already exists. Do you want to replace it?').format(filename)
        )
        
        self.SetExtendedMessage(
            GT(u'The file already exists in "{}". Replacing it will overwrite its contents.').format(dirname)
        )


class StandardFileSaveDialog(wx.FileDialog):
    def __init__(self, parent, title, default_dir=os.getcwd(), default_extension=wx.EmptyString,
            wildcard=wx.FileSelectorDefaultWildcardStr,
            style=wx.FD_SAVE|wx.FD_CHANGE_DIR):
        wx.FileDialog.__init__(self, parent, title, default_dir, wildcard=wildcard, style=style)
        
        self.extension = default_extension
        
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnAccept)
    
    
    def GetFilename(self, *args, **kwargs):
        filename = wx.FileDialog.GetFilename(self, *args, **kwargs)
        
        if not filename.split(u'.')[-1] == self.extension:
            filename = u'{}.{}'.format(filename, self.extension)
        
        return filename
    
    
    def GetPath(self, *args, **kwargs):
        path = wx.FileDialog.GetPath(self, *args, **kwargs)
        
        out_dir = os.path.dirname(path)
        return u'{}/{}'.format(out_dir, self.GetFilename())
    
    
    def GetExtension(self):
        return self.extension
    
    
    def OnAccept(self, event=None):
        path = self.GetPath()
        if os.path.isfile(path):
            overwrite = OverwriteDialog(self, path).ShowModal()
            
            if overwrite == wx.ID_YES:
                self.EndModal(wx.ID_OK)
            
            return
        
        self.EndModal(wx.ID_OK)
