# -*- coding: utf-8 -*-

## \package ui.manual

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language           import GT
from dbr.log                import Logger
from globals                import ident
from globals.ident          import manid
from globals.ident          import pgid
from globals.wizardhelper   import GetPage
from input.text             import TextAreaPanel
from ui.button              import ButtonBrowse
from ui.button              import ButtonPreview
from ui.button              import ButtonSave
from ui.layout              import BoxSizer
from ui.mansect             import DEFAULT_MANSECT_STYLE
from ui.mansect             import ManBanner
from ui.mansect             import ManPanel
from ui.mansect             import ManSect
from ui.menu                import PanelMenu
from ui.menu                import PanelMenuBar
from ui.panel               import BorderedPanel
from ui.panel               import ScrolledPanel


## TODO: Doxygen
class ManPage(wx.Panel):
    def __init__(self, parent, name=u'manual', easy_mode=True):
        wx.Panel.__init__(self, parent, name=name)
        
        # False is 'manual', True is 'easy'
        self.SetMode(easy_mode)
    
    
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
            event_object = event.GetEventObject()
            
            if isinstance(event_object, wx.Menu):
                event_id = event.GetId()
            
            else:
                event_id = event_object.GetId()
            
            if event_id == manid.MULTILINE:
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
    
    
    ## TODO: Doxygen
    def SetMode(self, mode):
        print(u'\nDEBUG: SetMode')
        print(u'  Parent instance: {}'.format(type(self.Parent)))
        
        if isinstance(mode, wx.CommandEvent):
            mode = mode.GetEventObject().Mode
        
        # Restart with fresh panel
        self.DestroyChildren()
        
        btn_rename = wx.Button(self, label=GT(u'Rename'))
        btn_mode = wx.Button(self, label=GT(u'Switch mode'))
        btn_mode.Mode = not mode
        
        # Import/Export/Preview
        btn_browse = ButtonBrowse(self)
        btn_save = ButtonSave(self)
        btn_preview = ButtonPreview(self)
        
        btn_rename.Bind(wx.EVT_BUTTON, GetPage(pgid.MAN).OnRenameTab)
        btn_mode.Bind(wx.EVT_BUTTON, self.SetMode)
        
        # *** Layout *** #
        
        self.lyt_buttons = BoxSizer(wx.HORIZONTAL)
        self.lyt_buttons.Add(btn_rename, 0, wx.ALIGN_TOP)
        self.lyt_buttons.Add(btn_mode, 0, wx.ALIGN_TOP|wx.LEFT, 5)
        self.lyt_buttons.AddStretchSpacer(1)
        self.lyt_buttons.Add(btn_browse)
        self.lyt_buttons.Add(btn_save)
        self.lyt_buttons.Add(btn_preview)
        
        self.lyt_main = BoxSizer(wx.VERTICAL)
        
        if mode:
            return self.SetModeEasy()
        
        return self.SetModeManual()
    
    
    ## TODO: Doxygen
    def SetModeEasy(self):
        # Add sibling panel to hold menu & rename button
        pnl_top = wx.Panel(self)
        
        for C in self.GetChildren():
            if isinstance(C, wx.Button):
                C.Reparent(pnl_top)
        
        # FIXME: Hack
        temp_bar = BorderedPanel(pnl_top)
        
        menubar = PanelMenuBar(temp_bar)
        menubar.HideBorder()
        
        menu_add = PanelMenu(menubar, label=GT(u'Add'))
        menu_add.Append(ident.SINGLE, GT(u'Single line section'))
        menu_add.Append(manid.MULTILINE, GT(u'Multi-line section'))
        
        menubar.AddItem(menu_add)
        
        self.pnl_bottom = ScrolledPanel(self)
        
        # *** Banners *** #
        
        txt_banners = wx.StaticText(self.pnl_bottom, label=GT(u'Banners'))
        banners = ManBanner(self.pnl_bottom)
        pnl_banners = banners.GetPanel()
        
        # *** Event Handling *** #
        
        wx.EVT_MENU(self, ident.SINGLE, self.OnAddDocumentSection)
        wx.EVT_MENU(self, manid.MULTILINE, self.OnAddDocumentSection)
        
        # *** Layout *** #
        
        # FIXME: Hack
        temp_lyt = BoxSizer(wx.HORIZONTAL)
        temp_lyt.Add(menubar)
        temp_lyt.AddStretchSpacer(1)
        
        temp_bar.SetSizer(temp_lyt)
        
        lyt_top = BoxSizer(wx.VERTICAL)
        lyt_top.Add(self.lyt_buttons, 0, wx.EXPAND|wx.ALL, 5)
        # FIXME: temp_bar height is initially wrong
        lyt_top.Add(temp_bar, 0, wx.EXPAND|wx.ALL, 5)
        
        pnl_top.SetAutoLayout(True)
        pnl_top.SetSizer(lyt_top)
        
        # FIXME: Use GridBagSizer???
        lyt_bottom = BoxSizer(wx.VERTICAL)
        lyt_bottom.Add(txt_banners, 0, wx.ALIGN_BOTTOM|wx.LEFT|wx.TOP, 5)
        lyt_bottom.Add(pnl_banners, 0, wx.LEFT, 5)
        lyt_bottom.AddStretchSpacer(1)
        
        self.pnl_bottom.SetAutoLayout(True)
        self.pnl_bottom.SetSizer(lyt_bottom)
        
        self.lyt_main.Add(pnl_top, 0, wx.EXPAND)
        self.lyt_main.Add(self.pnl_bottom, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.lyt_main)
        
        # *** Default Sections *** #
        
        # This calls self.Layout
        self.AddDocumentSection(GT(u'Name'))
        self.AddDocumentSection(GT(u'Synopsis'), style=DEFAULT_MANSECT_STYLE|manid.MULTILINE)
        self.AddDocumentSection(GT(u'Description'), style=DEFAULT_MANSECT_STYLE|manid.MULTILINE)
        self.AddDocumentSection(GT(u'Options'), style=DEFAULT_MANSECT_STYLE|manid.MULTILINE)
        self.AddDocumentSection(GT(u'Examples'), style=DEFAULT_MANSECT_STYLE|manid.MULTILINE)
        self.AddDocumentSection(GT(u'See also'))
    
    
    ## TODO: Doxygen
    def SetModeManual(self):
        self.ManualText = TextAreaPanel(self)
        
        # *** Layout *** #
        
        self.lyt_main.Add(self.lyt_buttons, 0, wx.EXPAND|wx.ALL, 5)
        self.lyt_main.Add(self.ManualText, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.lyt_main)
        self.Layout()
