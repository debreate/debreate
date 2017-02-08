# -*- coding: utf-8 -*-

## \package input.pathctrl

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from input.essential    import EssentialField
from input.text         import TextArea


## A text area that can track if it's value is an actual path on the system
class PathCtrl(TextArea):
    def __init__(self, parent, win_id=wx.ID_ANY, value=u'/', defaultValue=u'/', warn=False,
            name=wx.TextCtrlNameStr):
        
        TextArea.__init__(self, parent, win_id, value, defaultValue, name=name)
        
        # TODO: Rename to 'self.Default'
        self.Default = defaultValue
        
        self.Warn = warn
        
        # For restoring color of text area
        self.clr_default = self.GetBackgroundColour()
        
        # Make sure first character is forward slash
        wx.EVT_KEY_UP(self, self.OnKeyUp)
        
        # Set to default value & check path availability on construction
        self.Reset()
    
    
    ## Retrieves the text area's default value
    def GetDefaultValue(self):
        return self.Default
    
    
    ## Key events trigger checking path availability
    def OnKeyUp(self, event=None):
        value = self.GetValue()
        insertion_point = self.GetInsertionPoint()+1
        if value == wx.EmptyString or value[0] != u'/':
            self.SetValue(u'/{}'.format(value))
            self.SetInsertionPoint(insertion_point)
        
        value = self.GetValue()
        self.SetPathAvailable()
        
        if event:
            event.Skip()
    
    
    ## Resets text area to default value
    def Reset(self):
        self.SetPathAvailable()
        self.SetInsertionPointEnd()
        
        return TextArea.Reset(self)
    
    
    ## If using 'Warn', changed background to red if path doesn't exists on system
    def SetPathAvailable(self):
        # input.ifield.InputField calls 'Reset' before PathCtrl is constructed
        try:
            if self.Warn:
                if os.path.isdir(self.GetValue()):
                    self.SetBackgroundColour(self.clr_default)
                    return
                
                self.SetBackgroundColour(u'red')
        
        except AttributeError:
            pass
    
    
    ## Checks if field will show a warning when path is not available
    def ShowsWarning(self):
        return self.Warn
    
    
    ## Sets the text area's default value
    def SetDefaultValue(self, default):
        self.Default = default


## PathCtrl that notifies main window to mark project dirty
class PathCtrlESS(PathCtrl, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, value=u'/', defaultValue=u'/', warn=False,
            name=wx.TextCtrlNameStr):
        
        PathCtrl.__init__(self, parent, win_id, value, defaultValue, warn, name)
        EssentialField.__init__(self)
