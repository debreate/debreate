# -*- coding: utf-8 -*-

## \package wizbin.manuals

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.containers     import Contains
from dbr.language       import GT
from dbr.log            import Logger
from globals.ident      import btnid
from globals.ident      import pgid
from globals.strings    import TextIsEmpty
from globals.tooltips   import SetPageToolTips
from input.toggle       import CheckBox
from ui.dialog          import ShowDialog
from ui.dialog          import ShowErrorDialog
from ui.layout          import BoxSizer
from ui.manual          import ManPage
from ui.notebook        import MultiTemplate
from ui.prompt          import TextEntryDialog
from wiz.helper         import GetMainWindow
from wiz.wizard         import WizardPage


## Manual pages page
class Page(WizardPage):
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        WizardPage.__init__(self, parent, pgid.MAN)
        
        ## Override default label
        self.Label = GT(u'Manual Pages')
        
        self.Tabs = MultiTemplate(self, ManPage)
        
        self.Tabs.RenameButton(btnid.ADD, GT(u'Add Manual'))
        self.Tabs.RenameButton(btnid.RENAME, GT(u'Rename Manual'))
        self.Tabs.AddTabButton(GT(u'Switch Mode'), u'mode', btnid.MODE, self.OnChangeMode)
        
        # FIXME: Call after new page added???
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.Tabs, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Check if title is okay for manpage target filename
    #
    #  \param title
    #    New <b><i>string</i></b> title to be checked for whitespace & tabs
    #  \return
    #    <b><i>True</i></b> if title is okay to use
    def _title_is_ok(self, title):
        if TextIsEmpty(title):
            return False
        
        return not Contains(title, (u' ', u'\t',))
    
    
    ## Adds a new tab representing a manual page
    #
    #  \param name
    #    Title & target output filename to use for manual
    #  \param easyMode
    #    If <b><i>True</i></b>, interface displays multiple fields, otherwise
    #    uses plain text area
    def AddManpage(self, name=u'manual', easyMode=True):
        # Set 'select' argument to True to switch to new manpage
        ret_val = self.Tabs.AddPage(name, ManPage(self.Tabs, name, easyMode), select=True)
        
        # New page should be selected
        #new_page = self.Tabs.GetPage(self.Tabs.GetSelection())
        
        # Set up some event handling for new page
        #new_page.btn_rename.Bind(wx.EVT_BUTTON, self.OnRenamePage)
        
        return ret_val
    
    
    ## Retrieves manpages info for text output
    #
    #  TODO: Nothing here yet
    #
    #  \param getModule
    #    If <b><i>True</i></b>, returns a <b><i>tuple</b></i> of the module name
    #    & page data, otherwise return only page data string
    #  \see wiz.wizard.WizardPage.Get
    def Get(self, getModule=False):
        # TODO:
        page = None
        
        if getModule:
            page = (__name__, page,)
        
        return page
    
    
    ## Retrieves TabsTemplate instance
    def GetTabsTemplate(self):
        return self.Tabs
    
    
    ## Reads & parses page data from a formatted text file
    #
    #  TODO: Define
    #
    #  \param filename
    #    File path to open
    #  \see wiz.wizard.WizardPage.ImportFromFile
    def ImportFromFile(self, filename):
        pass
    
    
    ## Handles event emitted by btn_add
    def OnAddManpage(self, event=None):
        return self.SetTabName()
    
    
    ## Toggles between 'easy' & 'standard' mode
    def OnChangeMode(self, event=None):
        tab = self.Tabs.GetCurrentTab()
        
        if isinstance(tab, ManPage):
            easy_mode = tab.InEasyMode()
            
            tab.SetMode(not easy_mode)
            
            return tab.InEasyMode() != easy_mode
    
    
    ## Handles event emitting when a tab is being closed
    #
    #  TODO: Define
    def OnCloseTab(self, event=None):
        Logger.Debug(__name__, u'Closing tab')
    
    
    ## Passes event to ui.notebook.TabsTemplate.OnRenameTab
    def OnRenameTab(self, event=None):
        self.Tabs.OnRenameTab(event)
    
    
    ## Either renames an existing page or creates a new one
    #
    #  \param index
    #    Page index to rename (only used if 'rename' is True)
    #  \param rename
    #    Renames an existing page instead of creating a new one
    #  \return
    #    Value of wizbin.manuals.Page.AddManpage or wizbin.manuals.Page.Tabs.SetPageText
    def SetTabName(self, index=-1, rename=False):
        getname = TextEntryDialog(GetMainWindow(), GT(u'Name for new manpage'))
        new_title = None
        
        if not rename:
            easy_mode = CheckBox(getname, label=u'Easy mode', defaultValue=True)
            
            sizer = getname.GetSizer()
            insert_point = len(sizer.GetChildren()) - 1
            
            sizer.InsertSpacer(insert_point, 5)
            sizer.Insert(insert_point + 1, easy_mode, 0, wx.LEFT, 16)
            
            getname.SetSize(sizer.GetMinSize())
            getname.Fit()
            getname.CenterOnParent()
        
        valid_name = False
        
        while not valid_name:
            if new_title and TextIsEmpty(new_title):
                getname.Clear()
            
            # User cancelled
            if not ShowDialog(getname):
                return False
            
            else:
                new_title = getname.GetValue()
            
            valid_name = self._title_is_ok(new_title)
            
            if valid_name:
                break
            
            ShowErrorDialog(GT(u'Manpage name cannot contain whitespace'), warn=True)
        
        if rename:
            if index < 0:
                return False
            
            return self.Tabs.SetPageText(index, new_title)
        
        return self.AddManpage(new_title, easy_mode.GetValue())
