# -*- coding: utf-8 -*-

# Wizard class for Debreate

# System imports
import wx, os
from wx.lib.newevent import NewCommandEvent

# Local imports
from dbr import Logger
from dbr.buttons import ButtonNext, ButtonPrev
from dbr.constants import ERR_DIR_NOT_AVAILABLE
from dbr.functions import TextIsEmpty


ID_PREV = wx.NewId()
ID_NEXT = wx.NewId()

class Wizard(wx.Panel):
    def __init__(self, parent, page_list=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, page_list)
        
        self.parent = parent
        
        # List of pages available in the wizard
        self.pages = []
        
        # A Header for the wizard
        self.title = wx.Panel(self, style=wx.RAISED_BORDER)
        self.title.SetBackgroundColour((10, 47, 162))
        self.title_txt = wx.StaticText(self.title, -1, u'Title') # Text displayed from objects "name" - object.GetName()
        self.title_txt.SetForegroundColour((255, 255, 255))
        
        headerfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD) # font to use in the header
        self.title_txt.SetFont(headerfont)
        
        # Position the text in the header
        title_sizer = wx.GridSizer(1, 1)
        title_sizer.Add(self.title_txt, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.title.SetSizer(title_sizer)
        self.title.Layout()
        
        # Previous and Next buttons
        self.button_prev = ButtonPrev(self, ID_PREV)
        self.button_next = ButtonNext(self, ID_NEXT)
        
        wx.EVT_BUTTON(self.button_prev, -1, self.ChangePage)
        wx.EVT_BUTTON(self.button_next, -1, self.ChangePage)
        
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
    
    def SetPages(self, pages):
        # Make sure all pages are hidden
        children = self.GetChildren()
        for child in children:
            if child not in self.permanent_children:
                child.Hide()
        
        self.ClearPages() # Remove any current pages from the wizard
        
        if type(pages) not in (list, tuple):
            raise TypeError(u'Argument 2 of dbwizard.SetPages() must be List or Tuple')
        
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
    
    def ChangePage(self, event):
        event_id = event.GetEventObject().GetId()
        
        # Get index of currently shown page
        for page in self.pages:
            if page.IsShown():
                index = self.pages.index(page)
        
        if event_id == ID_PREV:
            if index != 0:
                index -= 1
        elif event_id == ID_NEXT:
            if index != len(self.pages)-1:
                index += 1
        
        # Show the indexed page
        self.ShowPage(self.pages[index].GetId())
        
        # Check current page in "pages menu"
        for p in self.parent.pages:
            if self.pages[index].GetId() == p.GetId():
                p.Check()
#        for page in self.pages:
#            if page != self.pages[index]:
#                page.Hide()
#            else:
#                page.Show()
#                self.title_txt.SetLabel(page.GetName())
#        
#        self.Layout()
#        for child in self.GetChildren():
#            wx.PostEvent(child, self.evt)
    
    def ClearPages(self):
        for page in self.pages:
            self.sizer.Remove(page)
        self.pages = []
        # Re-enable the buttons if the have been disabled
        self.EnableNext()
        self.EnablePrev()
    
    def SetTitle(self, title):
        self.title_txt.SetLabel(title)
        self.Layout()
    
    def EnableNext(self, value=True):
        if type(value) in (type(True), type(1)):
            if value:
                self.button_next.Enable()
            else:
                self.button_next.Disable()
        else:
            raise TypeError(u'Must be bool or int value')
    
    def DisableNext(self):
        self.EnableNext(False)
    
    def EnablePrev(self, value=True):
        if type(value) in (type(True), type(1)):
            if value:
                self.button_prev.Enable()
            else:
                self.button_prev.Disable()
        else:
            raise TypeError(u'Must be bool or int value')
    
    def DisablePrev(self):
        self.EnablePrev(False)
    
    def GetCurrentPage(self):
        for page in self.pages:
            if page.IsShown():
                return page
    
    
    def ExportPages(self, page_list, out_dir):
        for P in page_list:
            P.Export(out_dir)


## Parent class for wizard pages
class WizardPage():
    def __init__(self):
        return
    
    
    def GetPageInfo(self):
        return None
    
    
    ## 
    #  
    #  Child class must define 'GetPageInfo' method.
    def Export(self, out_dir, out_name=wx.EmptyString):
        if not os.path.isdir(out_dir):
            Logger.Debug(__name__, u'Directory does not exist: {}'.format(out_dir))
            return ERR_DIR_NOT_AVAILABLE
        
        if out_name == wx.EmptyString:
            out_name = self.GetName()
        
        out_name = out_name.upper()
        
        page_info = self.GetPageInfo()
        
        if not page_info:
            return 0
        
        page_name = page_info[0]
        page_info = page_info[1]
        
        if TextIsEmpty(page_info):
            return 0
        
        absolute_filename = u'{}/{}'.format(out_dir, out_name)
        
        Logger.Debug(page_name, u'Exporting: {}'.format(absolute_filename))
        
        f_opened = open(absolute_filename, u'w')
        f_opened.write(page_info)
        f_opened.close()
        
        return 0
