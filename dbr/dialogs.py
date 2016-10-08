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
        
        self.parent = parent
        
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
        
        self.parent = parent
        
        self.extension = default_extension
        
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnAccept)
    
    
    def GetDebreateWindow(self):
        return self.parent.GetDebreateWindow()
    
    
    ## FIXME: Seems to be being called 3 times
    def GetFilename(self, *args, **kwargs):
        filename = wx.FileDialog.GetFilename(self, *args, **kwargs)
        
        # Allow users to manually set filename extension
        if not self.HasExtension(filename):
            if not filename.split(u'.')[-1] == self.extension:
                filename = u'{}.{}'.format(filename, self.extension)
        
        return filename
    
    
    ## Fixme: Seems to be being called twice
    def GetPath(self, *args, **kwargs):
        path = wx.FileDialog.GetPath(self, *args, **kwargs)
        
        if len(path):
            if path[-1] == u'.':
                #wx.MessageDialog(self, GT(u'Filename cannot end with "{}"').format(path[-1]), GT(u'Error'),
                #        style=wx.ICON_ERROR|wx.OK).ShowModal()
                name_error = wx.MessageDialog(self.GetDebreateWindow(), GT(u'Error'),
                        style=wx.ICON_ERROR|wx.OK)
                
                name_error.SetExtendedMessage(GT(u'Name cannot end with "{}"').format(path[-1]))
                # FIXME: Setting icon causes segfault
                #name_error.SetIcon(MAIN_ICON)
                name_error.ShowModal()
                
                return None
        
        out_dir = os.path.dirname(path)
        return u'{}/{}'.format(out_dir, self.GetFilename())
    
    
    def GetExtension(self):
        return self.extension
    
    
    def HasExtension(self, path):
        if u'.' in path:
            if path.split(u'.')[-1] != u'':
                return True
        
        return False
    
    
    def OnAccept(self, event=None):
        path = self.GetPath()
        
        if path:
            if os.path.isfile(path):
                overwrite = OverwriteDialog(self.GetDebreateWindow(), path).ShowModal()
                
                if overwrite == wx.ID_YES:
                    os.remove(path)
                    self.EndModal(wx.ID_OK)
                
                return
            
            self.EndModal(wx.ID_OK)
