# -*- coding: utf-8 -*-

## \package wiz_bin.man


import wx
from wx.aui import EVT_AUINOTEBOOK_PAGE_CLOSE

from dbr.containers         import Contains
from dbr.language           import GT
from dbr.log                import Logger
from globals                import ident
from globals.ident          import manid
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetTopWindow
from ui.button              import ButtonAdd
from ui.button              import ButtonBrowse64
from ui.button              import ButtonPreview64
from ui.button              import ButtonSave64
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.mansect             import DEFAULT_MANSECT_STYLE
from ui.mansect             import ManBanner
from ui.mansect             import ManPanel
from ui.mansect             import ManSect
from ui.menu                import PanelMenu
from ui.menu                import PanelMenuBar
from ui.notebook            import Notebook
from ui.panel               import ScrolledPanel
from ui.prompt              import TextEntryDialog
from ui.wizard              import WizardPage


## Manual pages page
class Panel(WizardPage):
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        WizardPage.__init__(self, parent, ident.MAN)
        
        ## Override default label
        self.label = GT(u'Manual Pages')
        
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
        lyt_add.Add(wx.StaticText(self, label=GT(u'Add manual')), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
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
        ret_val = self.tabs.AddPage(name, ManPage(self.tabs, name), select=True)
        
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
class ManPage(wx.Panel):
    def __init__(self, parent, name=u'manual'):
        wx.Panel.__init__(self, parent, name=name)
        
        # Add sibling panel to hold menu & rename button
        pnl_top = wx.Panel(self)
        pnl_top.SetBackgroundColour(wx.BLUE)
        
        # FIXME: wx.Panel can't set wx.MenuBar
        # TODO: Create custom menubar
        menubar = PanelMenuBar(pnl_top)
        menubar.AddItem(PanelMenu(pnl_top, wx.ID_ADD), GT(u'Add'))
        
        self.btn_rename = wx.Button(pnl_top, label=GT(u'Rename'))
        
        self.pnl_bottom = ScrolledPanel(self)
        
        # *** Banners *** #
        
        txt_banners = wx.StaticText(self.pnl_bottom, label=GT(u'Banners'))
        banners = ManBanner(self.pnl_bottom)
        pnl_banners = banners.GetPanel()
        
        #FIXME: Replace buttons with drop-down menu
        btn_single_line = ButtonAdd(self.pnl_bottom, ident.SINGLE)
        txt_single_line = wx.StaticText(self.pnl_bottom, label=GT(u'Add single line section'))
        
        btn_multi_line = ButtonAdd(self.pnl_bottom, manid.MULTILINE)
        txt_multi_line = wx.StaticText(self.pnl_bottom, label=GT(u'Add multi-line section'))
        
        # *** Event Handling *** #
        
        btn_single_line.Bind(wx.EVT_BUTTON, self.OnAddDocumentSection)
        btn_multi_line.Bind(wx.EVT_BUTTON, self.OnAddDocumentSection)
        
        # *** Layout *** #
        
        lyt_top = BoxSizer(wx.VERTICAL)
        lyt_top.Add(menubar, 0, wx.EXPAND)
        lyt_top.Add(self.btn_rename, 0, wx.LEFT|wx.TOP, 5)
        
        pnl_top.SetAutoLayout(True)
        pnl_top.SetSizer(lyt_top)
        
        lyt_button = BoxSizer(wx.HORIZONTAL)
        lyt_button.Add(btn_single_line)
        lyt_button.Add(txt_single_line, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        lyt_button.Add(btn_multi_line, 0, wx.LEFT, 5)
        lyt_button.Add(txt_multi_line, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        # FIXME: Use GridBagSizer???
        lyt_bottom = BoxSizer(wx.VERTICAL)
        lyt_bottom.Add(txt_banners, 0, wx.ALIGN_BOTTOM|wx.LEFT|wx.TOP, 5)
        lyt_bottom.Add(pnl_banners, 0, wx.LEFT, 5)
        lyt_bottom.Add(lyt_button, 0, wx.LEFT|wx.TOP, 5)
        lyt_bottom.AddStretchSpacer(1)
        
        self.pnl_bottom.SetAutoLayout(True)
        self.pnl_bottom.SetSizer(lyt_bottom)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(pnl_top, 0, wx.EXPAND)
        lyt_main.Add(self.pnl_bottom, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        
        # *** Default Sections *** #
        
        # This calls self.Layout
        self.AddDocumentSection(GT(u'Name'))
        self.AddDocumentSection(GT(u'Synopsis'))
        self.AddDocumentSection(GT(u'Description'))
        self.AddDocumentSection(GT(u'Examples'))
        self.AddDocumentSection(GT(u'See also'))
    
    
    ## Retrieves the section index that contains the object
    #  
    #  \param item
    #    Object instance to search for
    #  \return
    #    \b \e Integer index of the item or -1
    def _get_object_section(self, item):
        index = 0
        
        for C1 in self.pnl_bottom.GetSizer().GetChildren():
            C1 = C1.GetWindow()
            
            if isinstance(C1, ManPanel):
                for C2 in C1.GetChildren():
                    if C2 == item:
                        return index
            
            index += 1
        
        return None
    
    
    ## Adds a new section to the document
    def AddDocumentSection(self, section_name=None, style=DEFAULT_MANSECT_STYLE):
        doc_section = ManSect(self.pnl_bottom, section_name, style=style)
        obj_section = doc_section.GetObject()
        
        if not obj_section:
            return False
        
        if doc_section.HasStyle(manid.CHOICE|manid.MUTABLE):
            labels = (
                GT(u'Name'),
                GT(u'Synopsis'),
                GT(u'Configuration'),
                GT(u'Description'),
                GT(u'Options'),
                GT(u'Exit status'),
                GT(u'Return value'),
                GT(u'Errors'),
                GT(u'Environment'),
                GT(u'Files'),
                GT(u'Versions'),
                GT(u'Conforming to'),
                GT(u'Notes'),
                GT(u'Bugs'),
                GT(u'Examples'),
                GT(u'See also')
                )
            
            doc_section.Label.Set(labels)
            
            if section_name:
                doc_section.Label.SetStringSelection(section_name)
            
            if not doc_section.Label.GetSelection():
                doc_section.Label.SetSelection(0)
        
        if doc_section.HasStyle(manid.REMOVABLE):
            # FIXME: Replace with checkboxes
            btn_remove = doc_section.GetButton()
            if btn_remove:
                btn_remove.Bind(wx.EVT_BUTTON, self.OnRemoveDocumentSection)
        
        proportion = 0
        if doc_section.HasStyle(manid.MULTILINE):
            # FIXME: Proportion for multilines is not any bigger
            proportion = 2
        
        FLAGS = wx.LEFT|wx.RIGHT|wx.TOP
        
        layout = self.pnl_bottom.GetSizer()
        layout.AddKeepLast(obj_section, proportion, wx.EXPAND|FLAGS, 5)
        
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
        style = DEFAULT_MANSECT_STYLE
        
        if event:
            if event.GetEventObject().GetId() == manid.MULTILINE:
                style = style|manid.MULTILINE
        
        self.AddDocumentSection(style=style)
    
    
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
    
    
    ## Removes selected section from manpage document
    #  
    #  \return
    #    \b \e True if section elements were removed
    def RemoveDocumentSection(self, index):
        if index == None:
            Logger.Error(__name__, u'Cannot remove desired index')
            
            return False
        
        Logger.Debug(__name__, u'Removing manpage section at index {}'.format(index))
        
        layout = self.pnl_bottom.GetSizer()
        
        object_to_remove = layout.GetItem(index).GetWindow()
        
        # Object was returned as wx.Window instance
        if object_to_remove:
            layout.Detach(object_to_remove)
            object_to_remove.Destroy()
            
            self.Layout()
            
            return True
        
        return False
