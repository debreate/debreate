# -*- coding: utf-8 -*-

## \package wizbin.manuals

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.containers         import Contains
from dbr.language           import GT
from dbr.log                import Logger
from globals.ident          import btnid
from globals.ident          import pgid
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetMainWindow
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.manual              import ManPage
from ui.notebook            import MultiTemplate
from ui.prompt              import TextEntryDialog
from wiz.wizard             import WizardPage


## Manual pages page
class Page(WizardPage):
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        WizardPage.__init__(self, parent, pgid.MAN)
        
        ## Override default label
        self.label = GT(u'Manual Pages')
        
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
    #    New \b \e string title to be checked for whitespace & tabs
    #  \return
    #    \b \e True if title is okay to use
    def _title_is_ok(self, title):
        if TextIsEmpty(title):
            return False
        
        return not Contains(title, (u' ', u'\t',))
    
    
    ## TODO: Doxygen
    def AddManpage(self, name=u'manual', easy_mode=True):
        # Set 'select' argument to True to switch to new manpage
        ret_val = self.Tabs.AddPage(name, ManPage(self.Tabs, name, easy_mode), select=True)
        
        # New page should be selected
        #new_page = self.Tabs.GetPage(self.Tabs.GetSelection())
        
        # Set up some event handling for new page
        #new_page.btn_rename.Bind(wx.EVT_BUTTON, self.OnRenamePage)
        
        return ret_val
    
    
    ## Retrieves manpages info for text output
    #  
    #  TODO: Nothing here yet
    def Get(self, getModule=False):
        # TODO:
        page = None
        
        if getModule:
            page = (__name__, page,)
        
        return page
    
    
    ## Retrieves TabsTemplate instance
    def GetTabsTemplate(self):
        return self.Tabs
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
        pass
    
    
    ## TODO: Doxygen
    def OnAddManpage(self, event=None):
        return self.SetTabName()
    
    
    ## TODO: Doxygen
    def OnChangeMode(self, event=None):
        tab = self.Tabs.GetCurrentTab()
        
        if isinstance(tab, ManPage):
            easy_mode = tab.InEasyMode()
            
            tab.SetMode(not easy_mode)
            
            return tab.InEasyMode() != easy_mode
    
    
    ## TODO: Doxygen
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
    def SetTabName(self, index=-1, rename=False):
        getname = TextEntryDialog(GetMainWindow(), GT(u'Name for new manpage'))
        new_title = None
        
        if not rename:
            easy_mode = wx.CheckBox(getname, label=u'Easy mode')
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
