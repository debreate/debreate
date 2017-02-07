# -*- coding: utf-8 -*-

## \package wizbin.launchers

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from globals.ident      import btnid
from globals.ident      import inputid
from globals.ident      import listid
from globals.ident      import pgid
from globals.tooltips   import SetPageToolTips
from ui.launcher        import LauncherTemplate
from ui.layout          import BoxSizer
from ui.notebook        import MultiTemplate
from wiz.wizard         import WizardPage


## Page for creating a system launchers
class Page(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.LAUNCHERS)
        
        ## Override default label
        self.label = GT(u'Menu Launchers')
        
        self.IgnoreResetIds = [
            inputid.OTHER,
            listid.CAT,
            ]
        
        templates = MultiTemplate(self, LauncherTemplate)
        
        templates.RenameButton(btnid.ADD, GT(u'Add Launcher'))
        templates.RenameButton(btnid.RENAME, GT(u'Rename Launcher'))
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        wx.EVT_BUTTON(self, wx.ID_ADD, self.OnAddTab)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(templates, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Retrieves data from all launchers
    #
    #  TODO: Define
    def Get(self, getModule=False):
        pass
    
    
    ## Updates tooltips for new tab
    def OnAddTab(self, event=None):
        SetPageToolTips(self)
