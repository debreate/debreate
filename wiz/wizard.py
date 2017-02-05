# -*- coding: utf-8 -*-

## \package wiz.wizard

# MIT licensing
# See: docs/LICENSE.txt


import os, traceback, wx

from dbr.event          import ChangePageEvent
from dbr.language       import GT
from dbr.log            import DebugEnabled
from dbr.log            import Logger
from globals            import ident
from globals.errorcodes import ERR_DIR_NOT_AVAILABLE
from globals.errorcodes import dbrerrno
from globals.fileio     import WriteFile
from globals.ident      import chkid
from globals.ident      import inputid
from globals.ident      import listid
from globals.ident      import menuid
from globals.ident      import page_ids
from globals.ident      import pgid
from globals.ident      import selid
from globals.strings    import TextIsEmpty
from globals.system     import mimport
from globals.tooltips   import TT_wiz_next
from globals.tooltips   import TT_wiz_prev
from input.markdown     import MarkdownDialog
from startup.tests      import GetTestList
from ui.button          import ButtonHelp
from ui.button          import ButtonNext
from ui.button          import ButtonPrev
from ui.dialog          import ShowDialog
from ui.dialog          import ShowErrorDialog
from ui.layout          import BoxSizer
from ui.notebook        import MultiTemplate
from ui.notebook        import Notebook
from ui.panel           import ScrolledPanel
from wiz.helper         import FieldEnabled
from wiz.helper         import GetAllTypeFields
from wiz.helper         import GetField
from wiz.helper         import GetMainWindow
from wiz.helper         import GetMenu


## Wizard class for Debreate
class Wizard(wx.Panel):
    def __init__(self, parent, page_list=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, page_list)
        
        testing = u'alpha' in GetTestList()
        
        # List of pages available in the wizard
        self.pages = []
        
        self.pages_ids = {}
        
        # IDs for first & last pages
        self.ID_FIRST = None
        self.ID_LAST = None
        
        if testing:
            # Help button
            btn_help = ButtonHelp(self)
            btn_help.SetToolTipString(GT(u'Page help'))
        
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
        
        # These widgets are put into a list so that they are not automatically hidden
        self.permanent_children = [
            pnl_title,
            self.btn_prev,
            self.btn_next,
            ]
        
        if testing:
            self.permanent_children.insert(0, btn_help)
        
        # *** Event Handling *** #
        
        if testing:
            btn_help.Bind(wx.EVT_BUTTON, self.OnHelpButton)
        
        self.btn_prev.Bind(wx.EVT_BUTTON, self.ChangePage)
        self.btn_next.Bind(wx.EVT_BUTTON, self.ChangePage)
        
        # *** Layout *** #
        
        # Position the text in the header
        lyt_title = wx.GridSizer(1, 1)
        lyt_title.Add(self.txt_title, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        
        pnl_title.SetSizer(lyt_title)
        
        # Button sizer includes header
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        
        if testing:
            lyt_buttons.Add(btn_help, 0, wx.LEFT, 5)
        
        lyt_buttons.AddSpacer(5)
        lyt_buttons.Add(pnl_title, 1, wx.EXPAND|wx.RIGHT, 5)
        lyt_buttons.Add(self.btn_prev)
        lyt_buttons.AddSpacer(5)
        lyt_buttons.Add(self.btn_next)
        lyt_buttons.AddSpacer(5)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(lyt_buttons, 0, wx.EXPAND)
        
        self.SetSizer(lyt_main)
        self.SetAutoLayout(True)
        self.Layout()
    
    
    ## Add a new page to the wizard
    #
    #  \param page
    #    Must either be a WizardPage instance or the string suffix of the page's moduls
    def AddPage(self, page):
        err_msg = None
        err_det = None
        
        if not isinstance(page, WizardPage):
            try:
                pagemod = u'wizbin.{}'.format(page)
                page = mimport(pagemod).Page(self)
            
            except ImportError:
                err_msg = u'module does not exist'
                err_det = traceback.format_exc()
        
        lyt_main = self.GetSizer()
        
        if not err_msg:
            # Must already be child
            if not isinstance(page, WizardPage):
                err_msg = u'not WizardPage instance'
            
            elif page not in self.GetChildren():
                err_msg = u'not child of wizard'
            
            elif page in lyt_main.GetChildWindows():
                err_msg = u'page is already added to wizard'
        
        if err_msg:
            err_msg = u'Cannot add page, {}'.format(err_msg)
            
            if err_det:
                ShowErrorDialog(err_msg, err_det)
            
            else:
                ShowErrorDialog(err_msg)
            
            return
        
        main_window = GetMainWindow()
        
        lyt_main.Add(page, 1, wx.EXPAND)
        self.pages.append(page)
        
        # Add to page menu
        page_menu = GetMenu(menuid.PAGE)
        
        page_menu.AppendItem(
            wx.MenuItem(page_menu, page.Id, page.GetLabel(),
            kind=wx.ITEM_RADIO))
        
        # Bind menu event to ID
        wx.EVT_MENU(main_window, page.Id, main_window.OnMenuChangePage)
    
    
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
        
        GetMainWindow().GetMenuBar().GetMenuById(menuid.PAGE).Check(page_id, True)
    
    
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
            # Support using list of IDs instead of WizardPage instances
            if not isinstance(P, WizardPage):
                P = self.GetPage(P)
            
            P.Export(out_dir)
    
    
    ## Retrieves all current page instances
    def GetAllPages(self):
        return tuple(self.pages)
    
    
    ## Retrieve currently showing page
    def GetCurrentPage(self):
        for page in self.pages:
            if page.IsShown():
                return page
    
    
    ## Retrieve currently showing page's ID
    def GetCurrentPageId(self):
        current_page = self.GetCurrentPage()
        if current_page:
            return current_page.GetId()
    
    
    ## TODO: Doxygen
    def GetPage(self, page_id):
        for P in self.pages:
            if P.GetId() == page_id:
                return P
        
        Logger.Warn(__name__, u'Page with ID {} has not been constructed'.format(page_id))
    
    
    ## Retrieves the full list of page IDs
    #  
    #  \return
    #        \b e\ tuple : List of all page IDs
    def GetPagesIdList(self):
        page_ids = []
        
        for P in self.pages:
            page_ids.append(P.GetId())
        
        return tuple(page_ids)
    
    
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
                        
                        page.ImportFromFile(u'{}/{}'.format(PATH, F))
    
    
    ## Initailize the wizard
    def Initialize(self, showPage=0):
        if self.pages:
            self.ID_FIRST = self.pages[0].Id
            self.ID_LAST = self.pages[-1].Id
        
        if not showPage:
            self.ShowPage(self.ID_FIRST)
        
        else:
            self.ShowPage(self.pages[showPage].Id)
        
        self.Layout()
    
    
    ## Uses children WizardPage instances to set pages
    def InitPages(self):
        pages = []
        
        for C in self.GetChildren():
            if isinstance(C, WizardPage):
                pages.append(C)
        
        return self.SetPages(pages)
    
    
    ## Show a help dialog for current page
    def OnHelpButton(self, event=None):
        label = self.GetCurrentPage().GetLabel()
        page_help = MarkdownDialog(self, title=GT(u'Help'), readonly=True)
        
        page_help.SetText(GT(u'Help information for page "{}"'.format(label)))
        
        ShowDialog(page_help)
    
    
    ## Remove a page from the wizard & memory
    #
    #  \param pageId
    #    \b \e Integer ID of the page to remove
    def RemovePage(self, pageId):
        page = self.GetPage(pageId)
        
        if page in self.pages:
            self.pages.pop(self.pages.index(page))
        
        lyt_main = self.GetSizer()
        if page in lyt_main.GetChildWindows():
            lyt_main.Remove(page)
        
        self.Layout()
        
        # Remove from page menu
        GetMainWindow().GetMenuBar().GetMenuById(menuid.PAGE).Remove(pageId).Destroy()
    
    
    ## Reset all but greeting page
    def Reset(self):
        for PAGE in reversed(self.pages):
            if PAGE.Id != pgid.GREETING:
                self.RemovePage(PAGE.Id)
        
        self.Initialize()
    
    
    ## TODO: Doxygen
    def ResetPagesInfo(self):
        for page in self.pages:
            page.Reset()
    
    
    ## Sets up the wizard for 'binary' mode
    def SetModeBin(self):
        self.Reset()
        
        mods = [
            u'control',
            u'depends',
            u'files',
            u'scripts',
            u'changelog',
            u'copyright',
            u'launchers',
            u'build',
            ]
        
        if u'alpha' in GetTestList() or DebugEnabled():
            mods.insert(3, u'manuals')
        
        for M in mods:
            self.AddPage(M)
        
        self.Initialize(1)
    
    
    ## Sets up the wizard for 'source' mode
    def SetModeSrc(self):
        self.Reset()
    
    
    ## TODO: Doxygen
    def SetPages(self, pages):
        self.ID_FIRST = pages[0].GetId()
        self.ID_LAST = pages[-1].GetId()
        
        main_window = GetMainWindow()
        
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
        
        for PAGE in pages:
            if PAGE.GetId() != pgid.GREETING:
                self.pages.append(PAGE)
                self.pages_ids[PAGE.GetId()] = PAGE.GetName().upper()
                self.GetSizer().Insert(1, PAGE, 1, wx.EXPAND)
                
                page_id = PAGE.GetId()
                
                # Add pages to main menu
                page_menu = main_window.GetMenu(menuid.PAGE)
                
                page_menu.AppendItem(
                    wx.MenuItem(page_menu, page_id, PAGE.GetLabel(),
                    kind=wx.ITEM_RADIO))
                
                # Bind menu event to ID
                wx.EVT_MENU(main_window, page_id, main_window.OnMenuChangePage)
        
        # Initailize functions that can only be called after all pages are constructed
        for PAGE in pages:
            PAGE.InitPage()
        
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
        
        wx.PostEvent(GetMainWindow(), ChangePageEvent(0))


## Parent class for wizard pages
class WizardPage(ScrolledPanel):
    def __init__(self, parent, page_id):
        ScrolledPanel.__init__(self, parent, page_id)
        
        # Pages should not be shown until wizard is initialized
        self.Hide()
        
        self.SetName(page_ids[self.GetId()])
        
        ## Label to show in title & menu
        self.label = None
        
        ## List of IDs that should not be reset
        self.IgnoreResetIds = []
        
        # Is added to prebuild check list
        self.prebuild_check = True
    
    
    ## TODO: Doxygen
    #  
    #  Child class must define 'Get' method.
    def Export(self, out_dir, out_name=wx.EmptyString):
        if not os.path.isdir(out_dir):
            Logger.Debug(__name__, u'Directory does not exist: {}'.format(out_dir))
            return ERR_DIR_NOT_AVAILABLE
        
        if out_name == wx.EmptyString:
            out_name = page_ids[self.GetId()].upper()
        
        page_info = self.Get()
        
        if not page_info:
            return 0
        
        if not out_name:
            out_name = self.Name
        
        if TextIsEmpty(page_info):
            return 0
        
        absolute_filename = u'{}/{}'.format(out_dir, out_name)
        
        Logger.Debug(out_name, u'Exporting: {}'.format(absolute_filename))
        
        WriteFile(absolute_filename, page_info)
        
        return 0
    
    
    ## Exports data for the build process
    def ExportBuild(self, target):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method ExportBuild').format(self.GetName()))
        
        return (dbrerrno.SUCCESS, None)
    
    
    ## TODO: Doxygen
    def Get(self, getModule=False):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method Get').format(self.GetName()))
    
    
    ## TODO: Doxygen
    def GetLabel(self):
        if self.label == None:
            return self.GetName()
        
        return self.label
    
    
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
    
    
    ## Retrieve the parent Wizard instance
    #  
    #  \return
    #    \b \e dbr.Wizard
    def GetWizard(self):
        return self.GetParent()
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method ImportFromFile').format(self.GetName()))
    
    
    ## This method should contain anything that needs to be initialized only after all pages are constructed
    #
    #  FIXME: Rename to 'OnWizardInit'???
    def InitPage(self):
        Logger.Debug(__name__, GT(u'Page {} does not override inherited method InitPage').format(self.GetName()))
        
        return False
    
    
    ## TODO: Doxygen
    def IsOkay(self):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method IsOkay').format(self.GetName()))
        
        return False
    
    
    ## Resets page fields to default settings
    #
    #  Set the IgnoreResetIds attribute for any field that should not be reset
    def Reset(self):
        field_ids = (
            chkid,
            inputid,
            listid,
            selid,
            )
        
        for IDTYPE in field_ids:
            idlist = IDTYPE.IdList
            
            for ID in idlist:
                if ID not in self.IgnoreResetIds:
                    field = GetField(self, ID)
                    
                    if isinstance(field, wx.Window):
                        field.Reset()
        
        # Pages that use MultiTemplate instances
        multit_ids = (
            pgid.MAN,
            pgid.LAUNCHERS,
            )
        
        if self.Id in multit_ids:
            NBLIST = GetAllTypeFields(self, Notebook)
            
            if NBLIST:
                for NB in NBLIST:
                    MT = NB.GetContainingSizer()
                    
                    if isinstance(MT, MultiTemplate):
                        MT.Reset()
