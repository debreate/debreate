# -*- coding: utf-8 -*-

## \package wiz_bin.man


import wx
from wx.aui import AUI_NB_CLOSE_BUTTON
from wx.aui import AUI_NB_TAB_MOVE
from wx.aui import AUI_NB_TAB_SPLIT
from wx.aui import AuiNotebook
from wx.aui import EVT_AUINOTEBOOK_PAGE_CLOSE

from dbr.buttons            import ButtonAdd
from dbr.buttons            import ButtonBrowse64
from dbr.buttons            import ButtonPreview64
from dbr.buttons            import ButtonSave64
from dbr.dialogs            import ConfirmationDialog
from dbr.language           import GT
from dbr.log                import Logger
from dbr.mansect            import ManSectName
from dbr.mansect            import ManSectSynopsis
from dbr.menu               import PanelMenu
from dbr.menu               import PanelMenuBar
from dbr.wizard             import WizardPage
from globals                import ident
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetTopWindow


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        WizardPage.__init__(self, parent, ident.MAN)
        
        ## Override default label
        self.label = GT(u'Man Pages')
        
        btn_add = ButtonAdd(self)
        btn_add.SetName(u'add')
        
        # Import/Export/Preview
        btn_browse = ButtonBrowse64(self)
        btn_save = ButtonSave64(self)
        btn_preview = ButtonPreview64(self)
        
        self.tabs = AuiNotebook(self, style=AUI_NB_TAB_SPLIT|AUI_NB_TAB_MOVE|AUI_NB_CLOSE_BUTTON)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        btn_add.Bind(wx.EVT_BUTTON, self.OnAddManpage)
        
        self.tabs.Bind(EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnCloseTab)
        
        # *** Layout *** #
        
        lyt_add = wx.BoxSizer(wx.HORIZONTAL)
        lyt_add.Add(btn_add, 0)
        lyt_add.Add(wx.StaticText(self, label=GT(u'Add manpage')), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(lyt_add, 0, wx.ALIGN_BOTTOM)
        lyt_buttons.AddStretchSpacer(1)
        lyt_buttons.Add(btn_browse, 0)
        lyt_buttons.Add(btn_save, 0, wx.LEFT, 5)
        lyt_buttons.Add(btn_preview, 0, wx.LEFT, 5)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(lyt_buttons, 0, wx.EXPAND|wx.ALL, 5)
        lyt_main.Add(self.tabs, 1, wx.ALL|wx.EXPAND, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def AddManpage(self, name=u'manual'):
        self.tabs.AddPage(ManPage(self.tabs, name), name)
    
    
    ## Retrieves manpages info for text output
    #  
    #  TODO: Nothing here yet
    def Get(self, get_module=False):
        # TODO:
        page = None
        
        if get_module:
            page = (__name__, page,)
        
        return page
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
        pass
    
    
    ## TODO: Doxygen
    def OnAddManpage(self, event=None):
        main_window = GetTopWindow()
        
        getname = wx.TextEntryDialog(main_window, GT(u'Name for new manpage'))
        
        # FIXME: Better way to do this?
        invalid_name = True
        while invalid_name:
            if getname.ShowModal() == wx.ID_OK:
                name = getname.GetValue()
                invalid_name = False
                
                # FIXME: support unicode characters
                for C in name:
                    if not C.isalnum():
                        invalid_name = True
                        wx.MessageDialog(main_window, GT(u'Invalid characters found in name'), GT(u'Error'),
                            style=wx.OK|wx.ICON_ERROR).ShowModal()
                        break
                
                if not invalid_name:
                    self.AddManpage(name)
            
            invalid_name = False
    
    
    ## TODO: Doxygen
    def Reset(self):
        pass
    
    
    ## Show a confirmation dialog when closing a tab
    def OnCloseTab(self, event=None):
        if not TextIsEmpty(self.tabs.CurrentPage.GetValue()):
            if not ConfirmationDialog(GetTopWindow(), GT(u'Close Tab'),
                    GT(u'Are you sure you want to close this tab?')).Confirmed():
                if event:
                    event.Veto()


## TODO: Doxygen
class ManPage(ScrolledPanel):
    def __init__(self, parent, name=u'manual'):
        wx.ScrolledWindow.__init__(self, parent, style=wx.VSCROLL, name=name)
        
        # List of sections & definitions
        self.sections = {
            u'1': GT(u'General commands'),
            u'2': GT(u'System calls'),
            u'3': GT(u'Library functions'),
            u'4': GT(u'Special files and drivers'),
            u'5': GT(u'File formats and conventions'),
            u'6': GT(u'Games and screensavers'),
            u'7': GT(u'Miscellanea'),
            u'8': GT(u'System administration commands and daemons'),
        }
        
        # FIXME: wx.Panel can't set wx.MenuBar
        # TODO: Create custom menubar
        menubar = PanelMenuBar(self)
        menubar.Add(PanelMenu(), GT(u'Add'))
        
        txt_section = wx.StaticText(self, label=GT(u'Section'))
        
        self.sel_section = wx.Choice(self, choices=tuple(self.sections))
        self.sel_section.default = u'1'
        self.sel_section.SetStringSelection(self.sel_section.default)
        
        self.label_section = wx.StaticText(self, label=self.sections[self.sel_section.default])
        
        # *** Event Handling *** #
        
        self.sel_section.Bind(wx.EVT_CHOICE, self.OnSetSection)
        
        # *** Layout *** #
        
        lyt_title = wx.BoxSizer(wx.HORIZONTAL)
        lyt_title.Add(txt_section, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        lyt_title.Add(self.sel_section, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        lyt_title.Add(self.label_section, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(menubar, 0, wx.EXPAND)
        lyt_main.Add(lyt_title, 0, wx.LEFT|wx.TOP, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Get manpage section & contents
    def Get(self):
        return (self.GetSection(), self.GetValue(),)
    
    
    ## Get the manpage section number
    def GetSection(self):
        return self.sel_section.GetStringSelection()
    
    
    ## Get the contents of manpage
    def GetValue(self):
        return self.ti_man.GetValue()
    
    
    ## Adds a new section to the document via button press
    def OnAddDocumentSection(self, event=None):
        self.AddDocumentSection(expand=True)
    
    
    ## TODO: Doxygen
    def OnSetSection(self, event=None):
        self.SetSectionLabel(self.sel_section.GetStringSelection())
    
    
    ## Updates the label for the current section
    def SetSectionLabel(self, section):
        if section in self.sections:
            Logger.Debug(__name__, u'Setting section to {}'.format(section))
            
            self.label_section.SetLabel(self.sections[section])
            return True
        
        return False
