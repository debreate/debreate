# -*- coding: utf-8 -*-

## \package wiz_bin.menu


import wx, os, shutil

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonBrowse64
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonDel
from dbr.buttons        import ButtonPreview64
from dbr.buttons        import ButtonSave64
from dbr.dialogs        import GetFileOpenDialog
from dbr.dialogs        import GetFileSaveDialog
from dbr.dialogs        import ShowDialog
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from dbr.log            import Logger
from dbr.wizard         import WizardPage
from globals.errorcodes import dbrerrno
from globals.ident      import ID_MENU
from globals.tooltips   import SetPageToolTips


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_MENU)
        
        # Allows executing parent methods
        self.parent = parent
        
        ## Override default label
        self.label = GT(u'Menu Launcher')
        
        # --- Main Menu Entry --- #
        
        self.options_button = []
        self.options_input = []
        self.options_choice = []
        self.options_list = []
        
        # --- Buttons to open/preview/save .desktop file
        self.btn_open = ButtonBrowse64(self)
        self.btn_open.SetName(u'open')
        self.options_button.append(self.btn_open)
        
        self.btn_save = ButtonSave64(self)
        self.btn_save.SetName(u'export')
        self.options_button.append(self.btn_save)
        
        self.btn_preview = ButtonPreview64(self)
        self.btn_preview.SetName(u'preview')
        self.options_button.append(self.btn_preview)
        
        self.btn_open.Bind(wx.EVT_BUTTON, self.OpenFile)
        wx.EVT_BUTTON(self.btn_save, wx.ID_ANY, self.OnSave)
        wx.EVT_BUTTON(self.btn_preview, wx.ID_ANY, self.OnPreview)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.btn_open, 0)
        button_sizer.Add(self.btn_save, 0)
        button_sizer.Add(self.btn_preview, 0)
        
        # --- CHECKBOX
        self.activate = wx.CheckBox(self, -1, GT(u'Create system menu launcher'))
        self.activate.default = False
        
        self.activate.Bind(wx.EVT_CHECKBOX, self.OnToggle)
        
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
        
        self.type_choice = wx.ComboBox(self, -1, value=self.type_opt[0], choices=self.type_opt, name=u'Type')
        self.type_choice.default = self.type_choice.GetValue()
        self.options_input.append(self.type_choice)
        
        # --- TERMINAL
        self.term_opt = (u'true', u'false')
        self.term_text = wx.StaticText(self, label=GT(u'Terminal'), name=u'terminal')
        
        self.term_choice = wx.Choice(self, -1, choices=self.term_opt, name=u'Terminal')
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
        self.enc_opt = (u'UTF-1',u'UTF-7',u'UTF-8',u'CESU-8',u'UTF-EBCDIC',
                u'UTF-16',u'UTF-32',u'SCSU',u'BOCU-1',u'Punycode', u'GB 18030')
        self.enc_text = wx.StaticText(self, label=GT(u'Encoding'), name=u'encoding')
        
        self.enc_input = wx.ComboBox(self, -1, value=self.enc_opt[2], choices=self.enc_opt, name=u'Encoding')
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
        self.cat_choice = wx.ComboBox(self, -1, value=self.cat_opt[0], choices=self.cat_opt,
                name=self.cat_text.GetLabel())
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
        
        # NOTE: wx. 3.0 compat
        if wx.MAJOR_VERSION > 3:
            self.categories = wx.ListCtrl(self, -1, style=wx.LC_SINGLE_SEL|wx.BORDER_SIMPLE)
            self.categories.InsertColumn(0, u'')
        
        else:
            self.categories = wx.ListCtrl(self, -1)
            self.categories.SetSingleStyle(wx.LC_SINGLE_SEL)
        
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
        
        self.other = wx.TextCtrl(self, name=self.other_text.Name, style=wx.TE_MULTILINE|wx.BORDER_SIMPLE)
        self.other.default = wx.EmptyString
        self.options_input.append(self.other)
        
        misc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        misc_sizer.Add(self.other, 1, wx.EXPAND)
        
        # Organize the widgets and create a nice border
        sizer1 = wx.FlexGridSizer(0, 4, 5, 5)
        sizer1.AddGrowableCol(1)
        sizer1.AddMany( [
            (self.name_text, 0, wx.TOP, 10),(self.name_input, 0, wx.EXPAND|wx.TOP, 10),
            (self.type_text, 0, wx.TOP, 10),(self.type_choice, 0, wx.TOP, 10),
            (self.exe_text),(self.exe_input, 0, wx.EXPAND),
            (self.term_text),(self.term_choice),
            (self.comm_text),(self.comm_input, 0, wx.EXPAND),
            (self.notify_text),(self.notify_choice),
            (self.icon_text),(self.icon_input, 0, wx.EXPAND),
            (self.enc_text),(self.enc_input, 0, wx.EXPAND),
            ] )
        
        self.border = wx.StaticBox(self, -1, size=(20,20))
        border_box = wx.StaticBoxSizer(self.border, wx.VERTICAL)
        border_box.Add(sizer1, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        border_box.Add(cat_sizer2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        border_box.AddSpacer(20)
        border_box.Add(self.other_text, 0, wx.LEFT, 6)
        border_box.Add(self.other, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        
        
        self.OnToggle()  # Initially disable widgets
        
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
        # FIXME: Deprecated???
        self.standards = {    u'name': self.name_input, u'type': self.type_choice, u'exec': self.exe_input,
                            u'comment': self.comm_input, u'terminal': self.term_choice,
                            u'startupnotify': self.notify_choice, u'encoding': self.enc_input,
                            u'categories': self.categories
                            }
        
        # Lists of widgets that change language
        # FIXME: deprecated???
        self.setlabels = {    self.activate: u'Menu', self.btn_open: u'Open', self.border: u'Border',
                            self.icon_text: u'Icon',
                            self.name_text: u'Name', self.comm_text: u'Comm', self.exe_text: u'Exec',
                            self.enc_text: u'Enc', self.type_text: u'Type', self.cat_text: u'Cat',
                            self.term_text: u'Term', self.notify_text: u'Notify'}
        
        
        SetPageToolTips(self)
    
    
    ## TODO: Doxygen
    def Export(self, out_dir, out_name=wx.EmptyString, executable=False):
        ret_code = WizardPage.Export(self, out_dir, out_name=out_name)
        
        absolute_filename = u'{}/{}'.format(out_dir, out_name).replace(u'//', u'/')
        if executable:
            os.chmod(absolute_filename, 0755)
        
        return ret_code
    
    
    ## TODO: Doxygen
    def ExportBuild(self, stage):
        stage = u'{}/usr/share/applications'.format(stage).replace(u'//', u'/')
        
        if not os.path.isdir(stage):
            os.makedirs(stage)
        
        ret_code = self.Export(stage, u'{}.desktop'.format(self.name_input.GetValue()), True)
        if ret_code:
            return (ret_code, GT(u'Could not export menu launcher'))
        
        return (0, None)
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        return self.activate.IsChecked()
    
    
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
    
    
    ## TODO: Doxygen
    def GetMenuInfo(self):
        # Create list to store info
        desktop_list = [u'[Desktop Entry]']
        
        # Add Name
        name = self.name_input.GetValue()
        if not TextIsEmpty(name):
            desktop_list.append(u'Name={}'.format(name))
        
        # Add Version
        desktop_list.append(u'Version=1.0')
        
        # Add Executable
        exe = self.exe_input.GetValue()
        if not TextIsEmpty(exe):
            desktop_list.append(u'Exec={}'.format(exe))
        
        # Add Comment
        comm = self.comm_input.GetValue()
        if not TextIsEmpty(comm):
            desktop_list.append(u'Comment={}'.format(comm))
        
        # Add Icon
        icon = self.icon_input.GetValue()
        if not TextIsEmpty(icon):
            desktop_list.append(u'Icon={}'.format(icon))
        
        # Add Type
        #type = self.type_opt[self.type_choice.GetSelection()]
        m_type = self.type_choice.GetValue()
        if not TextIsEmpty(m_type):
            desktop_list.append(u'Type={}'.format(m_type))
        
        # Add Terminal
        desktop_list.append(u'Terminal={}'.format(unicode(self.term_choice.GetSelection() == 0).lower()))
        
        # Add Startup Notify
        desktop_list.append(u'StartupNotify={}'.format(unicode(self.notify_choice.GetSelection() == 0).lower()))
        
        # Add Encoding
        enc = self.enc_input.GetValue()
        if not TextIsEmpty(enc):
            desktop_list.append(u'Encoding={}'.format(enc))
        
        # Add Categories
        cat_list = []
        cat_total = self.categories.GetItemCount()
        count = 0
        while count < cat_total:
            cat_list.append(self.categories.GetItemText(count))
            count += 1
        
        if len(cat_list):
            # Add a final semi-colon if categories is not empty
            cat_list[-1] = u'%s;' % cat_list[-1]
            
            desktop_list.append(u'Categories={}'.format(u';'.join(cat_list)))
        
        # Add Misc
        other = self.other.GetValue()
        if not TextIsEmpty(other):
            desktop_list.append(other)
        
        return u'\n'.join(desktop_list)
    
    
    ## TODO: Doxygen
    def SetCategory(self, event):
        try:
            key_code = event.GetKeyCode()
        except AttributeError:
            key_code = event.GetEventObject().GetId()
        
        cat = self.cat_choice.GetValue()
        cat = cat.split()
        cat = u''.join(cat)
        
        if key_code == wx.WXK_RETURN or key_code == wx.WXK_NUMPAD_ENTER:
            self.categories.InsertStringItem(0, cat)
        
        elif key_code == wx.WXK_DELETE:
            cur_cat = self.categories.GetFirstSelected()
            self.categories.DeleteItem(cur_cat)
        
        elif key_code == wx.WXK_ESCAPE:
            confirm = wx.MessageDialog(self, GT(u'Delete all categories?'), GT(u'Confirm'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if confirm.ShowModal() == wx.ID_YES:
                self.categories.DeleteAllItems()
        event.Skip()
    
    
    
    ## TODO: Doxygen
    def OnSave(self, event):
        # Get data to write to control file
        menu_data = self.GetMenuInfo().encode(u'utf-8')
        menu_data = menu_data.split(u'\n')
        menu_data = u'\n'.join(menu_data[1:])
        
        # Saving?
        cont = False
        
        # Open a u'Save Dialog'
        dia = GetFileSaveDialog(self.GetDebreateWindow(), GT(u'Save Launcher'), u'All files|*')
        if ShowDialog(dia):
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
            
            f_opened = open(path, u'w')
            try:
                f_opened.write(menu_data)
                f_opened.close()
                if overwrite:
                    os.remove(backup)
            except UnicodeEncodeError:
                serr = GT(u'Save failed')
                uni = GT(u'Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                UniErr = wx.MessageDialog(self, u'%s\n\n%s' % (serr, uni), GT(u'Unicode Error'), style=wx.OK|wx.ICON_EXCLAMATION)
                UniErr.ShowModal()
                f_opened.close()
                os.remove(path)
                # Restore from backup
                shutil.move(backup, path)
    
    
    ## TODO: Doxygen
    def OpenFile(self, event):
        cont = False
        
        dia = GetFileOpenDialog(self.GetDebreateWindow(), GT(u'Open Launcher'), u'All files|*')
        if ShowDialog(dia):
            cont = True
        
        if cont == True:
            path = dia.GetPath()
            f_opened = open(path, u'r')
            text = f_opened.read()
            f_opened.close()
            data = text.split(u'\n')
            if data[0] == u'[Desktop Entry]':
                data = data[1:]
                # First line needs to be changed to '1'
            data.insert(0, u'1')
            self.SetFieldDataLegacy(u'\n'.join(data))
    
    
    ## TODO: Doxygen
    def OnPreview(self, event):
        # Show a preview of the .desktop config file
        config = self.GetMenuInfo()
        
        dia = wx.Dialog(self, -1, GT(u'Preview'), size=(500,400))
        preview = wx.TextCtrl(dia, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        preview.SetValue(config)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    
    ## TODO: Doxygen
    def SetFieldDataLegacy(self, data):
        # Clear all fields first
        self.ResetPageInfo()
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
                self.other.SetValue(u'\n'.join(leftovers))
        self.OnToggle(None)
    
    
    ## Retrieves Desktop Entry file information
    #  
    #  \return
    #        \b \e tuple(str, str, str) : File/Page name,
    #          string formatted menu information, & filename to output
    def GetPageInfo(self):
        if not self.activate.GetValue():
            return None
        
        return(__name__, self.GetMenuInfo(), u'MENU')
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, filename):
        Logger.Debug(__name__, GT(u'Importing page info from {}').format(filename))
        
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        FILE = open(filename, u'r')
        menu_data = FILE.read().split(u'\n')
        FILE.close()
        
        if menu_data[0] == u'[Desktop Entry]':
            menu_data.remove(menu_data[0])
        
        menu_definitions = {}
        unused_raw_lines = []
        
        for L in menu_data:
            if u'=' in L:
                key = L.split(u'=')
                value = key[-1]
                key = key[0]
                
                menu_definitions[key] = value
                
                continue
            
            # Any unrecognizable lines will be added to "Other" section
            unused_raw_lines.append(L)
        
        
        def set_value(option):
            key = option.GetName()
            value = None
            
            if key in menu_definitions:
                value = menu_definitions[key]
                
                if not TextIsEmpty(value):
                    if option in self.options_input:
                        option.SetValue(value)
                        return True
                    
                    elif option in self.options_choice:
                        if option.SetStringSelection(value):
                            return True
                    
                    elif option in self.options_list:
                        if key == self.categories.GetName():
                            value = value.split(u';')
                            
                            if value:
                                for X, val in enumerate(value):
                                    self.categories.InsertStringItem(X, val)
                                return True
            
            return False
                    
        
        categories_used = []
        menu_changed = False
        
        for group in self.options_input, self.options_choice, self.options_list:
            for O in group:
                if set_value(O):
                    menu_changed = True
                    categories_used.append(O.GetName())
        
        
        # List of keys that can be ignored if unused
        bypass_unused = (
            u'Version',
        )
        
        categories_unused = []
        for key in menu_definitions:
            if key not in categories_used and key not in bypass_unused:
                categories_unused.append(u'{}={}'.format(key, menu_definitions[key]))
        
        categories_unused += unused_raw_lines
        if len(categories_unused):
            categories_unused = u'\n'.join(categories_unused)
            
            self.other.SetValue(categories_unused)
        
        self.activate.SetValue(menu_changed)
        self.OnToggle()
        
        return 0
    
    
    ## TODO: Doxygen
    def ResetPageInfo(self):
        self.activate.SetValue(self.activate.default)
        self.OnToggle()
        
        for O in self.options_input:
            O.SetValue(O.default)
        
        for O in self.options_choice:
            O.SetSelection(O.default)
        
        for O in self.options_list:
            O.DeleteAllItems()
