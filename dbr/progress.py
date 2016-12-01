# -*- coding: utf-8 -*-

## \package dbr.progress

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language import GT


PD_DEFAULT_STYLE = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE


## A progress dialog that is compatible between wx versions
class ProgressDialog(wx.ProgressDialog):
    def __init__(self, parent, title=GT(u'Progress'), message=wx.EmptyString, size=None, maximum=100,
            style=PD_DEFAULT_STYLE):
        wx.ProgressDialog.__init__(self, title, message, maximum, parent, style)
        
        self.active = None
        
        if wx.MAJOR_VERSION < 3 and self.GetWindowStyle() & wx.PD_CAN_ABORT:
            wx.EVT_CLOSE(self, self.OnAbort)
            for C in self.GetChildren():
                if isinstance(C, wx.Button) and C.GetId() == wx.ID_CANCEL:
                    C.Bind(wx.EVT_BUTTON, self.OnAbort)
        
        if size:
            self.SetSize(size)
        
        if parent:
            self.CenterOnParent()
    
    
    ## TODO: Doxygen
    def Destroy(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            self.EndModal(0)
        
        return wx.ProgressDialog.Destroy(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def GetGauge(self):
        for C in self.GetChildren():
            if isinstance(C, wx.Gauge):
                return C
    
    
    ## TODO: Doxygen
    def GetMessage(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            for C in self.GetChildren():
                if isinstance(C, wx.StaticText):
                    return C.GetLabel()
            
            return
        
        return wx.ProgressDialog.GetMessage(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def GetRange(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            return self.GetGauge().GetRange()
        
        return wx.ProgressDialog.GetRange(self, *args, **kwargs)
    
    
    ## TODO: Doxgen
    def GetValue(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            return self.GetGauge().GetValue()
        
        return wx.ProgressDialog.GetValue(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def OnAbort(self, event=None):
        self.active = False
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def SetMessage(self, message):
        for C in self.GetChildren():
            if isinstance(C, wx.StaticText):
                return C.SetLabel(message)
        
        return False
    
    
    ## TODO: Doxygen
    def SetRange(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            return self.GetGauge().SetRange(*args, **kwargs)
        
        return wx.ProgressDialog.SetRange(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def ShowModal(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            self.active = True
        
        return wx.ProgressDialog.ShowModal(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def Update(self, *args, **kwargs):
        update_value = wx.ProgressDialog.Update(self, *args, **kwargs)
        
        self.UpdateSize()
        
        return update_value
    
    
    ## Currently only updates width
    #  
    #  FIXME: Window updates immediately, but children do not
    def UpdateSize(self):
        children = self.GetChildren()
        target_width = 0
        
        for C in children:
            child_width = C.GetSizeTuple()[0]
            if child_width > target_width:
                target_width = child_width
        
        if children:
            padding_x = children[0].GetPositionTuple()[0]
            
            # Add padding
            target_width += (padding_x * 2)
            
            width = self.GetSize()
            height = width[1]
            width = width[0]
            
            if target_width > width:
                self.SetSize((target_width, height))
                
                if self.GetParent():
                    self.CenterOnParent()
    
    
    ## Override WasCancelled method for compatibility wx older wx versions
    def WasCancelled(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            if self.active == None:
                return False
            
            return not self.active
        
        return wx.ProgressDialog.WasCancelled(self, *args, **kwargs)
