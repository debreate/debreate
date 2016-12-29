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
            style=PD_DEFAULT_STYLE, detailed=False, resize=True):
        wx.ProgressDialog.__init__(self, title, message, maximum, parent, style)
        
        self.resize = resize
        
        self.active = None
        
        if wx.MAJOR_VERSION < 3 and self.GetWindowStyle() & wx.PD_CAN_ABORT:
            wx.EVT_CLOSE(self, self.OnAbort)
            for C in self.GetChildren():
                if isinstance(C, wx.Button) and C.GetId() == wx.ID_CANCEL:
                    C.Bind(wx.EVT_BUTTON, self.OnAbort)
        
        if size:
            self.SetSize(size)
        
        self.detailed = detailed
        self.txt_tasks = None
        if detailed:
            lyt_main = self.GetSizer()
            
            self.txt_tasks = wx.StaticText(self, label=u'{} / {}'.format(0, maximum))
            
            children = self.GetChildren()
            
            t_index = None
            for X in children:
                if isinstance(X, wx.StaticText):
                    t_index = children.index(X)
                    #lyt_main.Detach(X)
                    break
            
            if t_index != None:
                lyt_main.Insert(t_index+1, self.txt_tasks, 0, wx.ALIGN_CENTER|wx.TOP, 5)
                lyt_main.Layout()
                
                dimensions_original = self.GetSizeTuple()
                
                self.Fit()
                
                dimensions_new = self.GetSizeTuple()
                
                # Preserve original width
                self.SetSize(wx.Size(dimensions_original[0], dimensions_new[1]))
                wx.Yield()
        
        if parent:
            self.CenterOnParent()
    
    
    ## Sets the active status to False
    #  
    #  Calls dbr.progress.ProgressDialog.OnAbort
    def Cancel(self):
        self.OnAbort()
    
    
    ## Closes & destroys the dialog
    #  
    #  Method for compatibility between wx 3.0 & older versions
    #  For 3.0 & newer, simply overrides wx.ProgressDialog.Destroy
    #  For older versions, calls dbr.progress.ProgressDialog.EndModal
    def Destroy(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            self.EndModal(0)
        
        return wx.ProgressDialog.Destroy(self, *args, **kwargs)
    
    
    ## Retrieves the wx.Gauge child object
    #  
    #  Mostly for compatibility with wx versions older than 3.0
    #  Older versions do not have many of methods for access & manipulation of the gauge
    def GetGauge(self):
        for C in self.GetChildren():
            if isinstance(C, wx.Gauge):
                return C
    
    
    ## Retrieves the message shown on the dialog
    #  
    #  Method for compatibility between wx 3.0 & older versions
    #  For wx 3.0 & newer, simply overrides wx.ProgressDialog.GetMessage
    #  For older versions, finds the child wx.StaticText object & returns the label
    def GetMessage(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            for C in self.GetChildren():
                if isinstance(C, wx.StaticText):
                    return C.GetLabel()
            
            return
        
        return wx.ProgressDialog.GetMessage(self, *args, **kwargs)
    
    
    ## Retrieves the range, or maximum value of the gauge
    #  
    #  Method for compatibility between wx 3.0 & older versions
    #  For 3.0 & newer, simply overrides wx.ProgressDialog.GetRange
    #  For older versions, calls GetRange on the child gauge object
    def GetRange(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            return self.GetGauge().GetRange()
        
        return wx.ProgressDialog.GetRange(self, *args, **kwargs)
    
    
    ## Retrieves the current value of the gauge
    #  
    #  Method for compatibility between wx 3.0 & older versions
    #  for 3.0 & newer, simply overrides wx.ProgressDialog.GetValue
    #  For older versions, calls GetValue() on the child wx.Gauge object
    def GetValue(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            return self.GetGauge().GetValue()
        
        return wx.ProgressDialog.GetValue(self, *args, **kwargs)
    
    
    ## Sets the active status to False
    #  
    #  The dialog will be destroyed when dbr.progress.ProgressDialog.WasCancelled is called
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
        
        if self.detailed:
            self.txt_tasks.SetLabel(u'{} / {}'.format(args[0], self.GetRange()))
        
        if self.resize:
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
        
        self.GetSizer().Layout()
    
    
    ## Override wx.ProgressDialog.WasCancelled method for compatibility wx older wx versions
    def WasCancelled(self, *args, **kwargs):
        if wx.MAJOR_VERSION < 3:
            if self.active == None:
                return False
            
            return not self.active
        
        # Failsafe for compatibility between wx 3.0 & older versions
        if self.active == False:
            return True
        
        return wx.ProgressDialog.WasCancelled(self, *args, **kwargs)
