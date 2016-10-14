# -*- coding: utf-8 -*-

import wx, os

PATH_DEFAULT = wx.NewId()
PATH_WARN = wx.NewId()


# FIXME: Use boolean value instead of type
class PathCtrl(wx.TextCtrl):
    def __init__(self, parent, id=wx.ID_ANY, value=wx.EmptyString, type=PATH_DEFAULT):
        wx.TextCtrl.__init__(self, parent, id, value)
        
        self.type = type
        
        # Get the value of the textctrl so it can be restored
        self.default = value
        
        # For restoring color of text area
        self.bg_color = self.GetBackgroundColour()
        
        # Make sure first character is forward slash
        wx.EVT_KEY_UP(self, self.OnKeyUp)
        
        # Check if path is available on construction
        if self.type == PATH_WARN:
            self.SetPathAvailable()
    
    
    def SetPathAvailable(self):
        if os.path.isdir(self.GetValue()):
            self.SetBackgroundColour(self.bg_color)
            return
        
        self.SetBackgroundColour(u'red')
    
    def OnKeyUp(self, event):
        value = self.GetValue()
        insertion_point = self.GetInsertionPoint()+1
        if value == wx.EmptyString or value[0] != u'/':
            self.SetValue(u'/{}'.format(value))
            self.SetInsertionPoint(insertion_point)
        
        # If PathCtrl is set to warn on non-existent paths, change background color to red when path
        # doesn't exist
        value = self.GetValue()
        if self.type == PATH_WARN:
            self.SetPathAvailable()
        
        event.Skip()
    
    
    def Reset(self):
        self.SetValue(self.default)
        
        if self.type == PATH_WARN:
            self.SetPathAvailable()
    
    
    def SetDefaultValue(self, value):
        self.default = value
