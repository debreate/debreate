# -*- coding: utf-8 -*-

# Menu Page


import os, shutil
from wx import \
    BoxSizer as wxBoxSizer, \
    CheckBox as wxCheckBox, \
    Choice as wxChoice, \
    ComboBox as wxComboBox, \
    Dialog as wxDialog, \
    EmptyString as wxEmptyString, \
    FileDialog as wxFileDialog, \
    FlexGridSizer as wxFlexGridSizer, \
    ListCtrl as wxListCtrl, \
    Panel as wxPanel, \
    StaticBox as wxStaticBox, \
    StaticBoxSizer as wxStaticBoxSizer, \
    StaticText as wxStaticText, \
    TextCtrl as wxTextCtrl, \
    ToolTip as wxToolTip, \
    NewId as wxNewId, \
    MessageDialog as wxMessageDialog
from wx import \
    MAJOR_VERSION as wxMAJOR_VERSION, \
    ALL as wxALL, \
    BORDER_SIMPLE as wxBORDER_SIMPLE, \
    BOTTOM as wxBOTTOM, \
    EXPAND as wxEXPAND, \
    HORIZONTAL as wxHORIZONTAL, \
    LC_SINGLE_SEL as wxLC_SINGLE_SEL, \
    LEFT as wxLEFT, \
    RIGHT as wxRIGHT, \
    TE_MULTILINE as wxTE_MULTILINE, \
    TOP as wxTOP, \
    VERTICAL as wxVERTICAL, \
    FD_CHANGE_DIR as wxFD_CHANGE_DIR, \
    FD_OVERWRITE_PROMPT as wxFD_OVERWRITE_PROMPT, \
    FD_SAVE as wxFD_SAVE, \
    EVT_BUTTON as wxEVT_BUTTON, \
    EVT_CHECKBOX as wxEVT_CHECKBOX, \
    EVT_KEY_DOWN as wxEVT_KEY_DOWN, \
    ID_ANY as wxID_ANY, \
    ID_OK as wxID_OK, \
    TE_READONLY as wxTE_READONLY, \
    WXK_ESCAPE as wxWXK_ESCAPE, \
    WXK_NUMPAD_ENTER as wxWXK_NUMPAD_ENTER, \
    WXK_RETURN as wxWXK_RETURN, \
    ID_YES as wxID_YES, \
    YES_NO as wxYES_NO, \
    NO_DEFAULT as wxNO_DEFAULT, \
    ICON_QUESTION as wxICON_QUESTION, \
    WXK_DELETE as wxWXK_DELETE, \
    OK as wxOK, \
    ICON_EXCLAMATION as wxICON_EXCLAMATION

import dbr


ID = wxNewId()

class Panel(wxPanel):
    def __init__(self, parent, id=ID, name=_(u'Menu Launcher')):
        wxPanel.__init__(self, parent, id, name=_(u'Menu Launcher'))
        
        # For identifying page to parent
        #self.ID = u'MENU'
        
        # Allows executing parent methods
        self.parent = parent
        
        # --- Tool Tips --- #
        DF_tip = wxToolTip(_(u'Open launcher file'))
        icon_tip = wxToolTip(_(u'Icon to be displayed for the launcher'))
        m_name_tip = wxToolTip(_(u'Text for the launcher'))
        #m_ver_tip = wxToolTip(u'The version of your application')
        m_com_tip = wxToolTip(_(u'Text displayed when mouse hovers over launcher'))
        m_exec_tip = wxToolTip(_(u'Executable to be launched'))
        m_mime_tip = wxToolTip(_(u'Specifies the MIME types that the application can handle'))
        #m_enc_tip = wxToolTip(u'Specifies the encoding of the desktop entry file')
        #m_type_tip = wxToolTip(_(u'The type of launcher'))
        m_cat_tip = wxToolTip(u'Choose which categories in which you would like your application to be displayed')
        m_term_tip = wxToolTip(_(u'Specifies whether application should be run from a terminal'))
        m_notify_tip = wxToolTip(_(u'Displays a notification in the system panel when launched'))
        m_nodisp_tip = wxToolTip(u'This options means "This application exists, but don\'t display it in the menus"')
        m_showin_tip = wxToolTip(u'Only Show In Tip')
        
        # --- Main Menu Entry --- #
        
        # --- Buttons to open/preview/save .desktop file
        self.open = dbr.ButtonBrowse64(self)
        self.open.SetToolTip(DF_tip)
        self.button_save = dbr.ButtonSave64(self)
        self.button_preview = dbr.ButtonPreview64(self)
        
        self.open.Bind(wxEVT_BUTTON, self.OpenFile)
        wxEVT_BUTTON(self.button_save, wxID_ANY, self.OnSave)
        wxEVT_BUTTON(self.button_preview, wxID_ANY, self.OnPreview)
        
        button_sizer = wxBoxSizer(wxHORIZONTAL)
        button_sizer.Add(self.open, 0)
        button_sizer.Add(self.button_save, 0)
        button_sizer.Add(self.button_preview, 0)
        
        # --- CHECKBOX
        self.activate = wxCheckBox(self, -1, _(u'Create system menu launcher'))
        
        self.activate.Bind(wxEVT_CHECKBOX, self.OnToggle)
        
        # --- NAME (menu)
        self.name_text = wxStaticText(self, -1, _(u'Name'))
        self.name_text.SetToolTip(m_name_tip)
        self.name_input = wxTextCtrl(self, -1)
#        self.name_input.SetBackgroundColour(dbr.Mandatory)
        
        # --- EXECUTABLE
        self.exe_text = wxStaticText(self, -1, _(u'Executable'))
        self.exe_text.SetToolTip(m_exec_tip)
        self.exe_input = wxTextCtrl(self, -1)
        
        # --- COMMENT
        self.comm_text = wxStaticText(self, -1, _(u'Comment'))
        self.comm_text.SetToolTip(m_com_tip)
        self.comm_input = wxTextCtrl(self, -1)
        
        # --- ICON
        self.icon_text = wxStaticText(self, -1, _(u'Icon'))
        self.icon_text.SetToolTip(icon_tip)
        self.icon_input = wxTextCtrl(self)
        
        # --- TYPE
        self.type_opt = (u'Application', u'Link', u'FSDevice', u'Directory')
        self.type_text = wxStaticText(self, -1, _(u'Type'))
        #self.type_text.SetToolTip(m_type_tip)
        self.type_choice = wxComboBox(self, -1, choices=self.type_opt)
        self.type_choice.SetSelection(0)
        #self.type_choice = wxChoice(self, -1, choices=self.type_opt)
        
        # --- TERMINAL
        self.term_opt = (u'true', u'false')
        self.term_text = wxStaticText(self, -1, _(u'Terminal'))
        self.term_text.SetToolTip(m_term_tip)
        self.term_choice = wxChoice(self, -1, choices=self.term_opt)
        self.term_choice.SetSelection(1)
        
        # --- STARTUP NOTIFY
        self.notify_opt = (u'true', u'false')
        self.notify_text = wxStaticText(self, -1, _(u'Startup Notify'))
        self.notify_text.SetToolTip(m_notify_tip)
        self.notify_choice = wxChoice(self, -1, choices=self.notify_opt)
        
        # --- ENCODING
        self.enc_opt = (u'UTF-1',u'UTF-7',u'UTF-8',u'CESU-8',u'UTF-EBCDIC',
                u'UTF-16',u'UTF-32',u'SCSU',u'BOCU-1',u'Punycode', u'GB 18030')
        self.enc_text = wxStaticText(self, -1, _(u'Encoding'))
        #self.enc_text.SetToolTip(m_enc_tip)
        self.enc_input = wxComboBox(self, -1, choices=self.enc_opt)
        self.enc_input.SetSelection(2)
        
        # --- CATEGORIES
        self.cat_opt = (u'2DGraphics',u'Accessibility',u'Application',u'ArcadeGame',u'Archiving',u'Audio',u'AudioVideo',
                        u'BlocksGame',u'BoardGame',u'Calculator',u'Calendar',u'CardGame',u'Compression',
                        u'ContactManagement',u'Core',u'DesktopSettings',u'Development',u'Dictionary',u'DiscBurning',
                        u'Documentation',u'Email',u'FileManager',u'FileTransfer',u'Game',u'GNOME',u'Graphics',u'GTK',
                        u'HardwareSettings',u'InstantMessaging',u'KDE',u'LogicGame',u'Math',u'Monitor',u'Network',u'OCR',
                        u'Office',u'P2P',u'PackageManager',u'Photography',u'Player',u'Presentation',u'Printing',u'Qt',
                        u'RasterGraphics',u'Recorder',u'RemoteAccess',u'Scanning',u'Screensaver',u'Security',u'Settings',
                        u'Spreadsheet',u'System',u'Telephony',u'TerminalEmulator',u'TextEditor',u'Utility',
                        u'VectorGraphics',u'Video',u'Viewer',u'WordProcessor',u'Wine',u'Wine-Programs-Accessories',
                        u'X-GNOME-NetworkSettings',u'X-GNOME-PersonalSettings',u'X-GNOME-SystemSettings',u'X-KDE-More',
                        u'X-Red-Hat-Base',u'X-SuSE-ControlCenter-System')
        self.cat_text = wxStaticText(self, -1, _(u'Category'))
        self.cat_choice = wxComboBox(self, -1, value=self.cat_opt[0], choices=self.cat_opt)
        self.cat_add = dbr.ButtonAdd(self)
        self.cat_del = dbr.ButtonDel(self)
        self.cat_clr = dbr.ButtonClear(self)
        
        # FIXME: wx 3.0 compat
        if wxMAJOR_VERSION > 3:
            self.categories = wxListCtrl(self, -1, style=wxLC_SINGLE_SEL|wxBORDER_SIMPLE)
            self.categories.InsertColumn(0, u'')
        
        else:
            self.categories = wxListCtrl(self, -1)
            self.categories.SetSingleStyle(wxLC_SINGLE_SEL)
        
        
        wxEVT_KEY_DOWN(self.cat_choice, self.SetCategory)
        wxEVT_KEY_DOWN(self.categories, self.SetCategory)
        wxEVT_BUTTON(self.cat_add, -1, self.SetCategory)
        wxEVT_BUTTON(self.cat_del, -1, self.SetCategory)
        wxEVT_BUTTON(self.cat_clr, -1, self.SetCategory)
        
        cat_sizer0 = wxBoxSizer(wxHORIZONTAL)
        cat_sizer0.Add(self.cat_add, 0, wxRIGHT, 5)
        cat_sizer0.Add(self.cat_del, 0, wxRIGHT, 5)
        cat_sizer0.Add(self.cat_clr, 0)
        
        cat_sizer1 = wxBoxSizer(wxVERTICAL)
        cat_sizer1.Add(self.cat_text, 0, wxLEFT, 1)
        cat_sizer1.Add(self.cat_choice, 0, wxTOP|wxBOTTOM, 5)
        cat_sizer1.Add(cat_sizer0, 0)
        
        cat_sizer2 = wxBoxSizer(wxHORIZONTAL)
        cat_sizer2.Add(cat_sizer1, 0)
        cat_sizer2.Add(self.categories, 1, wxEXPAND|wxLEFT, 5)
        
        
        # ----- MISC
        self.misc_text = wxStaticText(self, -1, _(u'Other'))
        self.misc = wxTextCtrl(self, -1, style=wxTE_MULTILINE|wxBORDER_SIMPLE)
        
        misc_sizer = wxBoxSizer(wxHORIZONTAL)
        misc_sizer.Add(self.misc, 1, wxEXPAND)
        
        # Organize the widgets and create a nice border
        sizer1 = wxFlexGridSizer(0, 4, 5, 5)
        sizer1.AddGrowableCol(1)
        sizer1.AddMany( [
            (self.name_text, 0, wxTOP, 10),(self.name_input, 0, wxEXPAND|wxTOP, 10),
            (self.type_text, 0, wxTOP, 10),(self.type_choice, 0, wxTOP, 10),
            (self.exe_text),(self.exe_input, 0, wxEXPAND),
            (self.term_text),(self.term_choice),
            (self.comm_text),(self.comm_input, 0, wxEXPAND),
            (self.notify_text),(self.notify_choice),
            (self.icon_text),(self.icon_input, 0, wxEXPAND),
            (self.enc_text),(self.enc_input, 0, wxEXPAND),
            ] )
        
        self.border = wxStaticBox(self, -1, size=(20,20))
        border_box = wxStaticBoxSizer(self.border, wxVERTICAL)
        border_box.Add(sizer1, 0, wxEXPAND|wxLEFT|wxRIGHT, 5)
        border_box.Add(cat_sizer2, 0, wxEXPAND|wxLEFT|wxRIGHT|wxTOP, 5)
        border_box.AddSpacer(20)
        border_box.Add(self.misc_text, 0, wxLEFT, 6)
        border_box.Add(self.misc, 1, wxEXPAND|wxLEFT|wxRIGHT, 5)
        
        # --- List of main menu items affected by checkbox -- used for toggling each widget
        self.menu_list = (self.open, self.button_save, self.button_preview, self.icon_input, self.name_input,
                        self.comm_input, self.exe_input, self.enc_input, self.type_choice, self.cat_choice,
                        self.categories, self.cat_add, self.cat_del, self.cat_clr, self.term_choice,
                        self.notify_choice, self.misc)
                        #, self.m_nodisp_widg, self.m_showin_widg)
        
        self.OnToggle(None) #Disable widgets
        
        # --- Page 5 Sizer --- #
        page_sizer = wxBoxSizer(wxVERTICAL)
        page_sizer.AddSpacer(5)
        page_sizer.Add(button_sizer, 0, wxLEFT, 5)
        page_sizer.AddSpacer(10)
        page_sizer.Add(self.activate, 0, wxLEFT, 5)
        page_sizer.Add(border_box, 1, wxEXPAND|wxALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(page_sizer)
        self.Layout()
        
        # List of entries in a standard .desktop file
        self.standards = {    u'name': self.name_input, u'type': self.type_choice, u'exec': self.exe_input,
                            u'comment': self.comm_input, u'terminal': self.term_choice,
                            u'startupnotify': self.notify_choice, u'encoding': self.enc_input,
                            u'categories': self.categories
                            }
        
        # Lists of widgets that change language
        self.setlabels = {    self.activate: u'Menu', self.open: u'Open', self.border: u'Border',
                            self.icon_text: u'Icon',
                            self.name_text: u'Name', self.comm_text: u'Comm', self.exe_text: u'Exec',
                            self.enc_text: u'Enc', self.type_text: u'Type', self.cat_text: u'Cat',
                            self.term_text: u'Term', self.notify_text: u'Notify'}
    
    def OnToggle(self, event):
        if self.activate.IsChecked():
            for item in self.menu_list:
                item.Enable()
                # Change the background color of name_input
#                if item == self.name_input:
#                    item.SetBackgroundColour(dbr.Mandatory)
                    
        else:
            for item in self.menu_list:
                item.Disable()
                # Change background color of name_input
#                if item == self.name_input:
#                    item.SetBackgroundColour(dbr.Disabled)
    
    def GetMenuInfo(self):
        # Create list to store info
        desktop_list = [u'[Desktop Entry]']
        
        # Add Name
        name = self.name_input.GetValue()
        desktop_list.append(u'Name=%s' % name)
        
        # Add Version
        desktop_list.append(u'Version=1.0')
        
        # Add Executable
        exe = self.exe_input.GetValue()
        desktop_list.append(u'Exec=%s' % exe)
        
        # Add Comment
        comm = self.comm_input.GetValue()
        desktop_list.append(u'Comment=%s' % comm)
        
        # Add Icon
        icon = self.icon_input.GetValue()
        desktop_list.append(u'Icon=%s' % icon)
        
        # Add Type
        #type = self.type_opt[self.type_choice.GetSelection()]
        _type = self.type_choice.GetValue()
        desktop_list.append(u'Type=%s' % _type)
        
        # Add Terminal
        if self.term_choice.GetSelection() == 0:
            desktop_list.append(u'Terminal=true')
        else:
            desktop_list.append(u'Terminal=false')
        
        # Add Startup Notify
        if self.notify_choice.GetSelection() == 0:
            desktop_list.append(u'StartupNotify=true')
        else:
            desktop_list.append(u'StartupNotify=false')
        
        # Add Encoding
        enc = self.enc_input.GetValue()
        desktop_list.append(u'Encoding=%s' % enc)
        
        # Add Categories
        cat_list = []
        cat_total = self.categories.GetItemCount()
        count = 0
        while count < cat_total:
            cat_list.append(self.categories.GetItemText(count))
            count += 1
        # Add a final semi-colon if categories is not empty
        if cat_list != []:
            cat_list[-1] = u'%s;' % cat_list[-1]
        desktop_list.append(u'Categories=%s' % u';'.join(cat_list))
        
        # Add Misc
        if self.misc.GetValue() != wxEmptyString:
            desktop_list.append(self.misc.GetValue())
        
        return u'\n'.join(desktop_list)
    
    def SetCategory(self, event):
        try:
            id = event.GetKeyCode()
        except AttributeError:
            id = event.GetEventObject().GetId()
        
        cat = self.cat_choice.GetValue()
        cat = cat.split()
        cat = u''.join(cat)
        
        if id == wxWXK_RETURN or id == wxWXK_NUMPAD_ENTER:
            self.categories.InsertStringItem(0, cat)
        
        elif id == wxWXK_DELETE:
            cur_cat = self.categories.GetFirstSelected()
            self.categories.DeleteItem(cur_cat)
        
        elif id == wxWXK_ESCAPE:
            confirm = wxMessageDialog(self, _(u'Delete all categories?'), _(u'Confirm'),
                    wxYES_NO|wxNO_DEFAULT|wxICON_QUESTION)
            if confirm.ShowModal() == wxID_YES:
                self.categories.DeleteAllItems()
        event.Skip()
    
    
    # *** OPEN/SAVE *** #
    def OnSave(self, event):
        # Get data to write to control file
        menu_data = self.GetMenuInfo().encode(u'utf-8')
        menu_data = menu_data.split(u'\n')
        menu_data = u'\n'.join(menu_data[1:])
        
        # Saving?
        cont = False
        
        # Open a u'Save Dialog'
        if self.parent.parent.cust_dias.IsChecked():
            dia = dbr.SaveFile(self, _(u'Save Launcher'))
#            dia.SetFilename(u'control')
            if dia.DisplayModal():
                cont = True
                path = u'%s/%s' % (dia.GetPath(), dia.GetFilename())
        else:
            dia = wxFileDialog(self, _(u'Save Launcher'), os.getcwd(),
                style=wxFD_SAVE|wxFD_CHANGE_DIR|wxFD_OVERWRITE_PROMPT)
#            dia.SetFilename(u'control')
            if dia.ShowModal() == wxID_OK:
                cont = True
                path = dia.GetPath()
        
        if cont:
            filename = dia.GetFilename()
            
            # Create a backup file
            overwrite = False
            if os.path.isfile(path):
                backup = u'%s.backup' % path
                shutil.copy(path, backup)
                overwrite = True
            
            file = open(path, u'w')
            try:
                file.write(menu_data)
                file.close()
                if overwrite:
                    os.remove(backup)
            except UnicodeEncodeError:
                serr = _(u'Save failed')
                uni = _(u'Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                UniErr = wxMessageDialog(self, u'%s\n\n%s' % (serr, uni), _(u'Unicode Error'), style=wxOK|wxICON_EXCLAMATION)
                UniErr.ShowModal()
                file.close()
                os.remove(path)
                # Restore from backup
                shutil.move(backup, path)
    
    def OpenFile(self, event):
        cont = False
        if self.parent.parent.cust_dias.IsChecked():
            dia = dbr.OpenFile(self, _(u'Open Launcher'))
            if dia.DisplayModal():
                cont = True
        else:
            dia = wxFileDialog(self, _(u'Open Launcher'), os.getcwd(),
                style=wxFD_CHANGE_DIR)
            if dia.ShowModal() == wxID_OK:
                cont = True
        
        if cont == True:
            path = dia.GetPath()
            file = open(path, u'r')
            text = file.read()
            file.close()
            data = text.split(u'\n')
            if data[0] == u'[Desktop Entry]':
                data = data[1:]
                # First line needs to be changed to '1'
            data.insert(0, u'1')
            self.SetFieldData(u'\n'.join(data))
        
    def OnPreview(self, event):
        # Show a preview of the .desktop config file
        config = self.GetMenuInfo()
        
        dia = wxDialog(self, -1, _(u'Preview'), size=(500,400))
        preview = wxTextCtrl(dia, -1, style=wxTE_MULTILINE|wxTE_READONLY)
        preview.SetValue(config)
        
        dia_sizer = wxBoxSizer(wxVERTICAL)
        dia_sizer.Add(preview, 1, wxEXPAND)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    def ResetAllFields(self):
        self.name_input.Clear()
        self.exe_input.Clear()
        self.comm_input.Clear()
        self.icon_input.Clear()
        self.type_choice.SetSelection(0)
        self.term_choice.SetSelection(1)
        self.notify_choice.SetSelection(0)
        self.enc_input.SetSelection(2)
        self.categories.DeleteAllItems()
        self.misc.Clear()
        self.activate.SetValue(False)
        self.OnToggle(None)
    
    def SetFieldData(self, data):
        # Clear all fields first
        self.ResetAllFields()
        self.activate.SetValue(False)
        
        if int(data[0]):
            self.activate.SetValue(True)
            # Fields using SetValue() function
            set_value_fields = (
                (u'Name', self.name_input), (u'Exec', self.exe_input), (u'Comment', self.comm_input),
                (u'Icon', self.icon_input)
                )
            
            # Fields using SetSelection() function
            set_selection_fields = (
                (u'Terminal', self.term_choice, self.term_opt),
                (u'StartupNotify', self.notify_choice, self.notify_opt)
                )
            
            # Fields using either SetSelection() or SetValue()
            set_either_fields = (
                (u'Type', self.type_choice, self.type_opt),
                (u'Encoding', self.enc_input, self.enc_opt)
                )
            
            lines = data.split(u'\n')
            
            # Leave leftover text in this list to dump into misc field
            leftovers = lines[:]
            
            # Remove 1st line (1) from leftovers
            leftovers = leftovers[1:]
            
            # Remove Version field since is not done below
            try:
                leftovers.remove(u'Version=1.0')
            except ValueError:
                pass
            
            for line in lines:
                f1 = line.split(u'=')[0]
                f2 = u'='.join(line.split(u'=')[1:])
                for setval in set_value_fields:
                    if f1 == setval[0]:
                        setval[1].SetValue(f2)
                        leftovers.remove(line) # Remove the field so it's not dumped into misc
                for setsel in set_selection_fields:
                    if f1 == setsel[0]:
                        setsel[1].SetSelection(setsel[2].index(f2))
                        leftovers.remove(line)
                for either in set_either_fields:
                    if f1 == either[0]:
                        # If the value is in the predefined options we will set the field data to show
                        # the option so that the mouse wheel works when hovering over field
                        if f2 in either[2]:
                            either[1].SetSelection(either[2].index(f2))
                        else:
                            either[1].SetValue(f2)
                        leftovers.remove(line)
                # Categories
                if f1 == u'Categories':
                    leftovers.remove(line)
                    categories = f2.split(u';')
                    cat_count = len(categories)-1
                    while cat_count > 0:
                        cat_count -= 1
                        self.categories.InsertStringItem(0, categories[cat_count])
            if len(leftovers) > 0:
                self.misc.SetValue(u'\n'.join(leftovers))
        self.OnToggle(None)
    
    def GatherData(self):
        if self.activate.GetValue():
            data = self.GetMenuInfo()
            data = u'\n'.join(data.split(u'\n')[1:])
            return u'<<MENU>>\n1\n%s\n<</MENU>>' % data
        else:
            return u'<<MENU>>\n0\n<</MENU>>'
