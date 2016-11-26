# -*- coding: utf-8 -*-

## \package dbr.wizard


import wx
from wx.lib.newevent import NewCommandEvent

from dbr.buttons        import ButtonNext
from dbr.buttons        import ButtonPrev
from dbr.language       import GT
from globals.ident      import ID_NEXT
from globals.ident      import ID_PREV
from globals.tooltips   import TT_wiz_next
from globals.tooltips   import TT_wiz_prev


## Wizard class for Debreate
class Wizard(wx.Panel):
    def __init__(self, parent, page_list=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, page_list)
        
        # List of pages available in the wizard
        self.pages = []
        
        # A Header for the wizard
        self.title = wx.Panel(self, style=wx.RAISED_BORDER)
        self.title.SetBackgroundColour((10, 47, 162))
        
        # Text displayed from objects "name" - object.GetName()
        self.title_txt = wx.StaticText(self.title, label=GT(u'Title'))
        self.title_txt.SetForegroundColour((255, 255, 255))
        
        # font to use in the header
        headerfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        
        self.title_txt.SetFont(headerfont)
        
        # Position the text in the header
        title_sizer = wx.GridSizer(1, 1)
        title_sizer.Add(self.title_txt, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.title.SetSizer(title_sizer)
        self.title.Layout()
        
        # Previous and Next buttons
        self.button_prev = ButtonPrev(self)
        self.button_prev.SetToolTip(TT_wiz_prev)
        self.button_next = ButtonNext(self)
        self.button_next.SetToolTip(TT_wiz_next)
        
        wx.EVT_BUTTON(self.button_prev, wx.ID_ANY, self.ChangePage)
        wx.EVT_BUTTON(self.button_next, wx.ID_ANY, self.ChangePage)
        
        self.ChangePageEvent, self.EVT_CHANGE_PAGE = NewCommandEvent()
        self.evt = self.ChangePageEvent(0)
        
        # Button sizer includes header
        layout_buttons = wx.BoxSizer(wx.HORIZONTAL)
        layout_buttons.AddSpacer(5)
        layout_buttons.Add(self.title, 1, wx.EXPAND)
        layout_buttons.Add(self.button_prev)
        layout_buttons.AddSpacer(5)
        layout_buttons.Add(self.button_next)
        layout_buttons.AddSpacer(5)
        
        layout_main = wx.BoxSizer(wx.VERTICAL)
        layout_main.Add(layout_buttons, 0, wx.EXPAND)
        
        self.SetSizer(layout_main)
        self.SetAutoLayout(True)
        self.Layout()
        
        # These widgets are put into a list so that they are not automatically hidden
        self.permanent_children = (self.title, self.button_prev, self.button_next)
    
    
    ## TODO: Doxygen
    def ChangePage(self, event=None):
        event_id = event.GetEventObject().GetId()
        
        # Get index of currently shown page
        for page in self.pages:
            if page.IsShown():
                index = self.pages.index(page)
        
        if event_id == ID_PREV:
            if index != 0:
                index -= 1
        
        elif event_id == ID_NEXT:
            if index != len(self.pages) - 1:
                index += 1
        
        # Show the indexed page
        self.ShowPage(self.pages[index].GetId())
        
        # Check current page in "pages menu"
        for p in wx.GetApp().GetTopWindow().pages:
            if self.pages[index].GetId() == p.GetId():
                p.Check()
    
    
    ## TODO: Doxygen
    def ClearPages(self):
        for page in self.pages:
            self.GetSizer().Remove(page)
        
        self.pages = []
        
        # Re-enable the buttons if they have been disabled
        self.EnableNext()
        self.EnablePrev()
    
    
    ## TODO: Doxygen
    def DisableNext(self):
        self.EnableNext(False)
    
    
    ## TODO: Doxygen
    def DisablePrev(self):
        self.EnablePrev(False)
    
    
    ## TODO: Doxygen
    def EnableNext(self, value=True):
        if isinstance(value, (bool, int)):
            if value:
                self.button_next.Enable()
            
            else:
                self.button_next.Disable()
        
        else:
            # FIXME: Should not raise error here???
            raise TypeError(u'Must be bool or int value')
    
    
    ## TODO: Doxygen
    def EnablePrev(self, value=True):
        if isinstance(value, (bool, int)):
            if value:
                self.button_prev.Enable()
            
            else:
                self.button_prev.Disable()
        
        else:
            # FIXME: Should not raise error here???
            raise TypeError(u'Must be bool or int value')
    
    
    ## TODO: Doxygen
    def GetCurrentPageId(self):
        for page in self.pages:
            if page.IsShown():
                return page.GetId()
    
    
    ## TODO: Doxygen
    def GetPage(self, page_id):
        for P in self.pages:
            if P.GetId() == page_id:
                return P
        
        return None
    
    
    ## TODO: Doxygen
    def SetPages(self, pages):
        # Make sure all pages are hidden
        children = self.GetChildren()
        for child in children:
            if child not in self.permanent_children:
                child.Hide()
        
        # Remove any current pages from the wizard
        self.ClearPages()
        
        if not isinstance(pages, (list, tuple)):
            # FIXME: Should not raise error here???
            raise TypeError(u'Argument 2 of Wizard.SetPages() must be List or Tuple')
        
        for page in pages:
            self.pages.append(page)
            self.GetSizer().Insert(1, page, 1, wx.EXPAND)
            
            # Show the first page
            if page != pages[0]:
                page.Hide()
            
            else:
                page.Show()
                self.title_txt.SetLabel(page.GetName())
        
        self.Layout()
    
    
    ## TODO: Doxygen
    def SetTitle(self, title):
        self.title_txt.SetLabel(title)
        self.Layout()
    
    
    ## TODO: Doxygen
    def ShowPage(self, page_id):
        for p in self.pages:
            if p.GetId() != page_id:
                p.Hide()
            
            else:
                p.Show()
                self.title_txt.SetLabel(p.GetName())
        
        self.Layout()
        
        for child in self.GetChildren():
            wx.PostEvent(child, self.evt)
