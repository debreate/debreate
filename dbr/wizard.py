# -*- coding: utf-8 -*-

# Wizard class for Debreate


import wx
from wx.lib.newevent import NewCommandEvent

from dbr.buttons    import ButtonNext
from dbr.buttons    import ButtonPrev
from dbr.language   import GT
from globals.ident  import ID_NEXT
from globals.ident  import ID_PREV


## TODO: Doxygen
class Wizard(wx.Panel):
    def __init__(self, parent, ID=wx.ID_ANY, page_list=None):
        wx.Panel.__init__(self, parent, ID, page_list)
        
        # List of pages available in the wizard
        self.pages = []
        
        # A Header for the wizard
        self.title = wx.Panel(self, style=wx.RAISED_BORDER)
        self.title.SetBackgroundColour((10, 47, 162))
        self.title_txt = wx.StaticText(self.title, label=GT(u'Title'))  # Text displayed from objects "name" - object.GetName()
        self.title_txt.SetForegroundColour((255, 255, 255))
        
        headerfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)  # font to use in the header
        self.title_txt.SetFont(headerfont)
        
        # Position the text in the header
        title_sizer = wx.GridSizer(1, 1)
        title_sizer.Add(self.title_txt, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.title.SetSizer(title_sizer)
        self.title.Layout()
        
        # Previous and Next buttons
        self.button_prev = ButtonPrev(self)
        self.button_next = ButtonNext(self)
        
        wx.EVT_BUTTON(self.button_prev, wx.ID_ANY, self.ChangePage)
        wx.EVT_BUTTON(self.button_next, wx.ID_ANY, self.ChangePage)
        
        self.ChangePageEvent, self.EVT_CHANGE_PAGE = NewCommandEvent()
        self.evt = self.ChangePageEvent(0)
        
        # Button sizer includes header
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddSpacer(5)
        button_sizer.Add(self.title, 1, wx.EXPAND)
        button_sizer.Add(self.button_prev)
        button_sizer.AddSpacer(5)
        button_sizer.Add(self.button_next)
        button_sizer.AddSpacer(5)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(button_sizer, 0, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
        
        # These widgets are put into a list so that they are not automatically hidden
        self.permanent_children = (self.title, self.button_prev, self.button_next)
    
    
    ## TODO: Doxygen
    def ChangePage(self, event=None):
        main_window = wx.GetApp().GetTopWindow()
        
        ID = event.GetEventObject().GetId()
        
        # Get index of currently shown page
        for page in self.pages:
            if page.IsShown():
                index = self.pages.index(page)
        
        if ID == ID_PREV:
            if index != 0:
                index -= 1
        
        elif ID == ID_NEXT:
            if index != len(self.pages) - 1:
                index += 1
        
        # Show the indexed page
        self.ShowPage(self.pages[index].GetId())
        
        # Check current page in "pages menu"
        for p in main_window.pages:
            if self.pages[index].GetId() == p.GetId():
                p.Check()
    
    
    ## TODO: Doxygen
    def ClearPages(self):
        for page in self.pages:
            self.sizer.Remove(page)
        
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
    def GetCurrentPage(self):
        for page in self.pages:
            if page.IsShown():
                return page
    
    
    ## TODO: Doxygen
    def SetPages(self, pages):
        # Make sure all pages are hidden
        children = self.GetChildren()
        for child in children:
            if child not in self.permanent_children:
                child.Hide()
        
        self.ClearPages() # Remove any current pages from the wizard
        
        if not isinstance(pages, (list, tuple)):
            # FIXME: Should not raise error here???
            raise TypeError(u'Argument 2 of Wizard.SetPages() must be List or Tuple')
        
        for page in pages:
            self.pages.append(page)
            self.sizer.Insert(1, page, 1, wx.EXPAND)
            
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
    def ShowPage(self, ID):
        for p in self.pages:
            if p.GetId() != ID:
                p.Hide()
            
            else:
                p.Show()
                self.title_txt.SetLabel(p.GetName())
        
        self.Layout()
        
        for child in self.GetChildren():
            wx.PostEvent(child, self.evt)
