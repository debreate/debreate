# -*- coding: utf-8 -*-

## \package ui.notebook

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.aui import AUI_NB_CLOSE_ON_ACTIVE_TAB
from wx.aui import AUI_NB_SCROLL_BUTTONS
from wx.aui import AUI_NB_TAB_MOVE
from wx.aui import AUI_NB_TAB_SPLIT
from wx.aui import AUI_NB_TOP
from wx.aui import AuiNotebook
from wx.aui import EVT_AUINOTEBOOK_PAGE_CLOSE

from dbr.containers         import Contains
from dbr.language           import GT
from dbr.log                import Logger
from globals.strings        import TextIsEmpty
from globals.wizardhelper   import GetMainWindow
from input.toggle           import CheckBox
from ui.button              import ButtonAdd
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.panel               import ScrolledPanel
from ui.prompt              import TextEntryDialog


# ???: What is TAB_SPLIT for?
DEFAULT_NB_STYLE = AUI_NB_TOP|AUI_NB_TAB_SPLIT|AUI_NB_TAB_MOVE|AUI_NB_CLOSE_ON_ACTIVE_TAB|AUI_NB_SCROLL_BUTTONS


## Custom notebook class for compatibility with legacy wx versions
class Notebook(AuiNotebook):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=DEFAULT_NB_STYLE, name=u'notebook'):
        
        AuiNotebook.__init__(self, parent, win_id, pos, size, style)
        
        # wx.aui.AuiNotebook does not allow setting name from constructor
        self.Name = name
    
    
    ## Adds a new page
    #
    #  \param page
    #    \b \e wx.Window instance that will be new page (if None, a new instance is created)
    #  \param winId
    #    Window \b \e integer ID
    #  \param title
    #    Label displayed on tab
    #  \param select
    #    Specifies whether the page should be displayed
    #  \param imageId
    #    Specifies optional image
    def AddPage(self, page=None, winId=wx.ID_ANY, title=u'tab', select=False, imageId=0):
        if not page:
            page = wx.Panel(self, winId)
        
        # Existing instance should already have an ID
        elif winId != wx.ID_ANY:
            Logger.Debug(__name__, u'Ignoring winId argument for pre-constructed page')
        
        if wx.MAJOR_VERSION <= 2:
            if not isinstance(imageId, wx.Bitmap):
                imageId = wx.NullBitmap
        
        AuiNotebook.AddPage(self, page, title, select, imageId)
        
        return page
    
    
    ## Adds a ui.panel.ScrolledPanel instance as new page
    #
    #  \param caption
    #    Label displayed on tab
    #  \param win_id
    #    Window \b \e integer ID
    #  \param select
    #    Specifies whether the page should be displayed
    #  \param imageId
    #    Specifies optional image
    def AddScrolledPage(self, caption, win_id=wx.ID_ANY, select=False, imageId=0):
        return self.AddPage(caption, ScrolledPanel(self), win_id, select, imageId)
    
    
    ## Deletes all tabs/pages
    #
    #  This is overridden to add functionality to older wx versions
    #
    #  \override wx.aui.AuiNotebook.DeleteAllPages
    def DeleteAllPages(self):
        if wx.MAJOR_VERSION > 2:
            return AuiNotebook.DeleteAllPages(self)
        
        # Reversing only used for deleting pages from right to left (not necessary)
        for INDEX in reversed(range(self.GetPageCount())):
            self.DeletePage(INDEX)


## Multiple instances of a single template
#
#  A ui.layout.BoxSizer that creates a ui.notebook.Notebook instance for creating
#  multiple templates on a single ui.wizard.WizardPage.
#
#  \param parent
#    The \b \e wx.Window parent instance
#  \param panelClass
#    \b \e wx.Panel derived class to use for tab pages
class TabsTemplate(BoxSizer):
    def __init__(self, parent, panelClass):
        BoxSizer.__init__(self, wx.VERTICAL)
        
        self.Panel = panelClass
        
        btn_add = ButtonAdd(parent)
        txt_add = wx.StaticText(parent, label=GT(u'Add page'))
        
        self.Tabs = Notebook(parent)
        
        # *** Event Handling *** #
        
        btn_add.Bind(wx.EVT_BUTTON, self.OnButtonAdd)
        
        self.Tabs.Bind(EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnCloseTab)
        
        # *** Layout *** #
        
        lyt_add = wx.BoxSizer(wx.HORIZONTAL)
        lyt_add.Add(btn_add)
        lyt_add.Add(txt_add, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        self.Add(lyt_add, 0, wx.EXPAND|wx.ALL, 5)
        self.Add(self.Tabs, 1, wx.ALL|wx.EXPAND, 5)
    
    
    ## Checks if input title is okay for using as tab title & target filename
    #
    #  \param title
    #    New \b \e string title to set as tab/page title & target filename
    #  \return
    #    \b \e True if new title is okay
    def _title_is_ok(self, title):
        if TextIsEmpty(title):
            return False
        
        return not Contains(title, (u' ', u'\t',))
    
    
    ## Adds a new tab/page to the ui.notebook.Notebook instance
    #
    #  \param title
    #    \b \e String title to use for new tab/page & target filename
    #  \return
    #    New ui.notebook.Notebook instance
    def AddPage(self, title, select=True):
        new_page = self.Panel(self.Tabs, name=title)
        
        return self.Tabs.AddPage(new_page, title=title, select=select)
    
    
    ## Retrieves parent window of the ui.notebook.Notebook instance
    def GetParent(self):
        return self.Tabs.Parent
    
    
    ## Handles button press event to add a new tab/page
    #
    #  \return
    #    Value of ui.notebook.TabsTemplate.SetTabName
    def OnButtonAdd(self, event=None):
        if event:
            event.Skip(True)
        
        return self.SetTabName()
    
    
    ## Handles closing tab event
    #
    #  TODO: Define
    def OnCloseTab(self, event=None):
        Logger.Debug(__name__, u'Closing tab')
    
    
    ## Change tab/page title & target filename
    #
    #  \return
    #    Value of ui.notebook.TabsTemplate.SetTabName
    def OnRenameTab(self, event=None):
        index = self.Tabs.GetSelection()
        
        return self.SetTabName(index, rename=True)
    
    
    ## Either renames an existing tab/page or creates a new one
    #
    #  \param index
    #    \b \e Integer index of tab/page to rename (only used if 'rename' is True)
    #  \param rename
    #    Renames an existing tab/page instead of creating a new one
    #  \return
    #    Value of ui.notebook.Notebook.SetPageText or ui.notebook.TabsTemplate.AddPage
    def SetTabName(self, index=-1, rename=False):
        getname = TextEntryDialog(GetMainWindow(), GT(u'Name for new page'))
        new_name = None
        
        if not rename:
            easy_mode = CheckBox(getname, label=u'Easy mode')
            easy_mode.SetValue(True)
            
            sizer = getname.GetSizer()
            insert_point = len(sizer.GetChildren()) - 1
            
            sizer.InsertSpacer(insert_point, 5)
            sizer.Insert(insert_point + 1, easy_mode, 0, wx.LEFT, 16)
            
            getname.SetSize(sizer.GetMinSize())
            getname.Fit()
            getname.CenterOnParent()
        
        valid_name = False
        
        while not valid_name:
            if new_name and TextIsEmpty(new_name):
                getname.Clear()
            
            # User cancelled
            if not ShowDialog(getname):
                return False
            
            else:
                new_name = getname.GetValue()
            
            valid_name = self._title_is_ok(new_name)
            
            if valid_name:
                break
            
            ShowErrorDialog(GT(u'Page name cannot contain whitespace'), warn=True)
        
        if rename:
            if index < 0:
                return False
            
            return self.Tabs.SetPageText(index, new_name)
        
        return self.AddPage(new_name, easy_mode.GetValue())
