# -*- coding: utf-8 -*-

# Menu Page


import os, shutil, wx
from wx.combo import OwnerDrawnComboBox

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonBrowse64
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonDel
from dbr.buttons        import ButtonPreview64
from dbr.buttons        import ButtonSave64
from dbr.custom         import OpenFile
from dbr.custom         import SaveFile
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from globals.ident      import ID_MENU
from globals.tooltips   import SetPageToolTips


class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_MENU, name=GT(u'Menu Launcher'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        # --- Main Menu Entry --- #
        
        self.options_button = []
        self.options_input = []
        self.options_choice = []
        self.options_list = []
        
        # --- Buttons to open/preview/save .desktop file
        self.btn_open = ButtonBrowse64(self)
        self.btn_open.SetName(u'open')
        
        self.btn_save = ButtonSave64(self)
        self.btn_save.SetName(u'export')
        self.options_button.append(self.btn_save)
        
        self.btn_preview = ButtonPreview64(self)
        self.btn_preview.SetName(u'preview')
        self.options_button.append(self.btn_preview)
        
        self.btn_open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
        wx.EVT_BUTTON(self.btn_save, wx.ID_ANY, self.OnSaveLauncher)
        wx.EVT_BUTTON(self.btn_preview, wx.ID_ANY, self.OnPreviewLauncher)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.btn_open, 0)
        button_sizer.Add(self.btn_save, 0)
        button_sizer.Add(self.btn_preview, 0)
        
        # --- CHECKBOX
        self.activate = wx.CheckBox(self, label=GT(u'Create system menu launcher'))
        self.activate.default = False
        
        self.activate.Bind(wx.EVT_CHECKBOX, self.OnToggle)
        
        # --- Custom output filename
        self.txt_filename = wx.StaticText(self, label=GT(u'Filename'), name=u'filename')
        self.input_filename = wx.TextCtrl(self, name=u'filename')
        
        self.chk_filename = wx.CheckBox(self, label=GT(u'Use "Name" as output filename (<Name>.desktop)'),
                name=u'filename chk')
        self.chk_filename.default = True
        self.chk_filename.SetValue(self.chk_filename.default)
        
        self.chk_filename.Bind(wx.EVT_CHECKBOX, self.OnSetCustomFilename)
        
        # --- NAME (menu)
        self.name_text = wx.StaticText(self, label=GT(u'Name'), name=u'name*')
        
        self.name_input = wx.TextCtrl(self, name=u'Name')
        self.name_input.req = True
        self.name_input.default = wx.EmptyString
        self.options_input.append(self.name_input)
        
        # --- EXECUTABLE
        self.exe_text = wx.StaticText(self, label=GT(u'Executable'), name=u'exec')
        
        self.exe_input = wx.TextCtrl(self, name=u'Exec')
        self.exe_input.default = wx.EmptyString
        self.options_input.append(self.exe_input)
        
        # --- COMMENT
        self.comm_text = wx.StaticText(self, label=GT(u'Comment'), name=u'comment')
        
        self.comm_input = wx.TextCtrl(self, name=u'Comment')
        self.comm_input.default = wx.EmptyString
        self.options_input.append(self.comm_input)
        
        # --- ICON
        self.icon_text = wx.StaticText(self, label=GT(u'Icon'), name=u'icon')
        
        self.icon_input = wx.TextCtrl(self, name=u'Icon')
        self.icon_input.default = wx.EmptyString
        self.options_input.append(self.icon_input)
        
        # --- TYPE
        self.type_opt = (u'Application', u'Link', u'FSDevice', u'Directory')
        self.type_text = wx.StaticText(self, label=GT(u'Type'), name=u'type')
        
        self.type_choice = OwnerDrawnComboBox(self, value=self.type_opt[0], choices=self.type_opt, name=u'Type')
        self.type_choice.default = self.type_choice.GetValue()
        self.options_input.append(self.type_choice)
        
        # --- TERMINAL
        self.term_opt = (u'true', u'false')
        self.term_text = wx.StaticText(self, label=GT(u'Terminal'), name=u'terminal')
        
        self.term_choice = wx.Choice(self, choices=self.term_opt, name=u'Terminal')
        self.term_choice.default = 1
        self.term_choice.SetSelection(self.term_choice.default)
        self.options_choice.append(self.term_choice)
        
        # --- STARTUP NOTIFY
        self.notify_opt = (u'true', u'false')
        self.notify_text = wx.StaticText(self, label=GT(u'Startup Notify'), name=u'startupnotify')
        
        self.notify_choice = wx.Choice(self, choices=self.notify_opt, name=u'StartupNotify')
        self.notify_choice.default = 0
        self.notify_choice.SetSelection(self.notify_choice.default)
        self.options_choice.append(self.notify_choice)
        
        # --- ENCODING
        self.enc_opt = (
            u'UTF-1', u'UTF-7', u'UTF-8', u'CESU-8', u'UTF-EBCDIC',
            u'UTF-16', u'UTF-32', u'SCSU', u'BOCU-1', u'Punycode',
            u'GB 18030',
            )
        self.enc_text = wx.StaticText(self, label=GT(u'Encoding'), name=u'encoding')
        
        self.enc_input = OwnerDrawnComboBox(self, value=self.enc_opt[2], choices=self.enc_opt, name=u'Encoding')
        self.enc_input.default = self.enc_input.GetValue()
        self.options_input.append(self.enc_input)
        
        # --- CATEGORIES
        self.cat_opt = (
            u'2DGraphics',
            u'Accessibility', u'Application', u'ArcadeGame', u'Archiving', u'Audio', u'AudioVideo',
            u'BlocksGame', u'BoardGame',
            u'Calculator', u'Calendar', u'CardGame', u'Compression', u'ContactManagement', u'Core',
            u'DesktopSettings', u'Development', u'Dictionary', u'DiscBurning', u'Documentation',
            u'Email',
            u'FileManager', u'FileTransfer',
            u'Game', u'GNOME', u'Graphics', u'GTK',
            u'HardwareSettings',
            u'InstantMessaging',
            u'KDE',
            u'LogicGame',
            u'Math', u'Monitor',
            u'Network',
            u'OCR', u'Office',
            u'P2P', u'PackageManager', u'Photography', u'Player', u'Presentation', u'Printing',
            u'Qt',
            u'RasterGraphics', u'Recorder', u'RemoteAccess',
            u'Scanning', u'Screensaver', u'Security', u'Settings', u'Spreadsheet', u'System',
            u'Telephony', u'TerminalEmulator', u'TextEditor',
            u'Utility',
            u'VectorGraphics', u'Video', u'Viewer',
            u'WordProcessor', u'Wine', u'Wine-Programs-Accessories',
            u'X-GNOME-NetworkSettings', u'X-GNOME-PersonalSettings', u'X-GNOME-SystemSettings',
            u'X-KDE-More', u'X-Red-Hat-Base', u'X-SuSE-ControlCenter-System',
            )
        
        self.cat_text = wx.StaticText(self, label=GT(u'Category'), name=u'category')
        
        # This option does not get set by importing a new project
        self.cat_choice = OwnerDrawnComboBox(self, value=self.cat_opt[0], choices=self.cat_opt,
                name=u'Category')
        self.cat_choice.default = self.cat_choice.GetValue()
        self.options_input.append(self.cat_choice)
        
        self.cat_add = ButtonAdd(self)
        self.cat_add.SetName(u'add category')
        self.cat_del = ButtonDel(self)
        self.cat_del.SetName(u'rm category')
        self.cat_clr = ButtonClear(self)
        self.cat_clr.SetName(u'clear categories')
        
        for B in self.cat_add, self.cat_del, self.cat_clr:
            self.options_button.append(B)
        
        # NOTE: wx 3.0 compat
        if wx.MAJOR_VERSION > 2:
            self.categories = wx.ListCtrl(self)
            self.categories.SetSingleStyle(wx.LC_SINGLE_SEL)
        
        else:
            self.categories = wx.ListCtrl(self, style=wx.LC_SINGLE_SEL|wx.BORDER_SIMPLE)
        
        # For manually setting background color after enable/disable
        self.categories.default_color = self.categories.GetBackgroundColour()
        self.categories.SetName(u'Categories')
        self.options_list.append(self.categories)
        
        
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
        self.other_text = wx.StaticText(self, label=GT(u'Other'), name=u'other')
        
        self.other = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.BORDER_SIMPLE,
                name=self.other_text.Name)
        self.other.default = wx.EmptyString
        self.options_input.append(self.other)
        
        misc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        misc_sizer.Add(self.other, 1, wx.EXPAND)
        
        # GridBagSizer flags
        CENTER = wx.ALIGN_CENTER_VERTICAL
        CENTER_EXPAND = wx.ALIGN_CENTER_VERTICAL|wx.EXPAND
        CENTER_RIGHT = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        
        sizer1 = wx.GridBagSizer(5, 5)
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
        sizer1.Add(self.type_choice, (1, 3), flag=CENTER_EXPAND)
        
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
        sizer1.Add(self.enc_input, (4, 3), flag=CENTER_EXPAND)
        
        
        self.border = wx.StaticBox(self, -1, size=(20,20))
        border_box = wx.StaticBoxSizer(self.border, wx.VERTICAL)
        
        border_box.Add(sizer1, 0, wx.EXPAND|wx.BOTTOM, 5)
        border_box.Add(cat_sizer2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        border_box.AddSpacer(5)
        border_box.Add(self.other_text, 0)
        border_box.Add(self.other, 1, wx.EXPAND)
        
        
        self.OnToggle()
        
        # --- Page 5 Sizer --- #
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page_sizer.AddSpacer(5)
        page_sizer.Add(button_sizer, 0, wx.LEFT, 5)
        page_sizer.AddSpacer(10)
        page_sizer.Add(self.activate, 0, wx.LEFT, 5)
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
            self.btn_open: u'Open',
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
        
        
        SetPageToolTips(self)
    
    
    def GatherData(self):
        if self.activate.GetValue():
            data = self.GetLauncherInfo()
            data = u'\n'.join(data.split(u'\n')[1:])
            
            if not self.chk_filename.GetValue():
                data = u'[FILENAME={}]\n{}'.format(self.input_filename.GetValue(), data)
            
            return u'<<MENU>>\n1\n{}\n<</MENU>>'.format(data)
        
        else:
            return u'<<MENU>>\n0\n<</MENU>>'
    
    
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
        
        desktop_list.append(u'Terminal={}'.format(unicode(self.term_choice.GetSelection() == 0).lower()))
        
        desktop_list.append(u'StartupNotify={}'.format(unicode(self.notify_choice.GetSelection() == 0).lower()))
        
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
        
        other = self.other.GetValue()
        if not TextIsEmpty(other):
            desktop_list.append(other)
        
        return u'\n'.join(desktop_list)
    
    
    ## Retrieves the filename to be used for the menu launcher
    def GetOutputFilename(self):
        if not self.chk_filename.GetValue():
            filename = self.input_filename.GetValue().strip(u' ').replace(u' ', u'_')
            if not TextIsEmpty(filename):
                return filename
        
        return self.name_input.GetValue().strip(u' ').replace(u' ', u'_')
    
    
    ## Loads a .desktop launcher's data
    def OnLoadLauncher(self, event=None):
        cont = False
        if wx.GetApp().GetTopWindow().cust_dias.IsChecked():
            dia = OpenFile(self, GT(u'Open Launcher'))
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
    
    
    ## Saves launcher information to file
    def OnSaveLauncher(self, event):
        # Get data to write to control file
        menu_data = self.GetLauncherInfo()
        
        # Saving?
        cont = False
        
        # Open a "Save Dialog"
        if wx.GetApp().GetTopWindow().cust_dias.IsChecked():
            dia = SaveFile(self, GT(u'Save Launcher'))
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
    
    
    ## TODO: Doxygen
    def OnToggle(self, event=None):
        enable = self.activate.IsChecked()
        
        listctrl_bgcolor_defs = {
            True: self.categories.default_color,
            False: wx.Colour(214, 214, 214),
        }
        
        for group in self.options_button, self.options_choice, self.options_input, self.options_list:
            for O in group:
                O.Enable(enable)
                
                # Small hack to gray-out ListCtrl when disabled
                if isinstance(O, wx.ListCtrl):
                    O.SetBackgroundColour(listctrl_bgcolor_defs[enable])
        
        self.chk_filename.Enable(enable)
        self.OnSetCustomFilename()
    
    
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
        self.other.Clear()
        self.activate.SetValue(self.activate.default)
        self.OnToggle()
    
    
    ## TODO: Doxygen
    def SetCategory(self, event):
        try:
            ID = event.GetKeyCode()
        except AttributeError:
            ID = event.GetEventObject().GetId()
        
        cat = self.cat_choice.GetValue()
        cat = cat.split()
        cat = u''.join(cat)
        
        if ID == wx.WXK_RETURN or ID == wx.WXK_NUMPAD_ENTER:
            self.categories.InsertStringItem(self.categories.GetItemCount(), cat)
        
        elif ID == wx.WXK_DELETE:
            if self.categories.GetItemCount() and self.categories.GetSelectedItemCount():
                cur_cat = self.categories.GetFirstSelected()
                self.categories.DeleteItem(cur_cat)
        
        elif ID == wx.ID_CLEAR:
            if self.categories.GetItemCount():
                confirm = wx.MessageDialog(self, GT(u'Clear categories?'), GT(u'Confirm'),
                        wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                
                if confirm.ShowModal() == wx.ID_YES:
                    self.categories.DeleteAllItems()
        
        event.Skip()
    
    
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
                self.other.WriteText(u'{}={}'.format(K, data_defs[K]))
        
        if misc_defs:
            for K in misc_defs:
                value = misc_defs[K]
                if not TextIsEmpty(value):
                    if K == u'FILENAME':
                        self.input_filename.SetValue(value)
                        self.chk_filename.SetValue(False)
        
        self.OnToggle()
