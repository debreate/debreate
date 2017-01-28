# -*- coding: utf-8 -*-

## \package ui.launcher

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, wx

from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from globals.errorcodes     import dbrerrno
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.ident          import page_ids
from globals.strings        import TextIsEmpty, GS
from globals.wizardhelper   import GetMainWindow
from input.list             import ListCtrlPanelESS
from input.select           import ChoiceESS
from input.select           import ComboBoxESS
from input.text             import TextAreaESS
from input.text             import TextAreaPanelESS
from ui.button              import ButtonAdd
from ui.button              import ButtonBrowse64
from ui.button              import ButtonClear
from ui.button              import ButtonPreview64
from ui.button              import ButtonRemove
from ui.button              import ButtonSave64
from ui.dialog              import ConfirmationDialog
from ui.dialog              import GetFileOpenDialog
from ui.dialog              import GetFileSaveDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.panel               import ScrolledPanel
from ui.textpreview         import TextPreview
from ui.wizard              import WizardPage


## Template for individual launchers
class LauncherTemplate(ScrolledPanel):
    def __init__(self, parent, win_id=wx.ID_ANY, name=u'launcher'):
        ScrolledPanel.__init__(self, parent, win_id, name=name)
        
        self.opts_button = []
        self.opts_input = []
        self.opts_choice = []
        self.opts_list = []
        
        self.labels = []
        
        # --- Buttons to open/preview/save .desktop file
        btn_open = ButtonBrowse64(self)
        btn_open.SetName(u'open')
        
        btn_save = ButtonSave64(self)
        btn_save.SetName(u'export')
        self.opts_button.append(btn_save)
        
        btn_preview = ButtonPreview64(self)
        btn_preview.SetName(u'preview')
        self.opts_button.append(btn_preview)
        
        # --- NAME (menu)
        txt_name = wx.StaticText(self, label=GT(u'Name'), name=u'name*')
        self.labels.append(txt_name)
        self.ti_name = TextAreaESS(self, name=u'Name')
        self.ti_name.req = True
        self.ti_name.default = wx.EmptyString
        self.opts_input.append(self.ti_name)
        
        # --- EXECUTABLE
        txt_exec = wx.StaticText(self, label=GT(u'Executable'), name=u'exec')
        self.labels.append(txt_exec)
        
        self.ti_exec = TextAreaESS(self, name=u'Exec')
        self.ti_exec.default = wx.EmptyString
        self.opts_input.append(self.ti_exec)
        
        # --- COMMENT
        txt_comm = wx.StaticText(self, label=GT(u'Comment'), name=u'comment')
        self.labels.append(txt_comm)
        
        self.ti_comm = TextAreaESS(self, name=u'Comment')
        self.ti_comm.default = wx.EmptyString
        self.opts_input.append(self.ti_comm)
        
        # --- ICON
        txt_icon = wx.StaticText(self, label=GT(u'Icon'), name=u'icon')
        self.labels.append(txt_icon)
        
        self.ti_icon = TextAreaESS(self, name=u'Icon')
        self.ti_icon.default = wx.EmptyString
        self.opts_input.append(self.ti_icon)
        
        # --- TYPE
        opts_type = (u'Application', u'Link', u'Directory',)
        
        txt_type = wx.StaticText(self, label=GT(u'Type'), name=u'type')
        self.labels.append(txt_type)
        
        self.ti_type = ComboBoxESS(self, value=opts_type[0], choices=opts_type, name=u'Type')
        self.ti_type.default = self.ti_type.GetValue()
        self.opts_input.append(self.ti_type)
        
        # --- TERMINAL
        opts_term = (u'true', u'false',)
        
        txt_term = wx.StaticText(self, label=GT(u'Terminal'), name=u'terminal')
        self.labels.append(txt_term)
        
        self.sel_term = ChoiceESS(self, choices=opts_term, name=u'Terminal')
        self.sel_term.default = 1
        self.sel_term.SetSelection(self.sel_term.default)
        self.opts_choice.append(self.sel_term)
        
        # --- STARTUP NOTIFY
        self.notify_opt = (u'true', u'false',)
        
        txt_notify = wx.StaticText(self, label=GT(u'Startup Notify'), name=u'startupnotify')
        self.labels.append(txt_notify)
        
        self.sel_notify = ChoiceESS(self, choices=self.notify_opt, name=u'StartupNotify')
        self.sel_notify.default = 0
        self.sel_notify.SetSelection(self.sel_notify.default)
        self.opts_choice.append(self.sel_notify)
        
        # --- ENCODING
        opts_enc = (
            u'UTF-1', u'UTF-7', u'UTF-8', u'CESU-8', u'UTF-EBCDIC',
            u'UTF-16', u'UTF-32', u'SCSU', u'BOCU-1', u'Punycode',
            u'GB 18030',
            )
        
        txt_enc = wx.StaticText(self, label=GT(u'Encoding'), name=u'encoding')
        self.labels.append(txt_enc)
        
        self.ti_enc = ComboBoxESS(self, value=opts_enc[2], choices=opts_enc, name=u'Encoding')
        self.ti_enc.default = self.ti_enc.GetValue()
        self.opts_input.append(self.ti_enc)
        
        # --- CATEGORIES
        opts_category = (
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
        
        txt_category = wx.StaticText(self, label=GT(u'Category'), name=u'category')
        self.labels.append(txt_category)
        
        # This option does not get set by importing a new project
        self.ti_category = ComboBoxESS(self, value=opts_category[0], choices=opts_category,
                name=txt_category.Name)
        self.ti_category.default = self.ti_category.GetValue()
        self.opts_input.append(self.ti_category)
        
        btn_catadd = ButtonAdd(self, name=u'add category')
        btn_catdel = ButtonRemove(self, name=u'rm category')
        btn_catclr = ButtonClear(self, name=u'clear categories')
        
        for B in btn_catadd, btn_catdel, btn_catclr:
            self.opts_button.append(B)
        
        # FIXME: Allow using multi-select + remove
        self.lst_categories = ListCtrlPanelESS(self)
        # Can't set LC_SINGLE_SEL in constructor for wx 3.0 (ListCtrlPanel bug???)
        self.lst_categories.SetSingleStyle(wx.LC_SINGLE_SEL)
        
        # For manually setting background color after enable/disable
        self.lst_categories.default_color = self.lst_categories.GetBackgroundColour()
        self.lst_categories.SetName(u'Categories')
        self.opts_list.append(self.lst_categories)
        
        # ----- MISC
        txt_other = wx.StaticText(self, label=GT(u'Other'), name=u'other')
        self.labels.append(txt_other)
        
        self.ti_other = TextAreaPanelESS(self, name=txt_other.Name)
        self.ti_other.default = wx.EmptyString
        self.ti_other.EnableDropTarget()
        self.opts_input.append(self.ti_other)
        
        #self.OnToggle()
        
        # *** Layout *** #
        
        CENTER_EXPAND = wx.ALIGN_CENTER_VERTICAL|wx.EXPAND
        LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        RIGHT_CENTER = wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL
        
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_open, 0)
        lyt_buttons.Add(btn_save, 0)
        lyt_buttons.Add(btn_preview, 0)
        
        lyt_cat_btn = BoxSizer(wx.HORIZONTAL)
        lyt_cat_btn.Add(btn_catadd, 0)
        lyt_cat_btn.Add(btn_catdel, 0)
        lyt_cat_btn.Add(btn_catclr, 0)
        
        lyt_cat_input = BoxSizer(wx.VERTICAL)
        lyt_cat_input.Add(txt_category, 0, LEFT_BOTTOM)
        lyt_cat_input.Add(self.ti_category, 0, wx.TOP|wx.BOTTOM, 5)
        lyt_cat_input.Add(lyt_cat_btn, 0)
        
        lyt_cat_main = BoxSizer(wx.HORIZONTAL)
        lyt_cat_main.Add(lyt_cat_input, 0)
        lyt_cat_main.Add(self.lst_categories, 1, wx.EXPAND|wx.LEFT, 5)
        
        lyt_grid = wx.GridBagSizer(5, 5)
        lyt_grid.SetCols(4)
        lyt_grid.AddGrowableCol(1)
        
        row = 0
        lyt_grid.Add(txt_name, (row, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(self.ti_name, (row, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_type, (row, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(self.ti_type, (row, 3), flag=CENTER_EXPAND)
        
        row += 1
        lyt_grid.Add(txt_exec, (row, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(self.ti_exec, (row, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_term, (row, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(self.sel_term, (row, 3), flag=LEFT_CENTER)
        
        row += 1
        lyt_grid.Add(txt_comm, (row, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(self.ti_comm, (row, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_notify, (row, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(self.sel_notify, (row, 3), flag=LEFT_CENTER)
        
        row += 1
        lyt_grid.Add(txt_icon, (row, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(self.ti_icon, (row, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_enc, (row, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(self.ti_enc, (row, 3), flag=CENTER_EXPAND)
        
        lyt_border = BoxSizer(wx.VERTICAL)
        
        lyt_border.Add(lyt_grid, 0, wx.EXPAND|wx.BOTTOM, 5)
        lyt_border.Add(lyt_cat_main, 0, wx.EXPAND|wx.TOP, 5)
        lyt_border.AddSpacer(5)
        lyt_border.Add(txt_other, 0)
        lyt_border.Add(self.ti_other, 1, wx.EXPAND)
        
        # --- Page 5 Sizer --- #
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_buttons, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, 5)
        lyt_main.Add(lyt_border, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
        btn_save.Bind(wx.EVT_BUTTON, self.OnSaveLauncher)
        btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewLauncher)
        
        wx.EVT_KEY_DOWN(self.ti_category, self.SetCategory)
        wx.EVT_KEY_DOWN(self.lst_categories, self.SetCategory)
        btn_catadd.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catdel.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catclr.Bind(wx.EVT_BUTTON, self.SetCategory)
    
    
    ## TODO: Doxygen
    def Export(self, out_dir, out_name=wx.EmptyString, executable=False):
        if out_name == wx.EmptyString:
            out_name = page_ids[self.GetId()].upper()
        
        ret_code = WizardPage.Export(self, out_dir, out_name)
        
        absolute_filename = u'{}/{}'.format(out_dir, out_name).replace(u'//', u'/')
        if executable:
            os.chmod(absolute_filename, 0755)
        
        Logger.Debug(__name__, GT(u'Output filename: {}').format(out_name))
        
        return ret_code
    
    
    ## TODO: Doxygen
    def ExportBuild(self, stage):
        stage = u'{}/usr/share/applications'.format(stage).replace(u'//', u'/')
        
        if not os.path.isdir(stage):
            os.makedirs(stage)
        
        ret_code = self.Export(stage, u'{}.desktop'.format(self.GetOutputFilename()))
        if ret_code:
            return (ret_code, GT(u'Could not export menu launcher'))
        
        return (0, None)
    
    
    ## Retrieves Desktop Entry file information
    #  
    #  \return
    #        \b \e tuple(str, str, str) : File/Page name,
    #          string formatted menu information, & filename to output
    def Get(self, get_module=False):
        page = self.GetLauncherInfo()
        
        if get_module:
            # FIXME: 'MENU' needed?
            page = (__name__, page, u'MENU')
        
        return page
    
    
    ## Formats the launcher information for export
    def GetLauncherInfo(self):
        desktop_list = [u'[Desktop Entry]']
        
        name = self.ti_name.GetValue()
        if not TextIsEmpty(name):
            desktop_list.append(u'Name={}'.format(name))
        
        desktop_list.append(u'Version=1.0')
        
        executable = self.ti_exec.GetValue()
        if not TextIsEmpty(executable):
            desktop_list.append(u'Exec={}'.format(executable))
        
        comment = self.ti_comm.GetValue()
        if not TextIsEmpty(comment):
            desktop_list.append(u'Comment={}'.format(comment))
        
        icon = self.ti_icon.GetValue()
        if not TextIsEmpty(icon):
            desktop_list.append(u'Icon={}'.format(icon))
        
        launcher_type = self.ti_type.GetValue()
        if not TextIsEmpty(launcher_type):
            desktop_list.append(u'Type={}'.format(launcher_type))
        
        desktop_list.append(u'Terminal={}'.format(GS(self.sel_term.GetSelection() == 0).lower()))
        
        desktop_list.append(u'StartupNotify={}'.format(GS(self.sel_notify.GetSelection() == 0).lower()))
        
        encoding = self.ti_enc.GetValue()
        if not TextIsEmpty(encoding):
            desktop_list.append(u'Encoding={}'.format(encoding))
        
        categories = []
        cat_total = self.lst_categories.GetItemCount()
        count = 0
        while count < cat_total:
            C = self.lst_categories.GetItemText(count)
            if not TextIsEmpty(C):
                categories.append(self.lst_categories.GetItemText(count))
            
            count += 1
        
        # Add a final semi-colon if categories is not empty
        if categories:
            categories = u';'.join(categories)
            if categories[-1] != u';':
                categories = u'{};'.format(categories)
            
            desktop_list.append(u'Categories={}'.format(categories))
        
        other = self.ti_other.GetValue()
        if not TextIsEmpty(other):
            desktop_list.append(other)
        
        return u'\n'.join(desktop_list)
    
    
    ## Retrieves the filename to be used for the menu launcher
    def GetOutputFilename(self):
        # FIXME: Use tab 'name' or 'title' attribute
        return self.ti_name.GetValue().strip(u' ').replace(u' ', u'_')
    
    
    ## Overrides ui.wizard.GetRequiredField
    def GetRequiredFields(self, children=None):
        required_fields = list(WizardPage.GetRequiredFields(self, children=children))
        
        return tuple(required_fields)
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
        Logger.Debug(__name__, GT(u'Importing page info from {}').format(filename))
        
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        menu_data = ReadFile(filename, split=True, convert=list)
        
        if u'[Desktop Entry]' in menu_data[0]:
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
                    if option in self.opts_input:
                        option.SetValue(value)
                        return True
                    
                    elif option in self.opts_choice:
                        if option.SetStringSelection(value):
                            return True
                    
                    elif option in self.opts_list:
                        if key == self.lst_categories.GetName():
                            value = value.split(u';')
                            
                            if value:
                                for X, val in enumerate(value):
                                    self.lst_categories.InsertStringItem(X, val)
                                return True
            
            return False
        
        categories_used = []
        
        for group in self.opts_input, self.opts_choice, self.opts_list:
            for O in group:
                if set_value(O):
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
            
            self.ti_other.SetValue(categories_unused)
        
        return 0
    
    
    ## Loads a .desktop launcher's data
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnSaveLauncher)
    #         'Others' field not being completely filled out.
    def OnLoadLauncher(self, event=None):
        dia = GetFileOpenDialog(GetMainWindow(), GT(u'Open Launcher'))
        
        if ShowDialog(dia):
            path = dia.GetPath()
            
            data = ReadFile(path, split=True, convert=list)
            
            # Remove unneeded lines
            if data[0] == u'[Desktop Entry]':
                data = data[1:]
            
            self.Reset()
            # First line needs to be changed to '1'
            data.insert(0, u'1')
            self.Set(u'\n'.join(data))
    
    
    ## TODO: Doxygen
    def OnPreviewLauncher(self, event=None):
        # Show a preview of the .desktop config file
        config = self.GetLauncherInfo()
        
        dia = TextPreview(title=GT(u'Menu Launcher Preview'),
                text=config, size=(500,400))
        
        dia.ShowModal()
        dia.Destroy()
    
    
    ## Saves launcher information to file
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnLoadLauncher)
    #         'Others' field not being completely filled out.
    def OnSaveLauncher(self, event=None):
        Logger.Debug(__name__, u'Export launcher ...')
        
        # Get data to write to control file
        menu_data = self.GetLauncherInfo().encode(u'utf-8')
        
        dia = GetFileSaveDialog(GetMainWindow(), GT(u'Save Launcher'))
        
        if ShowDialog(dia):
            path = dia.GetPath()
            
            # Create a backup file
            overwrite = False
            if os.path.isfile(path):
                backup = u'{}.backup'.format(path)
                shutil.copy(path, backup)
                overwrite = True
            
            try:
                WriteFile(path, menu_data)
                
                if overwrite:
                    os.remove(backup)
            
            except UnicodeEncodeError:
                detail1 = GT(u'Unfortunately Debreate does not support unicode yet.')
                detail2 = GT(u'Remove any non-ASCII characters from your project.')
                
                ShowErrorDialog(GT(u'Save failed'), u'{}\n{}'.format(detail1, detail2), title=GT(u'Unicode Error'))
                
                os.remove(path)
                # Restore from backup
                shutil.move(backup, path)
    
    
    ## TODO: Doxygen
    def Reset(self):
        for O in self.opts_input:
            O.SetValue(O.default)
        
        for O in self.opts_choice:
            O.SetSelection(O.default)
        
        for O in self.opts_list:
            O.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetCategory(self, event=None):
        try:
            ID = event.GetKeyCode()
        
        except AttributeError:
            ID = event.GetEventObject().GetId()
        
        cat = self.ti_category.GetValue()
        cat = cat.split()
        cat = u''.join(cat)
        
        if ID in (wx.ID_ADD, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.lst_categories.InsertStringItem(self.lst_categories.GetItemCount(), cat)
        
        elif ID in (wx.ID_REMOVE, wx.WXK_DELETE):
            if self.lst_categories.GetItemCount() and self.lst_categories.GetSelectedItemCount():
                cur_cat = self.lst_categories.GetFirstSelected()
                self.lst_categories.DeleteItem(cur_cat)
        
        elif ID == wx.ID_CLEAR:
            if self.lst_categories.GetItemCount():
                if ConfirmationDialog(GetMainWindow(), GT(u'Confirm'),
                        GT(u'Clear categories?')).ShowModal() in (wx.ID_OK, wx.OK):
                    self.lst_categories.DeleteAllItems()
        
        if event:
            event.Skip()
    
    
    ## Fills out launcher information from loaded file
    #  
    #  \param data
    #    Information to fill out menu launcher fields
    #  \param enabled
    #    \b \e bool : Launcher will be flagged for export if True
    def Set(self, data):
        # Make sure we are dealing with a list
        if isinstance(data, (unicode, str)):
            data = data.split(u'\n')
        
        # Data list is not empty
        if data:
            Logger.Debug(__name__, u'Loading launcher')
            
            if DebugEnabled():
                for L in data:
                    print(u'  Launcher line: {}'.format(L))
            
            data_defs = {}
            data_defs_remove = []
            misc_defs = []
            
            for L in data:
                if u'=' in L:
                    if L[0] == u'[' and L[-1] == u']':
                        key = L[1:-1].split(u'=')
                        value = key[1]
                        key = key[0]
                        
                        misc_defs.append(u'{}={}'.format(key, value))
                    
                    else:
                        key = L.split(u'=')
                        value = key[1]
                        key = key[0]
                        
                        data_defs[key] = value
            
            # Fields using SetValue() function
            set_value_fields = (
                (u'Name', self.ti_name),
                (u'Exec', self.ti_exec),
                (u'Comment', self.ti_comm),
                (u'Icon', self.ti_icon),
                (u'Type', self.ti_type),
                (u'Encoding', self.ti_enc),
                )
            
            for label, control in set_value_fields:
                try:
                    control.SetValue(data_defs[label])
                    data_defs_remove.append(label)
                
                except KeyError:
                    pass
            
            # Fields using SetSelection() function
            set_selection_fields = (
                (u'Terminal', self.sel_term),
                (u'StartupNotify', self.sel_notify),
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
                    self.lst_categories.InsertStringItem(self.lst_categories.GetItemCount(), C)
                
                data_defs_remove.append(u'Categories')
            
            except KeyError:
                pass
            
            for K in data_defs_remove:
                if K in data_defs:
                    del data_defs[K]
            
            # Add any leftover keys to misc/other
            for K in data_defs:
                if K not in (u'Version',):
                    misc_defs.append(u'{}={}'.format(K, data_defs[K]))
            
            for index in reversed(range(len(misc_defs))):
                K = misc_defs[index]
                
                # Set custom filename
                if u'FILENAME=' in K:
                    filename = K.replace(u'FILENAME=', u'')
                    
                    # Remove so not added to misc. list
                    misc_defs.pop(index)
                    
                    continue
            
            if misc_defs:
                self.ti_other.SetValue(u'\n'.join(sorted(misc_defs)))
