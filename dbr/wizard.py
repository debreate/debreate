# -*- coding: utf-8 -*-

## \package dbr.wizard

# MIT licensing
# See: docs/LICENSE.txt


import os, wx
from wx.lib.newevent import NewCommandEvent

import globals.ident as ident
from dbr.buttons            import ButtonNext
from dbr.buttons            import ButtonPrev
from dbr.functions          import TextIsEmpty
from dbr.language           import GT
from dbr.log                import Logger
from globals.errorcodes     import ERR_DIR_NOT_AVAILABLE
from globals.errorcodes     import dbrerrno
from globals.ident          import page_ids
from globals.tooltips       import TT_wiz_next
from globals.tooltips       import TT_wiz_prev
from globals.wizardhelper   import FieldEnabled
from globals.wizardhelper   import GetTopWindow


## Wizard class for Debreate
class Wizard(wx.Panel):
    def __init__(self, parent, page_list=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, page_list)
        
        # List of pages available in the wizard
        self.pages = []
        
        self.pages_ids = {}
        
        # IDs for first & last pages
        self.ID_FIRST = None
        self.ID_LAST = None
        
        # A Header for the wizard
        pnl_title = wx.Panel(self, style=wx.RAISED_BORDER)
        pnl_title.SetBackgroundColour((10, 47, 162))
        
        # Text displayed from objects "name" - object.GetName()
        self.txt_title = wx.StaticText(pnl_title, label=GT(u'Title'))
        self.txt_title.SetForegroundColour((255, 255, 255))
        
        # font to use in the header
        headerfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        
        self.txt_title.SetFont(headerfont)
        
        # Previous and Next buttons
        self.btn_prev = ButtonPrev(self)
        self.btn_prev.SetToolTip(TT_wiz_prev)
        self.btn_next = ButtonNext(self)
        self.btn_next.SetToolTip(TT_wiz_next)
        
        # FIXME: Should be global???
        self.ChangePageEvent, self.EVT_CHANGE_PAGE = NewCommandEvent()
        self.evt = self.ChangePageEvent(0)
        
        # These widgets are put into a list so that they are not automatically hidden
        self.permanent_children = (pnl_title, self.btn_prev, self.btn_next)
        
        # *** Layout *** #
        
        # Position the text in the header
        lyt_title = wx.GridSizer(1, 1)
        lyt_title.Add(self.txt_title, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        pnl_title.SetSizer(lyt_title)
        pnl_title.Layout()
        
        # Button sizer includes header
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.AddSpacer(5)
        lyt_buttons.Add(pnl_title, 1, wx.EXPAND|wx.RIGHT, 5)
        lyt_buttons.Add(self.btn_prev)
        lyt_buttons.AddSpacer(5)
        lyt_buttons.Add(self.btn_next)
        lyt_buttons.AddSpacer(5)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(lyt_buttons, 0, wx.EXPAND)
        
        self.SetSizer(lyt_main)
        self.SetAutoLayout(True)
        self.Layout()
        
        # *** Event handlers *** #
        
        self.btn_prev.Bind(wx.EVT_BUTTON, self.ChangePage)
        self.btn_next.Bind(wx.EVT_BUTTON, self.ChangePage)
    
    
    ## TODO: Doxygen
    def ChangePage(self, event=None):
        event_id = event.GetEventObject().GetId()
        
        # Get index of currently shown page
        for page in self.pages:
            if page.IsShown():
                index = self.pages.index(page)
                
                break
        
        if event_id == ident.PREV:
            if index != 0:
                index -= 1
        
        elif event_id == ident.NEXT:
            if index != len(self.pages) - 1:
                index += 1
        
        page_id = self.pages[index].GetId()
        
        # Show the indexed page
        self.ShowPage(page_id)
        
        GetTopWindow().menu_page.Check(page_id, True)
    
    
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
                self.btn_next.Enable()
            
            else:
                self.btn_next.Disable()
        
        else:
            # FIXME: Should not raise error here???
            raise TypeError(u'Must be bool or int value')
    
    
    ## TODO: Doxygen
    def EnablePrev(self, value=True):
        if isinstance(value, (bool, int)):
            if value:
                self.btn_prev.Enable()
            
            else:
                self.btn_prev.Disable()
        
        else:
            # FIXME: Should not raise error here???
            raise TypeError(u'Must be bool or int value')
    
    
    ## TODO: Doxygen
    def ExportPages(self, page_list, out_dir):
        for P in page_list:
            P.Export(out_dir)
    
    
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
    
    
    ## Fills information for each page when project file is opened
    #  
    #  \param files_dir
    #        \b \e unicode|str : Path to directory where project files have been extracted
    def ImportPagesInfo(self, files_dir):
        for PATH, DIRS, FILES in os.walk(files_dir):
            for F in FILES:
                for page in self.pages:
                    page_name = page_ids[page.GetId()].upper()
                    n_index = len(page_name)
                    
                    if F[:n_index] == page_name:
                        Logger.Debug(__name__,
                                GT(u'Imported project file {} matches page {}'.format(F, page_name)))
                        
                        page.ImportPageInfo(u'{}/{}'.format(PATH, F))
    
    
    ## TODO: Doxygen
    def ResetPagesInfo(self):
        for page in self.pages:
            page.ResetPageInfo()
    
    
    ## TODO: Doxygen
    def SetPages(self, pages):
        self.ID_FIRST = pages[0].GetId()
        self.ID_LAST = pages[-1].GetId()
        
        main_window = GetTopWindow()
        
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
            self.pages_ids[page.GetId()] = page.GetName().upper()
            self.GetSizer().Insert(1, page, 1, wx.EXPAND)
            
            # Add pages to main menu
            main_window.menu_page.AppendItem(
                wx.MenuItem(main_window.menu_page, page.GetId(), page.GetLabel(),
                kind=wx.ITEM_RADIO))
        
        self.ShowPage(self.ID_FIRST)
        
        self.Layout()
    
    
    ## TODO: Doxygen
    def SetTitle(self, title):
        self.txt_title.SetLabel(title)
        self.Layout()
    
    
    ## TODO: Doxygen
    def ShowPage(self, page_id):
        for p in self.pages:
            if p.GetId() != page_id:
                p.Hide()
            
            else:
                p.Show()
                self.txt_title.SetLabel(p.GetLabel())
        
        if page_id == self.ID_FIRST:
            self.btn_prev.Enable(False)
        
        elif not FieldEnabled(self.btn_prev):
            self.btn_prev.Enable(True)
        
        if page_id == self.ID_LAST:
            self.btn_next.Enable(False)
        
        elif not FieldEnabled(self.btn_next):
            self.btn_next.Enable(True)
        
        self.Layout()
        
        wx.PostEvent(GetTopWindow(), self.evt)


## Parent class for wizard pages
class WizardPage(wx.ScrolledWindow):
    def __init__(self, parent, page_id):
        wx.ScrolledWindow.__init__(self, parent, page_id)
        
        self.SetScrollbars(0, 20, 0, 0)
        
        self.wizard = parent
        
        self.SetName(page_ids[self.GetId()])
        
        ## Label to show in title & menu
        self.label = None
        
        # Is added to prebuild check list
        self.prebuild_check = True
    
    
    ## TODO: Doxygen
    #  
    #  Child class must define 'GetPageInfo' method.
    def Export(self, out_dir, out_name=wx.EmptyString):
        if not os.path.isdir(out_dir):
            Logger.Debug(__name__, u'Directory does not exist: {}'.format(out_dir))
            return ERR_DIR_NOT_AVAILABLE
        
        if out_name == wx.EmptyString:
            out_name = page_ids[self.GetId()].upper()
        
        page_info = self.GetPageInfo()
        
        if not page_info:
            return 0
        
        page_name = page_info[0]
        page_info = page_info[1]
        
        if TextIsEmpty(page_info):
            return 0
        
        absolute_filename = u'{}/{}'.format(out_dir, out_name)
        
        Logger.Debug(page_name, u'Exporting: {}'.format(absolute_filename))
        
        FILE_BUFFER = open(absolute_filename, u'w')
        FILE_BUFFER.write(page_info)
        FILE_BUFFER.close()
        
        return 0
    
    
    ## Exports data for the build process
    def ExportBuild(self, target):
        Logger.Warning(__name__, GT(u'Page {} does not override inherited method ExportBuild').format(self.GetName()))
        
        return (dbrerrno.SUCCESS, None)
    
    
    ## TODO: Doxygen
    def GetLabel(self):
        if self.label == None:
            return self.GetName()
        
        return self.label
    
    
    ## TODO: Doxygen
    def GetPageInfo(self, string_format=False):
        Logger.Warning(__name__, GT(u'Page {} does not override inherited method GetPageInfo').format(self.GetName()))
    
    
    ## Retrieves all fields that cannot be left blank for build
    #  
    #  \param children
    #        \b \e list|tuple : The controls to be checked
    #  \return
    #        \b \e tuple : List of controls marked as required
    def GetRequiredFields(self, children=None):
        required_fields = []
        
        if children == None:
            children = self.GetChildren()
        
        for C in children:
            for RF in self.GetRequiredFields(C.GetChildren()):
                required_fields.append(RF)
            
            # FIXME: Better way to mark fields as required???
            try:
                if C.req:
                    required_fields.append(C)
            
            except AttributeError:
                pass
        
        return tuple(required_fields)
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, filename):
        Logger.Warning(__name__, GT(u'Page {} does not override inherited method ImportPageInfo').format(self.GetName()))
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        Logger.Warning(__name__, GT(u'Page {} does not override inherited method IsExportable').format(self.GetName()))
        
        return False
    
    
    ## TODO: Doxygen
    def ResetPageInfo(self):
        Logger.Warning(__name__, GT(u'Page {} does not override inherited method ResetPageInfo').format(self.GetName()))
