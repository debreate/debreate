# -*- coding: utf-8 -*-

## \package wiz.wizard
#
#  The wizard interface

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
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    #  \param pageList
    #    <b><i>List</i></b> of wiz.wizard.WizardPage instances to initialize
    #    wizard with
    def __init__(self, parent, pageList=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, pageList)
        
        testing = u'alpha' in GetTestList()
        
        # List of pages available in the wizard
        self.Pages = []
        
        self.PagesIds = {}
        
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
    #    Must either be a wiz.wizard.WizardPage instance or the string suffix of the page's module
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
        self.Pages.append(page)
        
        # Add to page menu
        page_menu = GetMenu(menuid.PAGE)
        
        page_menu.AppendItem(
            wx.MenuItem(page_menu, page.Id, page.GetLabel(),
            kind=wx.ITEM_RADIO))
        
        # Bind menu event to ID
        wx.EVT_MENU(main_window, page.Id, main_window.OnMenuChangePage)
    
    
    ## Handles displaying a new page when commanded
    def ChangePage(self, event=None):
        event_id = event.GetEventObject().GetId()
        
        # Get index of currently shown page
        for page in self.Pages:
            if page.IsShown():
                index = self.Pages.index(page)
                
                break
        
        if event_id == ident.PREV:
            if index != 0:
                index -= 1
        
        elif event_id == ident.NEXT:
            if index != len(self.Pages) - 1:
                index += 1
        
        page_id = self.Pages[index].GetId()
        
        # Show the indexed page
        self.ShowPage(page_id)
        
        GetMenu(menuid.PAGE).Check(page_id, True)
    
    
    ## Deletes all pages from the wizard
    def ClearPages(self):
        for page in self.Pages:
            self.GetSizer().Remove(page)
        
        self.Pages = []
        
        # Re-enable the buttons if they have been disabled
        self.EnableNext()
        self.EnablePrev()
    
    
    ## Disables the 'next' page button when displaying the last page
    def DisableNext(self):
        self.EnableNext(False)
    
    
    ## Disables 'previous' page button when displaying the first page
    def DisablePrev(self):
        self.EnablePrev(False)
    
    
    ## Enables/Disables 'next' page button dependent on if the last
    #  page is displayed
    #
    #  \param value
    #    Button is enabled <b><i>True</i></b>, disabled otherwise
    def EnableNext(self, value=True):
        if isinstance(value, (bool, int)):
            if value:
                self.btn_next.Enable()
            
            else:
                self.btn_next.Disable()
        
        else:
            # FIXME: Should not raise error here???
            raise TypeError(u'Must be bool or int value')
    
    
    ## Enables/Disables 'previous' page button dependent on if the last
    #  page is displayed
    #
    #  \param value
    #    Button is enabled <b><i>True</i></b>, disabled otherwise
    def EnablePrev(self, value=True):
        if isinstance(value, (bool, int)):
            if value:
                self.btn_prev.Enable()
            
            else:
                self.btn_prev.Disable()
        
        else:
            # FIXME: Should not raise error here???
            raise TypeError(u'Must be bool or int value')
    
    
    ## Exports pages individually by calling wiz.wizard.WizardPage.Export
    #
    #  Filename output is handled by classes inheriting WizardPage
    #
    #  \param pageList
    #    List of WizardPage instances, or page IDs, to be exported
    #  \param outDir
    #    Path to target directory
    def ExportPages(self, pageList, outDir):
        for P in pageList:
            # Support using list of IDs instead of WizardPage instances
            if not isinstance(P, WizardPage):
                P = self.GetPage(P)
            
            P.Export(outDir)
    
    
    ## Retrieves all current wiz.wizard.WizardPage instances
    #
    #  \return
    #    <b><i>Tuple</i></b> list of currently available wizard pages
    def GetAllPages(self):
        return tuple(self.Pages)
    
    
    ## Retrieves currently displayed page
    #
    #  \return
    #    wiz.wizard.WizardPage instance
    def GetCurrentPage(self):
        for page in self.Pages:
            if page.IsShown():
                return page
    
    
    ## Retrieve currently displayed page's ID
    #
    #  \return
    #    <b><i>Integer</i></b> ID of page
    def GetCurrentPageId(self):
        current_page = self.GetCurrentPage()
        if current_page:
            return current_page.GetId()
    
    
    ## Retrieves a page by ID
    #
    #  \param pageId
    #    <b><i>Integer</i></b> ID of desired page
    #  \return
    #    wiz.wizard.WizardPage instance or <b><i>None</i></b> if ID not found
    def GetPage(self, pageId):
        for P in self.Pages:
            if P.GetId() == pageId:
                return P
        
        Logger.Warn(__name__, u'Page with ID {} has not been constructed'.format(pageId))
    
    
    ## Retrieves the full list of page IDs
    #
    #  \return
    #    <b><i>Tuple</i></b> list of all current pages IDs
    def GetPagesIdList(self):
        page_ids = []
        
        for P in self.Pages:
            page_ids.append(P.GetId())
        
        return tuple(page_ids)
    
    
    ## Fills information for each page when project file is opened
    #
    #  Each page imports a file by parsing the filename
    #
    #  \param filesDir
    #    Path to directory where project files have been extracted
    def ImportPagesInfo(self, filesDir):
        for PATH, DIRS, FILES in os.walk(filesDir):
            for F in FILES:
                for page in self.Pages:
                    page_name = page_ids[page.GetId()].upper()
                    n_index = len(page_name)
                    
                    if F[:n_index] == page_name:
                        Logger.Debug(__name__,
                                GT(u'Imported project file {} matches page {}'.format(F, page_name)))
                        
                        page.ImportFromFile(u'{}/{}'.format(PATH, F))
    
    
    ## Initializes wizard by displaying an initial page
    #
    #  \param showPage
    #    <b><i>Integer</i></b> index of page to be shown
    def Initialize(self, showPage=0):
        if self.Pages:
            self.ID_FIRST = self.Pages[0].Id
            self.ID_LAST = self.Pages[-1].Id
        
        if not showPage:
            self.ShowPage(self.ID_FIRST)
        
        else:
            self.ShowPage(self.Pages[showPage].Id)
        
        for PAGE in self.Pages:
            PAGE.InitPage()
        
        self.Layout()
    
    
    ## Uses children wiz.wizard.WizardPage instances to set pages
    #
    #  \return
    #    Value of wiz.wizard.Wizard.SetPages
    def InitPages(self):
        pages = []
        
        for C in self.GetChildren():
            if isinstance(C, WizardPage):
                pages.append(C)
        
        return self.SetPages(pages)
    
    
    ## Handles event emitted by 'help' button
    #
    #  Shows a help dialog for currently displayed page
    def OnHelpButton(self, event=None):
        label = self.GetCurrentPage().GetLabel()
        page_help = MarkdownDialog(self, title=GT(u'Help'), readonly=True)
        
        page_help.SetText(GT(u'Help information for page "{}"'.format(label)))
        
        ShowDialog(page_help)
    
    
    ## Removes a page from the wizard & memory
    #
    #  \param pageId
    #    <b><i>Integer</i></b> ID of the page to be removed
    def RemovePage(self, pageId):
        page = self.GetPage(pageId)
        
        if page in self.Pages:
            self.Pages.pop(self.Pages.index(page))
        
        lyt_main = self.GetSizer()
        if page in lyt_main.GetChildWindows():
            lyt_main.Remove(page)
        
        self.Layout()
        
        # Remove from page menu
        GetMenu(menuid.PAGE).Remove(pageId).Destroy()
    
    
    ## Resets all but greeting page
    #
    #  \return
    #    Value of wiz.wizard.Wizard.Initialize
    def Reset(self):
        for PAGE in reversed(self.Pages):
            if PAGE.Id != pgid.GREETING:
                self.RemovePage(PAGE.Id)
        
        return self.Initialize()
    
    
    ## Resets each page's fields to default settings
    #
    #  Calls wiz.wizard.WizardPage.Reset
    def ResetPagesInfo(self):
        for page in self.Pages:
            page.Reset()
    
    
    ## Sets up the wizard for 'binary' mode
    #
    #  \param startPage
    #    <b><i>Integer</i></b> index of page to be initially displayed
    def SetModeBin(self, startPage=1):
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
        
        self.Initialize(startPage)
    
    
    ## Sets up the wizard for 'source' mode
    #
    #  FIXME: WIP
    def SetModeSrc(self):
        self.Reset()
    
    
    ## Organizes wiz.wizard.WizardPage instances for displaying as pages in wizard
    #
    #  FIXME: Deprecated???
    #
    #  \param pages
    #    List of pages owned by wizard to be used
    #  \deprecated
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
                self.Pages.append(PAGE)
                self.PagesIds[PAGE.GetId()] = PAGE.GetName().upper()
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
    
    
    ## Sets the text displayed in the wizard title bar
    #
    #  \param title
    #    Text to be displayed
    def SetTitle(self, title):
        self.txt_title.SetLabel(title)
        self.Layout()
    
    
    ## Sets or changes the displayed page
    #
    #  Posts a 'change page' event to notify the main window
    #
    #  \param pageId
    #    globals.ident.pgid of the page to be displayed
    def ShowPage(self, pageId):
        for p in self.Pages:
            if p.GetId() != pageId:
                p.Hide()
            
            else:
                p.Show()
                self.txt_title.SetLabel(p.GetLabel())
        
        if pageId == self.ID_FIRST:
            self.btn_prev.Enable(False)
        
        elif not FieldEnabled(self.btn_prev):
            self.btn_prev.Enable(True)
        
        if pageId == self.ID_LAST:
            self.btn_next.Enable(False)
        
        elif not FieldEnabled(self.btn_next):
            self.btn_next.Enable(True)
        
        self.Layout()
        
        wx.PostEvent(GetMainWindow(), ChangePageEvent(0))


## Inherited class for wizard pages
class WizardPage(ScrolledPanel):
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    #  \param pageId
    #    Identifier to use for page
    def __init__(self, parent, pageId):
        ScrolledPanel.__init__(self, parent, pageId)
        
        # Pages should not be shown until wizard is initialized
        self.Hide()
        
        self.SetName(page_ids[self.GetId()])
        
        ## Label to show in title & menu
        self.Label = wx.EmptyString
        
        if not self.Label and self.Id in pgid.Labels:
            self.Label = pgid.Labels[self.Id]
        
        ## List of IDs that should not be reset
        self.IgnoreResetIds = []
        
        # Is added to prebuild check list
        self.prebuild_check = True
    
    
    ## Collects page's data & exports it to file
    #
    #  \param target
    #    Absolute filename path for output
    def Export(self, target):
        page_data = self.Get()
        
        return WriteFile(target, page_data)
    
    
    ## FIXME: Deprecated
    #
    #  \deprecated
    def ExportDeprecated(self, outDir, outName=wx.EmptyString):
        if not os.path.isdir(outDir):
            Logger.Debug(__name__, u'Directory does not exist: {}'.format(outDir))
            return ERR_DIR_NOT_AVAILABLE
        
        if outName == wx.EmptyString:
            outName = page_ids[self.GetId()].upper()
        
        page_info = self.Get()
        
        if not page_info:
            return 0
        
        if not outName:
            outName = self.Name
        
        if TextIsEmpty(page_info):
            return 0
        
        absolute_filename = u'{}/{}'.format(outDir, outName)
        
        Logger.Debug(outName, u'Exporting: {}'.format(absolute_filename))
        
        WriteFile(absolute_filename, page_info)
        
        return 0
    
    
    ## Exports data for the build process
    #
    #  \param target
    #    Filename path to be exported
    def ExportBuild(self, target):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method ExportBuild').format(self.GetName()))
        
        return (dbrerrno.SUCCESS, None)
    
    
    ## Retrieves the page's field's data
    #
    #  \param getModule
    #    If <b><i>True</i></b>, returns a <b><i>tuple</b></i> of the module name
    #    & page data, otherwise return only page data string
    def Get(self, getModule=False):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method Get').format(self.GetName()))
    
    
    ## Retrieves the page's label
    #
    #  if wiz.wizard.WizardPage.Label is not set, returns the wiz.wizard.WizardPage.Name attribute
    def GetLabel(self):
        if self.Label == None:
            return self.GetName()
        
        return self.Label
    
    
    ## Retrieves all fields that cannot be left blank for build
    #
    #  FIXME: Should only require page ID
    #
    #  \param children
    #    <b><i>List/Tuple</i></b> of the fields to be checked
    #  \return
    #    <b><i>Tuple</i></b> list of fields marked as required
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
    
    
    ## Reads & parses page data from a formatted text file
    #
    #  \param filename
    #    File path to open
    def ImportFromFile(self, filename):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method ImportFromFile').format(self.GetName()))
    
    
    ## This method can be used to access page members that are only available
    #  after the wizard has been completely initialized
    #
    #  FIXME: Rename to 'OnWizardInit'???
    def InitPage(self):
        Logger.Debug(__name__, GT(u'Page {} does not override inherited method InitPage').format(self.GetName()))
        
        return False
    
    
    ## Checks the page's fields for exporting
    #
    #  \return
    #    <b><i>False</i></b> if page cannot be exported
    def IsOkay(self):
        Logger.Warn(__name__, GT(u'Page {} does not override inherited method IsOkay').format(self.GetName()))
        
        return False
    
    
    ## Resets page's fields to default settings
    #
    #  Set the wiz.wizard.WizardPage.IgnoreResetIds attribute for any field
    #  that should not be reset
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
