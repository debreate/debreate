# -*- coding: utf-8 -*-

## \package dbr.dialogs


import wx, os
# FIXME: Can't import Logger
#from dbr import Logger
from dbr.language import GT
from dbr.buttons import ButtonConfirm
from dbr.constants import ICON_ERROR



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



# *** MESSAGE & ERROR *** #

## Displays a dialog with message & details
#  
#  FIXME: Crashes if icon is wx.NullBitmap
class DetailedMessageDialog(wx.Dialog):
    def __init__(self, parent, title=GT(u'Message'), icon=wx.NullBitmap, text=wx.EmptyString,
            details=wx.EmptyString, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(500,500), style=style)
        
        self.icon = wx.StaticBitmap(self, -1, wx.Bitmap(icon))
        
        self.text = wx.StaticText(self, -1, text)
        
        self.button_details = wx.ToggleButton(self, -1, GT(u'Details'))
        self.btn_copy_details = wx.Button(self, label=GT(u'Copy details'))
        
        wx.EVT_TOGGLEBUTTON(self.button_details, -1, self.ToggleDetails)
        wx.EVT_BUTTON(self.btn_copy_details, wx.ID_ANY, self.OnCopyDetails)
        
        LH_buttons1 = wx.BoxSizer(wx.HORIZONTAL)
        LH_buttons1.Add(self.button_details, 1)
        LH_buttons1.Add(self.btn_copy_details, 1)
        
        self.details = wx.TextCtrl(self, -1, details, size=(300,150), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.details.SetSize(self.details.GetBestSize())
        
        self.button_ok = ButtonConfirm(self)
        
        r_sizer = wx.BoxSizer(wx.VERTICAL)
        r_sizer.AddSpacer(10)
        r_sizer.Add(self.text)
        r_sizer.AddSpacer(20)
        r_sizer.Add(LH_buttons1)
        r_sizer.Add(self.details, 1, wx.EXPAND)
        r_sizer.Add(self.button_ok, 0, wx.ALIGN_RIGHT)
        
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.icon, 0, wx.ALL, 20)
        self.main_sizer.Add(r_sizer, 1, wx.EXPAND)
        self.main_sizer.AddSpacer(10)
        
        self.SetAutoLayout(True)
        self.ToggleDetails()
        
        self.btn_copy_details.Hide()
        self.details.Hide()
    
    
    # FIXME:
    def OnCopyDetails(self, event=None):
        print(u'DEBUG: Copying details to clipboard ...')
        
        cb_set = False
        
        clipboard = wx.Clipboard()
        if clipboard.Open():
            print(u'DEBUG: Clipboard opened')
            
            details = wx.TextDataObject(self.details.GetValue())
            print(u'DEBUG: Details set to:\n{}'.format(details.GetText()))
            
            clipboard.Clear()
            print(u'DEBUG: Clipboard cleared')
            
            cb_set = clipboard.SetData(details)
            print(u'DEBUG: Clipboard data set')
            
            clipboard.Flush()
            print(u'DEBUG: Clipboard flushed')
            
            clipboard.Close()
            print(u'DEBUG: Clipboard cloased')
        
        del clipboard
        print(u'DEBUG: Clipboard object deleted')
        
        wx.MessageBox(GT(u'FIXME: Details not copied to clipboard'), GT(u'Debug'))
    
    
    def SetDetails(self, details):
        self.details.SetValue(details)
        self.details.SetSize(self.details.GetBestSize())
        
        self.Layout()
    
    
    def ToggleDetails(self, event=None):
        if self.button_details.GetValue():
            self.details.Show()
        
        else:
            self.details.Hide()
        
        self.SetSizerAndFit(self.main_sizer)
        self.Layout()


## Message dialog that shows an error & details
class ErrorDialog(DetailedMessageDialog):
    def __init__(self, parent, text=wx.EmptyString, details=wx.EmptyString):
        DetailedMessageDialog.__init__(self, parent, GT(u'Error'), ICON_ERROR, text, details)
        
        self.btn_copy_details.Show()
        
        self.Layout()
