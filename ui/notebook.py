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
from wx.aui import EVT_AUINOTEBOOK_PAGE_CLOSED

from dbr.containers     import Contains
from dbr.language       import GT
from dbr.log            import Logger
from globals.ident      import btnid
from globals.strings    import TextIsEmpty
from input.toggle       import CheckBox
from ui.button          import CreateButton
from ui.dialog          import ShowDialog
from ui.dialog          import ShowErrorDialog
from ui.layout          import BoxSizer
from ui.manual          import ManPage
from ui.panel           import ScrolledPanel
from ui.prompt          import TextEntryDialog
from wiz.helper         import GetField
from wiz.helper         import GetMainWindow


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
    def DeleteAllPages(self):
        if wx.MAJOR_VERSION > 2:
            return AuiNotebook.DeleteAllPages(self)
        
        # Reversing only used for deleting pages from right to left (not necessary)
        for INDEX in reversed(range(self.GetPageCount())):
            self.DeletePage(INDEX)


## Multiple instances of a single template
#
#  A ui.layout.BoxSizer that creates a ui.notebook.Notebook instance for creating
#  multiple templates on a single wiz.wizard.WizardPage.
#
#  \param parent
#    The \b \e wx.Window parent instance
#  \param panelClass
#    \b \e wx.Panel derived class to use for tab pages
class MultiTemplate(BoxSizer):
    def __init__(self, parent, panelClass):
        BoxSizer.__init__(self, wx.VERTICAL)
        
        self.Panel = panelClass
        
        self.Tabs = Notebook(parent)
        
        self.TabButtonIds = []
        
        # *** Event Handling *** #
        
        self.Tabs.Bind(EVT_AUINOTEBOOK_PAGE_CLOSED, self.OnTabClosed)
        
        # *** Layout *** #
        
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        
        self.Add(lyt_buttons, 0, wx.EXPAND)
        self.Add(self.Tabs, 1, wx.EXPAND)
        
        # *** Post-Layout Actions *** #
        
        self.AddButton(GT(u'Add Tab'), u'add', btnid.ADD, self.OnButtonAdd)
        self.AddTabButton(GT(u'Rename Tab'), u'rename', btnid.RENAME, self.OnRenameTab)
    
    
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
    
    
    ## Adds a new button to the parent window
    def AddButton(self, label, image, btnId=wx.ID_ANY, handler=None):
        lyt_buttons = self.GetButtonSizer()
        
        if lyt_buttons:
            padding = 0
            if len(lyt_buttons.GetChildren()):
                padding = 5
            
            button = CreateButton(self.GetParent(), btnId, label, image)
            
            if button:
                if handler:
                    button.Bind(wx.EVT_BUTTON, handler)
                
                FLAG_TEXT = wx.ALIGN_CENTER_VERTICAL|wx.LEFT
                
                lyt_buttons.Add(button, 0, wx.LEFT, padding)
                
                if label:
                    lyt_buttons.Add(wx.StaticText(self.GetParent(), label=label), 0, FLAG_TEXT, 5)
                
                return button
    
    
    ## Adds a new button to parent window that is enabled/disabled with notebook tabs
    def AddTabButton(self, label, image, btnId=wx.ID_ANY, handler=None):
        button = self.AddButton(label, image, btnId, handler)
        
        if button:
            if btnId not in self.TabButtonIds:
                self.TabButtonIds.append(btnId)
            
            self.ToggleButtons()
        
        return button
    
    
    ## Adds a new tab/page to the ui.notebook.Notebook instance
    #
    #  \param title
    #    \b \e String title to use for new tab/page & target filename
    #  \return
    #    New ui.notebook.Notebook instance
    def AddPage(self, title, select=True, checkBox=None):
        if isinstance(checkBox, wx.CheckBox) and self.Panel == ManPage:
            new_page = self.Panel(self.Tabs, name=title, easy_mode=checkBox.GetValue())
        
        else:
            new_page = self.Panel(self.Tabs, name=title)
        
        added = self.Tabs.AddPage(new_page, title=title, select=select)
        
        self.ToggleButtons()
        
        return added
    
    
    ## Retrieves sizer for button instances
    def GetButtonSizer(self):
        children = self.GetChildSizers()
        
        if children:
            return children[0]
    
    
    ## Retrieves window instance of currently selected tab
    def GetCurrentPage(self):
        return self.GetPage(self.GetSelection())
    
    
    ## Alias of ui.notebook.MultiTemplate.GetCurrentPage
    def GetCurrentTab(self):
        return self.GetCurrentPage()
    
    
    ## Retrieves window instance at given index
    def GetPage(self, index):
        return self.Tabs.GetPage(index)
    
    
    ## Retrieves parent window of the ui.notebook.Notebook instance
    def GetParent(self):
        return self.Tabs.Parent
    
    
    ## Retrieves index of current tab
    def GetSelection(self):
        return self.Tabs.GetSelection()
    
    
    ## Checks if the notebook currently has any tabs
    def HasTabs(self):
        return self.Tabs.GetPageCount() > 0
    
    
    ## Handles button press event to add a new tab/page
    #
    #  \return
    #    Value of ui.notebook.TabsTemplate.SetTabName
    def OnButtonAdd(self, event=None):
        if event:
            event.Skip(True)
        
        if self.Panel == ManPage:
            return self.SetTabName(checkBox=GT(u'Easy Mode'), checked=True)
        
        return self.SetTabName()
    
    
    ## Change tab/page title & target filename
    #
    #  \return
    #    Value of ui.notebook.TabsTemplate.SetTabName
    def OnRenameTab(self, event=None):
        index = self.Tabs.GetSelection()
        
        return self.SetTabName(index, rename=True)
    
    
    ## Handles tab closed event & enables/disables rename button
    def OnTabClosed(self, event=None):
        self.ToggleButtons()
    
    
    ## Change a button's label
    #
    #  FIXME: Change tooltip too???
    def RenameButton(self, btnId, newLabel):
        children = self.GetButtonSizer().GetChildWindows()
        
        for INDEX in range(len(children)):
            # Make sure there is a label after the button
            if len(children) > INDEX + 1:
                child = children[INDEX]
                
                if isinstance(child, wx.Button) and child.Id == btnId:
                    label = children[INDEX+1]
                    
                    if isinstance(label, wx.StaticText):
                        return label.SetLabel(newLabel)
    
    
    ## Reset notebook instance to default values
    def Reset(self):
        self.Tabs.DeleteAllPages()
    
    
    ## Either renames an existing tab/page or creates a new one
    #
    #  \param index
    #    \b \e Integer index of tab/page to rename (only used if 'rename' is True)
    #  \param rename
    #    Renames an existing tab/page instead of creating a new one
    #  \return
    #    Value of ui.notebook.Notebook.SetPageText or ui.notebook.TabsTemplate.AddPage
    def SetTabName(self, index=-1, rename=False, checkBox=None, checked=False):
        getname = TextEntryDialog(GetMainWindow(), GT(u'Name for new page'))
        new_name = None
        
        if not rename and checkBox:
            check_box = CheckBox(getname, label=checkBox)
            check_box.SetValue(checked)
            
            sizer = getname.GetSizer()
            insert_point = len(sizer.GetChildren()) - 1
            
            sizer.InsertSpacer(insert_point, 5)
            sizer.Insert(insert_point + 1, check_box, 0, wx.LEFT, 16)
            
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
        
        if checkBox:
            return self.AddPage(new_name, checkBox=check_box)
        
        return self.AddPage(new_name)
    
    
    ## Enables/Disables buttons
    def ToggleButtons(self):
        parent = self.GetParent()
        
        for ID in self.TabButtonIds:
            button = GetField(parent, ID)
            
            if button:
                button.Enable(self.HasTabs())
