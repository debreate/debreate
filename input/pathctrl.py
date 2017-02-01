# -*- coding: utf-8 -*-

## \package input.pathctrl

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from input.text import TextArea


## A text area that can track if it's value is an actual path on the system
class PathCtrl(TextArea):
    def __init__(self, parent, win_id=wx.ID_ANY, value=u'/', defaultValue=u'/', warn=False,
            default=wx.EmptyString, name=wx.TextCtrlNameStr):
        
        TextArea.__init__(self, parent, win_id, value, defaultValue, name=name)
        
        self.Warn = warn
        
        # Get the value of the textctrl so it can be restored
        self.default = default
        
        # For restoring color of text area
        self.clr_default = self.GetBackgroundColour()
        
        # Make sure first character is forward slash
        wx.EVT_KEY_UP(self, self.OnKeyUp)
        
        # Check if path is available on construction
        if self.Warn:
            self.SetPathAvailable()
    
    
    ## Retrieves the text area's default value
    def GetDefaultValue(self):
        return self.default
    
    
    ## Key events trigger checking path availability
    def OnKeyUp(self, event=None):
        value = self.GetValue()
        insertion_point = self.GetInsertionPoint()+1
        if value == wx.EmptyString or value[0] != u'/':
            self.SetValue(u'/{}'.format(value))
            self.SetInsertionPoint(insertion_point)
        
        # If PathCtrl is set to warn on non-existent paths, change background color to red when path
        # doesn't exist
        value = self.GetValue()
        if self.Warn:
            self.SetPathAvailable()
        
        if event:
            event.Skip()
    
    
    ## Resets text area to default value
    #  
    #  \override input.text.TextArea.Reset
    def Reset(self):
        TextArea.Reset(self)
        
        if self.ctrl_type == PATH_WARN:
            self.SetPathAvailable()
        
        self.SetInsertionPointEnd()
    
    
    ## If using 'Warn', changed backgroun to red if path doesn't exists on system
    def SetPathAvailable(self):
        if os.path.isdir(self.GetValue()):
            self.SetBackgroundColour(self.clr_default)
            return
        
        self.SetBackgroundColour(u'red')
    
    
    ## Sets the text area's default value
    def SetDefaultValue(self, default):
        self.default = default
