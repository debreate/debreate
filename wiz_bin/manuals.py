# -*- coding: utf-8 -*-

## \package wiz_bin.manuals

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.containers         import Contains
from dbr.language           import GT
from dbr.log                import Logger
from globals.ident          import pgid
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetMainWindow
from ui.button              import ButtonBrowse64
from ui.button              import ButtonPreview64
from ui.button              import ButtonSave64
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.manual              import ManPage
from ui.notebook            import TabsTemplate
from ui.prompt              import TextEntryDialog
from ui.wizard              import WizardPage


## Manual pages page
class Panel(WizardPage):
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        WizardPage.__init__(self, parent, pgid.MAN)
        
        ## Override default label
        self.label = GT(u'Manual Pages')
        
        self.tabs = TabsTemplate(self, ManPage)
        
        # FIXME: Call after new page added???
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.tabs, 1, wx.ALL|wx.EXPAND, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Check if name is okay for manpage filename
    def _name_is_ok(self, name):
        if TextIsEmpty(name):
            return False
        
        return not Contains(name, (u' ', u'\t',))
    
    
    ## TODO: Doxygen
    def AddManpage(self, name=u'manual', easy_mode=True):
        # Set 'select' argument to True to switch to new manpage
        ret_val = self.tabs.AddPage(name, ManPage(self.tabs, name, easy_mode), select=True)
        
        # New page should be selected
        #new_page = self.tabs.GetPage(self.tabs.GetSelection())
        
        # Set up some event handling for new page
        #new_page.btn_rename.Bind(wx.EVT_BUTTON, self.OnRenamePage)
        
        return ret_val
    
    
    ## Retrieves manpages info for text output
    #  
    #  TODO: Nothing here yet
    def Get(self, get_module=False):
        # TODO:
        page = None
        
        if get_module:
            page = (__name__, page,)
        
        return page
    
    
    ## Retrieves TabsTemplate instance
    def GetTabsTemplate(self):
        return self.tabs
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
        pass
    
    
    ## TODO: Doxygen
    def OnAddManpage(self, event=None):
        return self.SetPageName()
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Define
    def OnCloseTab(self, event=None):
        Logger.Debug(__name__, u'Closing tab')
    
    
    ## Removes all tabs & sets page to default values
    def Reset(self):
        self.tabs.DeleteAllPages()
    
    
    ## Either renames an existing page or creates a new one
    #  
    #  \param index
    #    Page index to rename (only used if 'rename' is True)
    #  \param rename
    #    Renames an existing page instead of creating a new one
    def SetPageName(self, index=-1, rename=False):
        getname = TextEntryDialog(GetMainWindow(), GT(u'Name for new manpage'))
        new_name = None
        
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
            if new_name and TextIsEmpty(new_name):
                getname.Clear()
            
            # User cancelled
            if not ShowDialog(getname):
                return False
            
            else:
                new_name = getname.GetValue()
            
            valid_name = self._name_is_ok(new_name)
            
            if valid_name:
                break
            
            ShowErrorDialog(GT(u'Manpage name cannot contain whitespace'), warn=True)
        
        if rename:
            if index < 0:
                return False
            
            return self.tabs.SetPageText(index, new_name)
        
        return self.AddManpage(new_name, easy_mode.GetValue())
