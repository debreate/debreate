# -*- coding: utf-8 -*-

# Menu Page

import os, shutil, wx

import db
from dbr.buttons    import ButtonAdd
from dbr.buttons    import ButtonBrowse64
from dbr.buttons    import ButtonClear
from dbr.buttons    import ButtonDel
from dbr.buttons    import ButtonPreview64
from dbr.buttons    import ButtonSave64
from dbr.functions  import TextIsEmpty
from dbr.language   import GT


ID = wx.NewId()

class Panel(wx.ScrolledWindow):
    def __init__(self, parent, id=ID, name=GT(u'Menu Launcher')):
        wx.ScrolledWindow.__init__(self, parent, id, name=GT(u'Menu Launcher'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        # --- Tool Tips --- #
        DF_tip = wx.ToolTip(GT(u'Open launcher file'))
        icon_tip = wx.ToolTip(GT(u'Icon to be displayed for the launcher'))
        m_name_tip = wx.ToolTip(GT(u'Text for the launcher'))
        #m_ver_tip = wx.ToolTip(GT(u'The version of your application'))
        m_com_tip = wx.ToolTip(GT(u'Text displayed when mouse hovers over launcher'))
        m_exec_tip = wx.ToolTip(GT(u'Executable to be launched'))
        m_mime_tip = wx.ToolTip(GT(u'Specifies the MIME types that the application can handle'))
        #m_enc_tip = wx.ToolTip(GT(u'Specifies the encoding of the desktop entry file'))
        #m_type_tip = wx.ToolTip(GT(u'The type of launcher'))
        m_cat_tip = wx.ToolTip(GT(u'Choose which categories in which you would like your application to be displayed'))
        m_term_tip = wx.ToolTip(GT(u'Specifies whether application should be run from a terminal'))
        m_notify_tip = wx.ToolTip(GT(u'Displays a notification in the system panel when launched'))
        m_nodisp_tip = wx.ToolTip(GT(u'This options means "This application exists, but don\'t display it in the menus"'))
        m_showin_tip = wx.ToolTip(GT(u'Only Show In Tip'))
        
        # --- Main Menu Entry --- #
        
        # --- Buttons to open/preview/save .desktop file
        self.open = ButtonBrowse64(self)
        self.open.SetToolTip(DF_tip)
        self.button_save = ButtonSave64(self)
        self.button_preview = ButtonPreview64(self)
        
        self.open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
        wx.EVT_BUTTON(self.button_save, wx.ID_ANY, self.OnSaveLauncher)
        wx.EVT_BUTTON(self.button_preview, wx.ID_ANY, self.OnPreviewLauncher)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.open, 0)
        button_sizer.Add(self.button_save, 0)
        button_sizer.Add(self.button_preview, 0)
        
        # --- CHECKBOX
        self.activate = wx.CheckBox(self, -1, GT(u'Create system menu launcher'))
        
        self.activate.Bind(wx.EVT_CHECKBOX, self.OnToggle)
        
        self.txt_filename = wx.StaticText(self, label=GT(u'Filename'))
        self.input_filename = wx.TextCtrl(self)
        self.chk_filename = wx.CheckBox(self, label=GT(u'Use "Name" as output filename (<name>.desktop)'))
        self.chk_filename.SetValue(True)
        
        self.chk_filename.Bind(wx.EVT_CHECKBOX, self.OnSetCustomFilename)
        
        for I in self.txt_filename, self.input_filename:
            I.SetToolTip(wx.ToolTip(GT(u'Custom filename to use for launcher')))
        
        self.chk_filename.SetToolTip(
                wx.ToolTip(GT(u'If checked, the value of the "Name" field will be used for the filename'))
            )
        
        # --- NAME (menu)
        self.name_text = wx.StaticText(self, -1, GT(u'Name'))
        self.name_text.SetToolTip(m_name_tip)
        self.name_input = wx.TextCtrl(self, -1)
        
        # --- EXECUTABLE
        self.exe_text = wx.StaticText(self, -1, GT(u'Executable'))
        self.exe_text.SetToolTip(m_exec_tip)
        self.exe_input = wx.TextCtrl(self, -1)
        
        # --- COMMENT
        self.comm_text = wx.StaticText(self, -1, GT(u'Comment'))
        self.comm_text.SetToolTip(m_com_tip)
        self.comm_input = wx.TextCtrl(self, -1)
        
        # --- ICON
        self.icon_text = wx.StaticText(self, -1, GT(u'Icon'))
        self.icon_text.SetToolTip(icon_tip)
        self.icon_input = wx.TextCtrl(self)
        
        # --- TYPE
        self.type_opt = (u'Application', u'Link', u'FSDevice', u'Directory')
        self.type_text = wx.StaticText(self, -1, GT(u'Type'))
        #self.type_text.SetToolTip(m_type_tip)
        self.type_choice = wx.ComboBox(self, -1, choices=self.type_opt)
        self.type_choice.SetSelection(0)
        #self.type_choice = wx.Choice(self, -1, choices=self.type_opt)
        
        # --- TERMINAL
        self.term_opt = (u'true', u'false')
        self.term_text = wx.StaticText(self, -1, GT(u'Terminal'))
        self.term_text.SetToolTip(m_term_tip)
        self.term_choice = wx.Choice(self, -1, choices=self.term_opt)
        self.term_choice.SetSelection(1)
        
        # --- STARTUP NOTIFY
        self.notify_opt = (u'true', u'false')
        self.notify_text = wx.StaticText(self, -1, GT(u'Startup Notify'))
        self.notify_text.SetToolTip(m_notify_tip)
        self.notify_choice = wx.Choice(self, -1, choices=self.notify_opt)
        self.notify_choice.SetSelection(0)
        
        # --- ENCODING
        self.enc_opt = (
            u'UTF-1', u'UTF-7', u'UTF-8', u'CESU-8', u'UTF-EBCDIC', u'UTF-16', u'UTF-32',
            u'SCSU', u'BOCU-1', u'Punycode', u'GB 18030'
            )
        self.enc_text = wx.StaticText(self, -1, GT(u'Encoding'))
        #self.enc_text.SetToolTip(m_enc_tip)
        self.enc_input = wx.ComboBox(self, -1, choices=self.enc_opt)
        self.enc_input.SetSelection(2)
        
        # --- CATEGORIES
        self.cat_opt = (
            u'2DGraphics', u'Accessibility', u'Application', u'ArcadeGame', u'Archiving', u'Audio',
            u'AudioVideo', u'BlocksGame', u'BoardGame', u'Calculator', u'Calendar', u'CardGame',
            u'Compression', u'ContactManagement', u'Core', u'DesktopSettings', u'Development',
            u'Dictionary', u'DiscBurning', u'Documentation', u'Email', u'FileManager',
            u'FileTransfer', u'Game', u'GNOME', u'Graphics', u'GTK', u'HardwareSettings',
            u'InstantMessaging', u'KDE', u'LogicGame', u'Math', u'Monitor', u'Network', u'OCR',
            u'Office', u'P2P', u'PackageManager', u'Photography', u'Player', u'Presentation',
            u'Printing', u'Qt', u'RasterGraphics', u'Recorder', u'RemoteAccess', u'Scanning',
            u'Screensaver', u'Security', u'Settings', u'Spreadsheet', u'System', u'Telephony',
            u'TerminalEmulator', u'TextEditor', u'Utility', u'VectorGraphics', u'Video', u'Viewer',
            u'WordProcessor', u'Wine', u'Wine-Programs-Accessories', u'X-GNOME-NetworkSettings',
            u'X-GNOME-PersonalSettings', u'X-GNOME-SystemSettings', u'X-KDE-More', u'X-Red-Hat-Base',
            u'X-SuSE-ControlCenter-System',
            )
        self.cat_text = wx.StaticText(self, -1, GT(u'Category'))
        self.cat_choice = wx.ComboBox(self, -1, value=self.cat_opt[0], choices=self.cat_opt)
        self.cat_add = ButtonAdd(self)
        self.cat_del = ButtonDel(self)
        self.cat_clr = ButtonClear(self)
        
        if wx.MAJOR_VERSION > 2:
            self.categories = wx.ListCtrl(self, -1)
            self.categories.SetSingleStyle(wx.LC_SINGLE_SEL|wx.LC_REPORT)
        else:
            self.categories = wx.ListCtrl(self, -1, style=wx.LC_SINGLE_SEL|wx.BORDER_SIMPLE)
        
        self.categories.InsertColumn(0, u'')
        
        wx.EVT_KEY_DOWN(self.cat_choice, self.SetCategory)
        wx.EVT_KEY_DOWN(self.categories, self.SetCategory)
        wx.EVT_BUTTON(self.cat_add, -1, self.SetCategory)
        wx.EVT_BUTTON(self.cat_del, -1, self.SetCategory)
        wx.EVT_BUTTON(self.cat_clr, -1, self.SetCategory)
        
        cat_sizer0 = wx.BoxSizer(wx.HORIZONTAL)
        cat_sizer0.Add(self.cat_add, 0, wx.RIGHT, 5)
        cat_sizer0.Add(self.cat_del, 0, wx.RIGHT, 5)
        cat_sizer0.Add(self.cat_clr, 0)
        
        cat_sizer1 = wx.BoxSizer(wx.VERTICAL)
        cat_sizer1.Add(self.cat_text, 0, wx.LEFT, 1)
        cat_sizer1.Add(self.cat_choice, 0, wx.TOP|wx.BOTTOM, 5)
        cat_sizer1.Add(cat_sizer0, 0)
        
        cat_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        cat_sizer2.Add(cat_sizer1, 0)
        cat_sizer2.Add(self.categories, 1, wx.EXPAND|wx.LEFT, 5)
        
        
        # ----- MISC
        self.misc_text = wx.StaticText(self, -1, GT(u'Other'))
        self.misc = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.BORDER_SIMPLE)
        
        misc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        misc_sizer.Add(self.misc, 1, wx.EXPAND)
        
        
        # GridBagSizer flags
        CENTER = wx.ALIGN_CENTER_VERTICAL
        CENTER_EXPAND = wx.ALIGN_CENTER_VERTICAL|wx.EXPAND
        CENTER_RIGHT = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        
        # Organize the widgets and create a nice border
        sizer1 = wx.GridBagSizer(5, 5)
        #sizer1 = wx.FlexGridSizer(0, 4, 5, 5)
        sizer1.SetCols(4)
        sizer1.AddGrowableCol(1)
        
        # Row 1
        sizer1.Add(self.txt_filename, (0, 0), flag=CENTER)
        sizer1.Add(self.input_filename, pos=(0, 1), flag=CENTER_EXPAND)
        sizer1.Add(self.chk_filename, pos=(0, 2), span=(1, 2), flag=CENTER_RIGHT)
        
        # Row 2
        sizer1.Add(self.name_text, (1, 0), flag=CENTER)
        sizer1.Add(self.name_input, (1, 1), flag=CENTER_EXPAND)
        sizer1.Add(self.type_text, (1, 2), flag=CENTER)
        sizer1.Add(self.type_choice, (1, 3), flag=CENTER)
        
        # Row 3
        sizer1.Add(self.exe_text, (2, 0), flag=CENTER)
        sizer1.Add(self.exe_input, (2, 1), flag=CENTER_EXPAND)
        sizer1.Add(self.term_text, (2, 2), flag=CENTER)
        sizer1.Add(self.term_choice, (2, 3), flag=CENTER)
        
        # Row 4
        sizer1.Add(self.comm_text, (3, 0), flag=CENTER)
        sizer1.Add(self.comm_input, (3, 1), flag=CENTER_EXPAND)
        sizer1.Add(self.notify_text, (3, 2), flag=CENTER)
        sizer1.Add(self.notify_choice, (3, 3), flag=CENTER)
        
        # Row 5
        sizer1.Add(self.icon_text, (4, 0), flag=CENTER)
        sizer1.Add(self.icon_input, (4, 1), flag=CENTER_EXPAND)
        sizer1.Add(self.enc_text, (4, 2), flag=CENTER)
        sizer1.Add(self.enc_input, (4, 3), flag=CENTER)
        
        
        self.border = wx.StaticBox(self, -1, size=(20,20))
        border_box = wx.StaticBoxSizer(self.border, wx.VERTICAL)
        
        border_box.Add(sizer1, 0, wx.EXPAND|wx.BOTTOM, 5)
        border_box.Add(cat_sizer2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        border_box.AddSpacer(5)
        border_box.Add(self.misc_text, 0)
        border_box.Add(self.misc, 1, wx.EXPAND)
        
        # --- List of main menu items affected by checkbox -- used for toggling each widget
        self.menu_list = (
            self.button_save, self.button_preview, self.chk_filename, self.icon_input,
            self.name_input, self.comm_input, self.exe_input, self.enc_input, self.type_choice,
            self.cat_choice, self.categories, self.cat_add, self.cat_del, self.cat_clr,
            self.term_choice, self.notify_choice, self.misc,
            )
        
        self.OnToggle(None) #Disable widgets
        
        # --- Page 5 Sizer --- #
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page_sizer.AddSpacer(5)
        page_sizer.Add(button_sizer, 0, wx.LEFT, 5)
        page_sizer.AddSpacer(10)
        page_sizer.Add(self.activate, 0, wx.LEFT, 5)
        #page_sizer.Add(layout_filename, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5)
        page_sizer.Add(border_box, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(page_sizer)
        self.Layout()
        
        # List of entries in a standard .desktop file
        self.standards = {
            u'name': self.name_input,
            u'type': self.type_choice,
            u'exec': self.exe_input,
            u'comment': self.comm_input,
            u'terminal': self.term_choice,
            u'startupnotify': self.notify_choice,
            u'encoding': self.enc_input,
            u'categories': self.categories,
            }
        
        # Lists of widgets that change language
        self.setlabels = {
            self.activate: u'Menu',
            self.open: u'Open',
            self.border: u'Border',
            self.icon_text: u'Icon',
            self.name_text: u'Name',
            self.comm_text: u'Comm',
            self.exe_text: u'Exec',
            self.enc_text: u'Enc',
            self.type_text: u'Type',
            self.cat_text: u'Cat',
            self.term_text: u'Term',
            self.notify_text: u'Notify',
            }
    
    
    def OnToggle(self, event=None):
        if self.activate.IsChecked():
            for item in self.menu_list:
                item.Enable()
        
        else:
            for item in self.menu_list:
                item.Disable()
        
        self.OnSetCustomFilename(None)
    
    
    ## Formats the launcher information for export
    def GetLauncherInfo(self):
        desktop_list = [u'[Desktop Entry]']
        
        name = self.name_input.GetValue()
        if not TextIsEmpty(name):
            desktop_list.append(u'Name={}'.format(name))
        
        desktop_list.append(u'Version=1.0')
        
        executable = self.exe_input.GetValue()
        if not TextIsEmpty(executable):
            desktop_list.append(u'Exec={}'.format(executable))
        
        comment = self.comm_input.GetValue()
        if not TextIsEmpty(comment):
            desktop_list.append(u'Comment={}'.format(comment))
        
        icon = self.icon_input.GetValue()
        if not TextIsEmpty(icon):
            desktop_list.append(u'Icon={}'.format(icon))
        
        launcher_type = self.type_choice.GetValue()
        if not TextIsEmpty(launcher_type):
            desktop_list.append(u'Type={}'.format(launcher_type))
        
        terminal = self.term_choice.GetStringSelection()
        if not TextIsEmpty(terminal):
            desktop_list.append(u'Terminal={}'.format(terminal))
        
        startup_notify = self.notify_choice.GetStringSelection()
        if not TextIsEmpty(startup_notify):
            desktop_list.append(u'StartupNotify={}'.format(startup_notify))
        
        encoding = self.enc_input.GetValue()
        if not TextIsEmpty(encoding):
            desktop_list.append(u'Encoding={}'.format(encoding))
        
        categories = []
        cat_total = self.categories.GetItemCount()
        count = 0
        while count < cat_total:
            C = self.categories.GetItemText(count)
            if not TextIsEmpty(C):
                categories.append(self.categories.GetItemText(count))
            
            count += 1
        
        # Add a final semi-colon if categories is not empty
        if categories:
            categories = u';'.join(categories)
            if categories[-1] != u';':
                categories = u'{};'.format(categories)
            
            desktop_list.append(u'Categories={}'.format(categories))
        
        # Add Misc
        if self.misc.GetValue() != wx.EmptyString:
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
        
        if id == wx.WXK_RETURN or id == wx.WXK_NUMPAD_ENTER:
            self.categories.InsertStringItem(self.categories.GetItemCount(), cat)
        
        elif id == wx.WXK_DELETE:
            if self.categories.GetItemCount() and self.categories.GetSelectedItemCount():
                cur_cat = self.categories.GetFirstSelected()
                self.categories.DeleteItem(cur_cat)
        
        elif id == wx.ID_CLEAR:
            if self.categories.GetItemCount():
                confirm = wx.MessageDialog(self, GT(u'Clear categories?'), GT(u'Confirm'),
                        wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                
                if confirm.ShowModal() == wx.ID_YES:
                    self.categories.DeleteAllItems()
        
        event.Skip()
    
    
    ## Saves launcher information to file
    def OnSaveLauncher(self, event):
        # Get data to write to control file
        menu_data = self.GetLauncherInfo().encode(u'utf-8')
        
        # Saving?
        cont = False
        
        # Open a "Save Dialog"
        if wx.GetApp().GetTopWindow().cust_dias.IsChecked():
            dia = db.SaveFile(self, GT(u'Save Launcher'))
            if dia.DisplayModal():
                cont = True
                path = u'{}/{}'.format(dia.GetPath(), dia.GetFilename())
        
        else:
            dia = wx.FileDialog(self, GT(u'Save Launcher'), os.getcwd(),
                style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
                path = dia.GetPath()
        
        if cont:
            filename = dia.GetFilename()
            
            # Create a backup file
            overwrite = False
            if os.path.isfile(path):
                backup = u'{}.backup'.format(path)
                shutil.copy(path, backup)
                overwrite = True
            
            FILE_BUFFER = open(path, u'w')
            try:
                FILE_BUFFER.write(menu_data)
                FILE_BUFFER.close()
                if overwrite:
                    os.remove(backup)
            
            except UnicodeEncodeError:
                serr = GT(u'Save failed')
                uni = GT(u'Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                UniErr = wx.MessageDialog(self, u'{}\n\n{}'.format(serr, uni), GT(u'Unicode Error'), style=wx.OK|wx.ICON_EXCLAMATION)
                UniErr.ShowModal()
                FILE_BUFFER.close()
                os.remove(path)
                # Restore from backup
                shutil.move(backup, path)
    
    
    ## TODO: Doxygen
    def OnSetCustomFilename(self, event=None):
        if not self.chk_filename.IsEnabled():
            self.txt_filename.Enable(False)
            self.input_filename.Enable(False)
            return
        
        if self.chk_filename.GetValue():
            self.txt_filename.Enable(False)
            self.input_filename.Enable(False)
            return
        
        self.txt_filename.Enable(True)
        self.input_filename.Enable(True)
    
    
    ## Loads a .desktop launcher's data
    def OnLoadLauncher(self, event=None):
        cont = False
        if wx.GetApp().GetTopWindow().cust_dias.IsChecked():
            dia = db.OpenFile(self, GT(u'Open Launcher'))
            if dia.DisplayModal():
                cont = True
        else:
            dia = wx.FileDialog(self, GT(u'Open Launcher'), os.getcwd(),
                style=wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
        
        if cont == True:
            path = dia.GetPath()
            
            FILE_BUFFER = open(path, u'r')
            data = FILE_BUFFER.read().split(u'\n')
            FILE_BUFFER.close()
            
            # Remove unneeded lines
            if data[0] == u'[Desktop Entry]':
                data = data[1:]
            
            self.SetLauncherData(u'\n'.join(data), enabled=True)
    
    
    def OnPreviewLauncher(self, event):
        # Show a preview of the .desktop config file
        config = self.GetLauncherInfo()
        
        dia = wx.Dialog(self, -1, GT(u'Preview'), size=(500,400))
        preview = wx.TextCtrl(dia, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        preview.SetValue(config)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    def ResetAllFields(self):
        self.input_filename.Clear()
        self.chk_filename.SetValue(True)
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
    
    
    ## Fills out launcher information from loaded file
    def SetLauncherData(self, data, enabled=True):
        
        # Make sure we are dealing with a list
        if isinstance(data, (unicode, str)):
            data = data.split(u'\n')
        
        # Clear all fields first
        self.ResetAllFields()
        self.activate.SetValue(False)
        
        if enabled:
            self.activate.SetValue(True)
            
            data_defs = {}
            data_defs_remove = []
            misc_defs = {}
            
            for L in data:
                if u'=' in L:
                    if L[0] == u'[' and L[-1] == u']':
                        key = L[1:-1].split(u'=')
                        value = key[1]
                        key = key[0]
                        
                        misc_defs[key] = value
                    
                    else:
                        key = L.split(u'=')
                        value = key[1]
                        key = key[0]
                        
                        data_defs[key] = value
            
            # Fields using SetValue() function
            set_value_fields = (
                (u'Name', self.name_input),
                (u'Exec', self.exe_input),
                (u'Comment', self.comm_input),
                (u'Icon', self.icon_input),
                (u'Type', self.type_choice),
                (u'Encoding', self.enc_input),
                )
            
            for label, control in set_value_fields:
                try:
                    control.SetValue(data_defs[label])
                    data_defs_remove.append(label)
                
                except KeyError:
                    pass
            
            # Fields using SetSelection() function
            set_selection_fields = (
                (u'Terminal', self.term_choice), #, self.term_opt),
                (u'StartupNotify', self.notify_choice), #, self.notify_opt)
                )
            
            for label, control in set_selection_fields:
                try:
                    control.SetStringSelection(data_defs[label].lower())
                    data_defs_remove.append(label)
                
                except KeyError:
                    pass
            
            try:
                categories = tuple(data_defs[u'Categories'].split(u';'))
                for C in categories:
                    self.categories.InsertStringItem(self.categories.GetItemCount(), C)
                data_defs_remove.append(u'Categories')
            
            except KeyError:
                pass
        
        for K in data_defs_remove:
            if K in data_defs:
                del data_defs[K]
        
        # Add any leftover keys to misc/other
        for K in data_defs:
            if K not in (u'Version',):
                self.misc.WriteText(u'{}={}'.format(K, data_defs[K]))
        
        if misc_defs:
            for K in misc_defs:
                value = misc_defs[K]
                if not TextIsEmpty(value):
                    if K == u'FILENAME':
                        self.input_filename.SetValue(value)
                        self.chk_filename.SetValue(False)
        
        self.OnToggle(None)
    
    
    def GatherData(self):
        if self.activate.GetValue():
            data = self.GetLauncherInfo()
            data = u'\n'.join(data.split(u'\n')[1:])
            
            if not self.chk_filename.GetValue():
                data = u'[FILENAME={}]\n{}'.format(self.input_filename.GetValue(), data)
            
            return u'<<MENU>>\n1\n{}\n<</MENU>>'.format(data)
        
        else:
            return u'<<MENU>>\n0\n<</MENU>>'
