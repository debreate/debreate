# -*- coding: utf-8 -*-

## \package ui.panel

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.styles             import PANEL_BORDER
from globals.ident          import inputid
from globals.wizardhelper   import GetField
from ui.layout              import BoxSizer


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


## A ui.panel.ScrolledPanel that defines methods to add child sections
class SectionedPanel(ScrolledPanel):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                scrollDir=wx.VERTICAL, name=u'sectionedPanel'):
        
        style = wx.VSCROLL
        if scrollDir == wx.HORIZONTAL:
            style = wx.HSCROLL
        
        ScrolledPanel.__init__(self, parent, win_id, pos, size, style, name)
        
        # *** Event Handling *** #
        
        self.Bind(wx.EVT_CHECKBOX, self.OnSelect)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(scrollDir)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
    
    
    ## TODO: Doxygen
    def AddSection(self, panel):
        pnl_fields = panel.GetChildren()
        
        if pnl_fields:
            lyt_panel = None
            
            for FIELD in pnl_fields:
                lyt_panel = FIELD.GetContainingSizer()
                
                if lyt_panel:
                    break
            
            if lyt_panel:
                padding = 0
                if self.HasSections():
                    padding = 5
                
                # Section orientation should be opposite of main
                orient = wx.HORIZONTAL
                if self.Sizer.GetOrientation() == wx.HORIZONTAL:
                    orient = wx.VERTICAL
                
                lyt_sect = BoxSizer(orient)
                lyt_sect.Add(lyt_panel, 1, wx.EXPAND)
                lyt_sect.Add(wx.CheckBox(panel, inputid.CHECK), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
                
                panel.SetAutoLayout(True)
                panel.SetSizer(lyt_sect)
                panel.Layout()
                
                self.Sizer.Add(panel, 0, wx.EXPAND|wx.TOP, padding)
                
                self.Layout()
                
                return True
        
        return False
    
    
    ## TODO: Doxygen
    def GetSection(self, index):
        return self.GetChildren()[index]
    
    
    ## Retrieves number of sections
    def GetSectionCount(self):
        return len(self.Sizer.GetChildWindows())
    
    
    ## TODO: Doxygen
    def GetSectionIndex(self, item):
        sections = self.GetChildren()
        
        if item in sections:
            return sections.index(item)
    
    
    ## Check if any sections have been added
    def HasSections(self):
        return self.GetSectionCount() > 0
    
    
    ## Checks if any sections are selected
    def HasSelected(self):
        for SECT in self.GetChildren():
            if self.IsSelected(SECT):
                return True
        
        return False
    
    
    ## Checks if section check box state is 'checked'
    def IsSelected(self, section):
        if isinstance(section, int):
            section = self.GetSection(section)
        
        return GetField(section, inputid.CHECK).GetValue()
    
    
    ## TODO: Doxygen
    def OnSelect(self, event=None):
        self.PostCheckBoxEvent()
    
    
    ## TODO: Doxygen
    def PostCheckBoxEvent(self, target=None):
        if not target:
            target = self.Parent
        
        wx.PostEvent(target, wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, self.Id))
    
    
    ## TODO: Doxygen
    def RemoveSection(self, item):
        if isinstance(item, int):
            item = self.GetSection(item)
        
        self.Sizer.Detach(item)
        removed = item.Destroy()
        
        # Remove padding of first item
        first_section = self.Sizer.GetItemAtIndex(0)
        if first_section:
            self.Sizer.Detach(first_section)
            self.Sizer.Insert(0, first_section, 0, wx.EXPAND)
        
        self.Layout()
        
        return removed
    
    
    ## Removes all sections that are selected
    def RemoveSelected(self):
        for SECT in reversed(self.GetChildren()):
            selected = self.IsSelected(SECT)
            
            if selected:
                self.RemoveSection(SECT)


## Class designed for custom controls parented with a BorderedPanel
class ControlPanel:
    ## Retrieve main child of panel
    #  
    #  Intended for use in input.essential.EssentialField
    def GetMainControl(self):
        return self.MainCtrl
