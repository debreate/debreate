# -*- coding: utf-8 -*-

## \package ui.panel

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.styles import PANEL_BORDER


## Global function for setting & updating scrolled window scrollbars
#  
#  \param window
#    \b \e wx.ScrolledWindow to be set
#  \return
#    \b \e True if scrollbars were set
def SetScrollbars(window):
    if isinstance(window, wx.ScrolledWindow):
        window.SetScrollbars(20, 20, 0, 0)
        
        return True
    
    return False


## Abstract class
class PanelBase:
    ## Checks if the instance has children windows
    def HasChildren(self):
        if isinstance(self, wx.Window):
            return len(self.GetChildren()) > 0
        
        return False


## A wx.Panel with a border
#  
#  This is to work around differences in wx 3.0 with older versions
class BorderedPanel(wx.Panel, PanelBase):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=wx.TAB_TRAVERSAL, name=wx.PanelNameStr):
        
        wx.Panel.__init__(self, parent, ID, pos, size, style|PANEL_BORDER, name)
    
    
    ## Hide the panel's border
    def HideBorder(self):
        return self.ShowBorder(False)
    
    
    ## Show or hide the panel's border
    #  
    #  \param show
    #    If \b \e True, show border, otherwise hide
    #  \return
    #    \b \e True if border visible state changed
    def ShowBorder(self, show=True):
        style = self.GetWindowStyleFlag()
        
        if show:
            if not style & PANEL_BORDER:
                self.SetWindowStyleFlag(style|PANEL_BORDER)
                
                return True
        
        elif style & PANEL_BORDER:
            self.SetWindowStyleFlag(style&~PANEL_BORDER)
            
            return True
        
        return False


## A wx.ScrolledWindow that sets scrollbars by default
class ScrolledPanel(wx.ScrolledWindow, PanelBase):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=wx.HSCROLL|wx.VSCROLL, name=u'scrolledPanel'):
        
        wx.ScrolledWindow.__init__(self, parent, win_id, pos, size, style, name)
        
        SetScrollbars(self)
    
    
    ## Override inherited method to also update the scrollbars
    def Layout(self):
        layout = wx.ScrolledWindow.Layout(self)
        
        self.UpdateScrollbars()
        
        return layout
    
    
    ## Refresh the panel's size so scrollbars will update
    def UpdateScrollbars(self):
        sizer = self.GetSizer()
        if sizer:
            self.SetVirtualSize(sizer.GetMinSize())


## Class designed for custom controls parented with a BorderedPanel
class ControlPanel:
    ## Retrieve main child of panel
    #  
    #  Intended for use in input.essential.EssentialField
    def GetMainControl(self):
        return self.MainCtrl
