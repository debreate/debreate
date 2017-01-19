# -*- coding: utf-8 -*-

## \package wiz_bin.man


import wx
from wx.aui import EVT_AUINOTEBOOK_PAGE_CLOSE

from dbr.buttons            import ButtonAdd
from dbr.buttons            import ButtonBrowse64
from dbr.buttons            import ButtonPreview64
from dbr.buttons            import ButtonSave64
from dbr.containers         import Contains
from dbr.dialogs            import ShowDialog
from dbr.dialogs            import ShowErrorDialog
from dbr.language           import GT
from dbr.log                import Logger
from dbr.mansect            import ManBanner
from dbr.mansect            import ManSection
from dbr.menu               import PanelMenu
from dbr.menu               import PanelMenuBar
from dbr.textinput          import TextEntryDialog
from dbr.wizard             import WizardPage
from globals                import ident
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetTopWindow
from ui.layout              import BoxSizer
from ui.notebook            import Notebook
from ui.panel               import BorderedPanel
from ui.panel               import ScrolledPanel


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
        
        self.tabs = Notebook(self)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        btn_add.Bind(wx.EVT_BUTTON, self.OnAddManpage)
        
        self.tabs.Bind(EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnCloseTab)
        
        # *** Layout *** #
        
        lyt_add = BoxSizer(wx.HORIZONTAL)
        lyt_add.Add(btn_add, 0)
        lyt_add.Add(wx.StaticText(self, label=GT(u'Add manpage')), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(lyt_add, 0, wx.ALIGN_BOTTOM)
        lyt_buttons.AddStretchSpacer(1)
        lyt_buttons.Add(btn_browse, 0)
        lyt_buttons.Add(btn_save, 0, wx.LEFT, 5)
        lyt_buttons.Add(btn_preview, 0, wx.LEFT, 5)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(lyt_buttons, 0, wx.EXPAND|wx.ALL, 5)
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
    def AddManpage(self, name=u'manual'):
        # Set 'select' argument to True to switch to new manpage
        ret_val = self.tabs.AddPage(ManPage(self.tabs, name), name, select=True)
        
        # New page should be selected
        new_page = self.tabs.GetPage(self.tabs.GetSelection())
        
        # Set up some event handling for new page
        new_page.btn_rename.Bind(wx.EVT_BUTTON, self.OnRenamePage)
        
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
    
    
    ## Rename tab & manpage
    def OnRenamePage(self, event=None):
        index = self.tabs.GetSelection()
        
        return self.SetPageName(index, rename=True)
    
    
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
        getname = TextEntryDialog(GetTopWindow(), GT(u'Name for new manpage'))
        new_name = None
        
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
        
        return self.AddManpage(new_name)


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
        
        self.btn_rename = wx.Button(self, label=GT(u'Rename'))
        
        # *** Banners *** #
        
        txt_banners = wx.StaticText(self, label=GT(u'Banners'))
        pnl_banners = BorderedPanel(self)
        
        txt_section = wx.StaticText(pnl_banners, label=GT(u'Section'))
        
        self.sel_section = wx.Choice(pnl_banners, choices=tuple(self.sections))
        self.sel_section.default = u'1'
        self.sel_section.SetStringSelection(self.sel_section.default)
        
        # Section description that changes with EVT_CHOICE
        self.label_section = wx.StaticText(pnl_banners, label=self.sections[self.sel_section.default])
        
        #FIXME: Replace buttons with drop-down menu
        btn_single_line = ButtonAdd(self, ident.SINGLE)
        txt_single_line = wx.StaticText(self, label=GT(u'Add single line section'))
        
        btn_multi_line = ButtonAdd(self, ident.MULTI)
        txt_multi_line = wx.StaticText(self, label=GT(u'Add multi-line section'))
        
        # *** Event Handling *** #
        
        self.sel_section.Bind(wx.EVT_CHOICE, self.OnSetSection)
        
        btn_single_line.Bind(wx.EVT_BUTTON, self.OnAddDocumentSection)
        btn_multi_line.Bind(wx.EVT_BUTTON, self.OnAddDocumentSection)
        
        # *** Layout *** #
        
        lyt_section = BoxSizer(wx.HORIZONTAL)
        lyt_section.Add(txt_section, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        lyt_section.Add(self.sel_section, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        lyt_section.Add(self.label_section, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        
        lyt_banners = BoxSizer(wx.VERTICAL)
        lyt_banners.Add(lyt_section, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)
        lyt_banners.Add(ManBanner(pnl_banners).GetObject(), 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        pnl_banners.SetAutoLayout(True)
        pnl_banners.SetSizer(lyt_banners)
        
        lyt_button = BoxSizer(wx.HORIZONTAL)
        lyt_button.Add(btn_single_line)
        lyt_button.Add(txt_single_line, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        lyt_button.Add(btn_multi_line, 0, wx.LEFT, 5)
        lyt_button.Add(txt_multi_line, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        # FIXME: Use GridBagSizer???
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(menubar, 0, wx.EXPAND)
        lyt_main.Add(self.btn_rename, 0, wx.LEFT|wx.TOP, 5)
        lyt_main.Add(txt_banners, 0, wx.ALIGN_BOTTOM|wx.LEFT|wx.TOP, 5)
        lyt_main.Add(pnl_banners, 0, wx.LEFT, 5)
        lyt_main.Add(lyt_button, 0, wx.LEFT|wx.TOP, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        self.AddDocumentSection(GT(u'Name'), static=True, expand=False, removable=False)
    
    
    ## Retrieves the section index that contains the object
    #  
    #  \param item
    #    Object instance to search for
    #  \return
    #    \b \e Integer index of the item or -1
    def _get_object_section(self, item):
        index = -1
        
        for C1 in self.GetSizer().GetChildren():
            index += 1
            
            C1 = C1.GetSizer()
            
            if isinstance(C1, wx.Sizer):
                for C2 in C1.GetChildren():
                    C2 = C2.GetWindow()
                    
                    if C2 == item:
                        return index
        
        return None
    
    
    ## Adds a new section to the document
    def AddDocumentSection(self, section_name=None, multiline=False, static=False, expand=False,
                removable=True):
        doc_section = ManSection(self)
        sect_sizer = doc_section.GetObject(section_name, multiline, static, expand, removable)
        
        if not sect_sizer:
            return False
        
        FLAGS = wx.LEFT|wx.RIGHT|wx.TOP
        if expand:
            FLAGS = wx.EXPAND|FLAGS
        
        main_sizer = self.GetSizer()
        
        if removable:
            # FIXME: Replace with checkboxes
            btn_remove = doc_section.GetButton()
            if btn_remove:
                btn_remove.Bind(wx.EVT_BUTTON, self.OnRemoveDocumentSection)
        
        main_sizer.Add(sect_sizer, 0, FLAGS, 5)
        
        self.Layout()
        
        return True
    
    
    ## Get manpage section & contents
    def Get(self):
        return (self.GetSection(), self.GetValue(),)
    
    
    ## Get the manpage section number
    def GetSection(self):
        return self.sel_section.GetStringSelection()
    
    
    ## Adds a new section to the document via button press
    def OnAddDocumentSection(self, event=None):
        multiline = False
        
        if event:
            multiline = event.GetEventObject().GetId() == ident.MULTI
        
        self.AddDocumentSection(multiline=multiline, expand=True, removable=True)
    
    
    ## Show a confirmation dialog when closing a tab
    #  
    #  FIXME: Find children & check default values
    def OnCloseTab(self, event=None):
        pass
    
    
    ## Removes selected section from manpage document via button press
    #  
    #  \return
    #    \b \e True if section elements were removed
    def OnRemoveDocumentSection(self, event=None, index=None):
        if event:
            index = self._get_object_section(event.GetEventObject())
        
        return self.RemoveDocumentSection(index)
    
    
    ## TODO: Doxygen
    def OnSetSection(self, event=None):
        self.SetSectionLabel(self.sel_section.GetStringSelection())
    
    
    ## Removes selected section from manpage document
    #  
    #  \return
    #    \b \e True if section elements were removed
    def RemoveDocumentSection(self, index):
        if index == None:
            Logger.Error(__name__, u'Cannot remove desired index')
            
            return False
        
        Logger.Debug(__name__, u'Removing manpage section at index {}'.format(index))
        
        sizer_to_remove = self.GetSizer().GetItem(index).GetSizer()
        
        # Object was returned as sizer
        if sizer_to_remove:
            self.GetSizer().Detach(sizer_to_remove)
            sizer_to_remove.Clear(True)
            sizer_to_remove.Destroy()
            
            self.Layout()
            
            return True
        
        return False
    
    
    ## Updates the label for the current section
    def SetSectionLabel(self, section):
        if section in self.sections:
            Logger.Debug(__name__, u'Setting section to {}'.format(section))
            
            self.label_section.SetLabel(self.sections[section])
            return True
        
        return False
