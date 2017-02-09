# -*- coding: utf-8 -*-

## \package wizbin.launchers

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, wx

from dbr.language       import GT
from dbr.log            import DebugEnabled
from dbr.log            import Logger
from globals.fileio     import ReadFile
from globals.fileio     import WriteFile
from globals.ident      import btnid
from globals.ident      import chkid
from globals.ident      import inputid
from globals.ident      import listid
from globals.ident      import pgid
from globals.ident      import txtid
from globals.strings    import GS
from globals.strings    import TextIsEmpty
from globals.tooltips   import SetPageToolTips
from input.list         import ListCtrl
from input.select       import ComboBox
from input.select       import ComboBoxESS
from input.text         import TextArea
from input.text         import TextAreaESS
from input.text         import TextAreaPanel
from input.toggle       import CheckBox
from input.toggle       import CheckBoxESS
from ui.button          import CreateButton
from ui.dialog          import ConfirmationDialog
from ui.dialog          import ShowDialog
from ui.dialog          import ShowErrorDialog
from ui.layout          import BoxSizer
from ui.style           import layout as lyt
from ui.textpreview     import TextPreview
from wiz.helper         import GetAllTypeFields
from wiz.helper         import GetField
from wiz.helper         import GetMainWindow
from wiz.wizard         import WizardPage


## Page for creating a system menu launcher
class Page(WizardPage):
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.MENU) #, name=GT(u'Menu Launcher'))
        
        ## Override default label
        self.Label = GT(u'Menu Launcher')
        
        # --- Buttons to open/preview/save .desktop file
        btn_open = CreateButton(self, GT(u'Browse'), u'browse', btnid.BROWSE, name=u'btn browse')
        btn_save = CreateButton(self, GT(u'Save'), u'save', btnid.SAVE, name=u'btn save')
        btn_preview = CreateButton(self, GT(u'Preview'), u'preview', btnid.PREVIEW, name=u'btn preview')
        
        # --- CHECKBOX
        chk_enable = CheckBox(self, chkid.ENABLE, GT(u'Create system menu launcher'))
        
        # --- TYPE
        opts_type = (u'Application', u'Link', u'Directory',)
        
        txt_type = wx.StaticText(self, label=GT(u'Type'), name=u'type')
        ti_type = ComboBoxESS(self, inputid.TYPE, choices=opts_type,
                name=u'Type', defaultValue=opts_type[0])
        
        # --- ENCODING
        opts_enc = (
            u'UTF-1', u'UTF-7', u'UTF-8', u'CESU-8', u'UTF-EBCDIC',
            u'UTF-16', u'UTF-32', u'SCSU', u'BOCU-1', u'Punycode',
            u'GB 18030',
            )
        
        txt_enc = wx.StaticText(self, label=GT(u'Encoding'), name=u'encoding')
        ti_enc = ComboBoxESS(self, inputid.ENC, choices=opts_enc, name=u'Encoding',
                defaultValue=opts_enc[2])
        
        # --- TERMINAL
        chk_term = CheckBoxESS(self, chkid.TERM, GT(u'Terminal'), name=u'Terminal')
        
        # --- STARTUP NOTIFY
        chk_notify = CheckBoxESS(self, chkid.NOTIFY, GT(u'Startup Notify'), name=u'StartupNotify',
                defaultValue=True)
        
        # --- Custom output filename
        txt_filename = wx.StaticText(self, txtid.FNAME, GT(u'Filename'), name=u'filename')
        ti_filename = TextArea(self, inputid.FNAME, name=txt_filename.Name)
        
        chk_filename = CheckBox(self, chkid.FNAME, GT(u'Use "Name" as output filename (<Name>.desktop)'),
                name=u'filename chk', defaultValue=True)
        
        # --- NAME (menu)
        txt_name = wx.StaticText(self, label=GT(u'Name'), name=u'name*')
        ti_name = TextAreaESS(self, inputid.NAME, name=u'Name')
        ti_name.req = True
        
        # --- EXECUTABLE
        txt_exec = wx.StaticText(self, label=GT(u'Executable'), name=u'exec')
        ti_exec = TextAreaESS(self, inputid.EXEC, name=u'Exec')
        
        # --- COMMENT
        txt_comm = wx.StaticText(self, label=GT(u'Comment'), name=u'comment')
        ti_comm = TextAreaESS(self, inputid.DESCR, name=u'Comment')
        
        # --- ICON
        txt_icon = wx.StaticText(self, label=GT(u'Icon'), name=u'icon')
        ti_icon = TextAreaESS(self, inputid.ICON, name=u'Icon')
        
        txt_mime = wx.StaticText(self, label=GT(u'MIME Type'), name=u'mime')
        ti_mime = TextAreaESS(self, inputid.MIME, defaultValue=wx.EmptyString, name=u'MimeType')    
        
        # ----- OTHER/CUSTOM
        txt_other = wx.StaticText(self, label=GT(u'Custom Fields'), name=u'other')
        ti_other = TextAreaPanel(self, inputid.OTHER, name=txt_other.Name)
        ti_other.EnableDropTarget()
        
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
        
        txt_category = wx.StaticText(self, label=GT(u'Categories'), name=u'category')
        
        # This option does not get set by importing a new project
        ti_category = ComboBox(self, inputid.CAT, choices=opts_category, name=txt_category.Name,
                defaultValue=opts_category[0])
        
        btn_catadd = CreateButton(self, GT(u'Add'), u'add', btnid.ADD, name=u'add category')
        btn_catdel = CreateButton(self, GT(u'Remove'), u'remove', btnid.REMOVE, name=u'rm category')
        btn_catclr = CreateButton(self, GT(u'Clear'), u'clear', btnid.CLEAR, name=u'clear category')
        
        # FIXME: Allow using multi-select + remove
        lst_categories = ListCtrl(self, listid.CAT, name=u'Categories')
        # Can't set LC_SINGLE_SEL in constructor for wx 3.0 (ListCtrl bug???)
        lst_categories.SetSingleStyle(wx.LC_SINGLE_SEL)
        
        self.OnToggle()
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
        btn_save.Bind(wx.EVT_BUTTON, self.OnExportLauncher)
        btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewLauncher)
        
        chk_enable.Bind(wx.EVT_CHECKBOX, self.OnToggle)
        
        chk_filename.Bind(wx.EVT_CHECKBOX, self.OnSetCustomFilename)
        
        wx.EVT_KEY_DOWN(ti_category, self.SetCategory)
        wx.EVT_KEY_DOWN(lst_categories, self.SetCategory)
        btn_catadd.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catdel.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catclr.Bind(wx.EVT_BUTTON, self.OnClearCategories)
        
        # *** Layout *** #
        
        LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        LEFT_BOTTOM = lyt.ALGN_LB
        RIGHT_BOTTOM = wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM
        
        lyt_top = BoxSizer(wx.HORIZONTAL)
        lyt_top.Add(chk_enable, 0, LEFT_BOTTOM)
        lyt_top.AddStretchSpacer(1)
        lyt_top.Add(btn_open, 0, wx.ALIGN_TOP)
        lyt_top.Add(btn_save, 0, wx.ALIGN_TOP)
        lyt_top.Add(btn_preview, 0, wx.ALIGN_TOP)
        
        lyt_opts1 = wx.FlexGridSizer()
        lyt_opts1.SetCols(3)
        lyt_opts1.SetRows(2)
        
        lyt_opts1.Add(txt_type, 0, LEFT_CENTER)
        lyt_opts1.Add(ti_type, 0, wx.EXPAND|wx.LEFT, 5)
        lyt_opts1.Add(chk_term, 0, LEFT_CENTER|wx.LEFT, 5)
        lyt_opts1.Add(txt_enc, 0, LEFT_CENTER|wx.TOP, 5)
        lyt_opts1.Add(ti_enc, 0, lyt.PAD_LT, 5)
        lyt_opts1.Add(chk_notify, 0, LEFT_CENTER|lyt.PAD_LT, 5)
        
        lyt_mid = wx.GridBagSizer()
        lyt_mid.SetCols(4)
        lyt_mid.AddGrowableCol(1)
        lyt_mid.AddGrowableCol(3)
        
        # Row 1
        row = 0
        lyt_mid.Add(txt_filename, (row, 0), flag=LEFT_CENTER)
        lyt_mid.Add(ti_filename, (row, 1), flag=wx.EXPAND|wx.LEFT, border=5)
        lyt_mid.Add(chk_filename, (row, 2), span=(1, 2), flag=LEFT_CENTER|wx.LEFT, border=5)
        
        # Row 2
        row += 1
        lyt_mid.Add(txt_name, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
        lyt_mid.Add(ti_name, (row, 1), flag=wx.EXPAND|lyt.PAD_LT, border=5)
        lyt_mid.Add(txt_exec, (row, 2), flag=LEFT_CENTER|lyt.PAD_LT, border=5)
        lyt_mid.Add(ti_exec, (row, 3), flag=wx.EXPAND|lyt.PAD_LT, border=5)
        
        # Row 3
        row += 1
        lyt_mid.Add(txt_comm, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
        lyt_mid.Add(ti_comm, (row, 1), flag=wx.EXPAND|lyt.PAD_LT, border=5)
        lyt_mid.Add(txt_icon, (row, 2), flag=LEFT_CENTER|lyt.PAD_LT, border=5)
        lyt_mid.Add(ti_icon, (row, 3), flag=wx.EXPAND|lyt.PAD_LT, border=5)
        
        # Row 4
        row += 1
        lyt_mid.Add(txt_mime, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
        lyt_mid.Add(ti_mime, (row, 1), flag=wx.EXPAND|lyt.PAD_LT, border=5)
        
        lyt_bottom = wx.GridBagSizer()
        
        row = 0
        lyt_bottom.Add(txt_other, (row, 0), flag=LEFT_BOTTOM)
        lyt_bottom.Add(txt_category, (row, 2), flag=LEFT_BOTTOM|wx.LEFT, border=5)
        lyt_bottom.Add(ti_category, (row, 3), flag=LEFT_BOTTOM|wx.LEFT, border=5)
        lyt_bottom.Add(btn_catadd, (row, 4), flag=RIGHT_BOTTOM)
        lyt_bottom.Add(btn_catdel, (row, 5), flag=RIGHT_BOTTOM)
        lyt_bottom.Add(btn_catclr, (row, 6), flag=RIGHT_BOTTOM)
        
        row += 1
        lyt_bottom.Add(ti_other, (row, 0), (1, 2), wx.EXPAND)
        lyt_bottom.Add(lst_categories, (row, 2), (1, 5), wx.EXPAND|wx.LEFT, 5)
        
        lyt_bottom.AddGrowableRow(1)
        lyt_bottom.AddGrowableCol(1)
        lyt_bottom.AddGrowableCol(4)
        
        # --- Page 5 Sizer --- #
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_top, 0, wx.EXPAND|lyt.PAD_LR, 5)
        lyt_main.Add(lyt_opts1, 0, wx.EXPAND|lyt.PAD_LRT, 5)
        lyt_main.Add(lyt_mid, 0, wx.EXPAND|lyt.PAD_LRT, 5)
        lyt_main.Add(lyt_bottom, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Retrieves page data for export
    def Get(self):
        return self.GetLauncherInfo()
    
    
    ## Formats the launcher information for export
    def GetLauncherInfo(self):
        desktop_list = [u'[Desktop Entry]']
        
        name = GetField(self, inputid.NAME).GetValue()
        if not TextIsEmpty(name):
            desktop_list.append(u'Name={}'.format(name))
        
        desktop_list.append(u'Version=1.0')
        
        executable = GetField(self, inputid.EXEC).GetValue()
        if not TextIsEmpty(executable):
            desktop_list.append(u'Exec={}'.format(executable))
        
        comment = GetField(self, inputid.DESCR).GetValue()
        if not TextIsEmpty(comment):
            desktop_list.append(u'Comment={}'.format(comment))
        
        icon = GetField(self, inputid.ICON).GetValue()
        if not TextIsEmpty(icon):
            desktop_list.append(u'Icon={}'.format(icon))
        
        launcher_type = GetField(self, inputid.TYPE).GetValue()
        if not TextIsEmpty(launcher_type):
            desktop_list.append(u'Type={}'.format(launcher_type))
        
        desktop_list.append(u'Terminal={}'.format(GS(GetField(self, chkid.TERM).GetValue()).lower()))
        
        desktop_list.append(u'StartupNotify={}'.format(GS(GetField(self, chkid.NOTIFY).GetValue()).lower()))
        
        encoding = GetField(self, inputid.ENC).GetValue()
        if not TextIsEmpty(encoding):
            desktop_list.append(u'Encoding={}'.format(encoding))
        
        lst_categories = GetField(self, listid.CAT)
        categories = []
        cat_total = lst_categories.GetItemCount()
        count = 0
        while count < cat_total:
            C = lst_categories.GetItemText(count)
            if not TextIsEmpty(C):
                categories.append(lst_categories.GetItemText(count))
            
            count += 1
        
        # Add a final semi-colon if categories is not empty
        if categories:
            categories = u';'.join(categories)
            if categories[-1] != u';':
                categories = u'{};'.format(categories)
            
            desktop_list.append(u'Categories={}'.format(categories))
        
        other = GetField(self, inputid.OTHER).GetValue()
        if not TextIsEmpty(other):
            desktop_list.append(other)
        
        return u'\n'.join(desktop_list)
    
    
    ## Retrieves the filename to be used for the menu launcher
    def GetOutputFilename(self):
        if not GetField(self, chkid.FNAME).GetValue():
            filename = GetField(self, inputid.FNAME).GetValue().strip(u' ').replace(u' ', u'_')
            if not TextIsEmpty(filename):
                return filename
        
        return GetField(self, inputid.NAME).GetValue().strip(u' ').replace(u' ', u'_')
    
    
    ## TODO: Doxygen
    def GetSaveData(self):
        if GetField(self, chkid.ENABLE).GetValue():
            data = self.GetLauncherInfo()
            data = u'\n'.join(data.split(u'\n')[1:])
            
            if not GetField(self, chkid.FNAME).GetValue():
                data = u'[FILENAME={}]\n{}'.format(GetField(self, inputid.FNAME).GetValue(), data)
            
            return u'<<MENU>>\n1\n{}\n<</MENU>>'.format(data)
        
        else:
            return u'<<MENU>>\n0\n<</MENU>>'
    
    
    ## TODO: Doxygen
    def IsOkay(self):
        return GetField(self, chkid.ENABLE).GetValue()
    
    
    ## Handles button event from clear categories button
    def OnClearCategories(self, event=None):
        cats = GetField(self, listid.CAT)
        
        if cats.GetItemCount():
            clear = ConfirmationDialog(GetMainWindow(), GT(u'Confirm'), GT(u'Clear categories?'))
            
            if clear.Confirmed():
                cats.DeleteAllItems()
    
    
    ## Saves launcher information to file
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnLoadLauncher)
    #         'Others' field not being completely filled out.
    def OnExportLauncher(self, event=None):
        Logger.Debug(__name__, u'Export launcher ...')
        
        # Get data to write to control file
        menu_data = self.GetLauncherInfo().encode(u'utf-8')
        
        dia = wx.FileDialog(GetMainWindow(), GT(u'Save Launcher'), os.getcwd(),
            style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
        
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
    
    
    ## Loads a .desktop launcher's data
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnExportLauncher)
    #         'Others' field not being completely filled out.
    def OnLoadLauncher(self, event=None):
        dia = wx.FileDialog(GetMainWindow(), GT(u'Open Launcher'), os.getcwd(),
                style=wx.FD_CHANGE_DIR)
        
        if ShowDialog(dia):
            path = dia.GetPath()
            
            data = ReadFile(path, split=True)
            
            # Remove unneeded lines
            if data[0] == u'[Desktop Entry]':
                data = data[1:]
            
            self.Reset()
            self.SetLauncherData(u'\n'.join(data))
    
    
    ## TODO: Doxygen
    def OnPreviewLauncher(self, event=None):
        # Show a preview of the .desktop config file
        config = self.GetLauncherInfo()
        
        dia = TextPreview(title=GT(u'Menu Launcher Preview'),
                text=config, size=(500,400))
        
        dia.ShowModal()
        dia.Destroy()
    
    
    ## TODO: Doxygen
    def OnSetCustomFilename(self, event=None):
        chk_filename = GetField(self, chkid.FNAME)
        txt_filename = GetField(self, txtid.FNAME)
        ti_filename = GetField(self, inputid.FNAME)
        
        if not chk_filename.IsEnabled():
            txt_filename.Enable(False)
            ti_filename.Enable(False)
            return
        
        if chk_filename.GetValue():
            txt_filename.Enable(False)
            ti_filename.Enable(False)
            return
        
        txt_filename.Enable(True)
        ti_filename.Enable(True)
    
    
    ## Enables/Disables fields for creating a launcher
    def OnToggle(self, event=None):
        enabled = GetField(self, chkid.ENABLE).IsChecked()
        
        # Fields that should not be disabled
        skip_ids = (
            chkid.ENABLE,
            btnid.BROWSE,
            txtid.FNAME,
            )
        
        for LIST in inputid, chkid, listid, btnid:
            for ID in LIST.IdList:
                if ID not in skip_ids:
                    field = GetField(self, ID)
                    
                    if isinstance(field, wx.Window):
                        field.Enable(enabled)
        
        # Disable/Enable static text labels
        st_labels = GetAllTypeFields(self, wx.StaticText)
        for ST in st_labels:
            if ST.Id not in skip_ids:
                ST.Enable(enabled)
        
        self.OnSetCustomFilename()
    
    
    ## Resets all fields to default values
    def Reset(self):
        chk_filename = GetField(self, chkid.FNAME)
        
        chk_filename.SetValue(chk_filename.Default)
        GetField(self, inputid.FNAME).Clear()
        
        for IDS in inputid, chkid, listid:
            idlist = IDS.IdList
            
            for ID in idlist:
                field = GetField(self, ID)
                
                if isinstance(field, wx.Window):
                    field.Reset()
        
        self.OnToggle()
    
    
    ## TODO: Doxygen
    def SetCategory(self, event=None):
        try:
            ID = event.GetKeyCode()
        
        except AttributeError:
            ID = event.GetEventObject().GetId()
        
        cat = GetField(self, inputid.CAT).GetValue()
        cat = cat.split()
        cat = u''.join(cat)
        
        lst_categories = GetField(self, listid.CAT)
        
        if ID in (wx.ID_ADD, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            lst_categories.InsertStringItem(lst_categories.GetItemCount(), cat)
        
        elif ID in (wx.ID_REMOVE, wx.WXK_DELETE):
            if lst_categories.GetItemCount() and lst_categories.GetSelectedItemCount():
                cur_cat = lst_categories.GetFirstSelected()
                lst_categories.DeleteItem(cur_cat)
        
        elif ID == wx.ID_CLEAR:
            if lst_categories.GetItemCount():
                if ConfirmationDialog(GetMainWindow(), GT(u'Confirm'),
                        GT(u'Clear categories?')).ShowModal() in (wx.ID_OK, wx.OK):
                    lst_categories.DeleteAllItems()
        
        if event:
            event.Skip()
    
    
    ## Fills out launcher information from loaded file
    #  
    #  \param data
    #    Information to fill out menu launcher fields
    #  \param enabled
    #    \b \e bool : Launcher will be flagged for export if True
    def SetLauncherData(self, data, enabled=True):
        # Make sure we are dealing with a list
        if isinstance(data, (unicode, str)):
            data = data.split(u'\n')
        
        # Data list is not empty
        if data:
            Logger.Debug(__name__, u'Loading launcher')
            
            if data[0].isnumeric():
                enabled = int(data.pop(0)) > 0
            
            if DebugEnabled():
                for L in data:
                    print(u'  Launcher line: {}'.format(L))
            
            Logger.Debug(__name__, u'Enabling launcher: {}'.format(enabled))
            
            if enabled:
                GetField(self, chkid.ENABLE).SetValue(True)
                
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
                    (u'Name', GetField(self, inputid.NAME)),
                    (u'Exec', GetField(self, inputid.EXEC)),
                    (u'Comment', GetField(self, inputid.DESCR)),
                    (u'Icon', GetField(self, inputid.ICON)),
                    (u'Type', GetField(self, inputid.TYPE)),
                    (u'Encoding', GetField(self, inputid.ENC)),
                    )
                
                for label, control in set_value_fields:
                    try:
                        control.SetValue(data_defs[label])
                        data_defs_remove.append(label)
                    
                    except KeyError:
                        pass
                
                check_box_fields = (
                    (u'Terminal', GetField(self, chkid.TERM)),
                    (u'StartupNotify', GetField(self, chkid.NOTIFY)),
                    )
                
                for label, control in check_box_fields:
                    try:
                        if data_defs[label].lower() == u'true':
                            control.SetValue(True)
                        
                        else:
                            control.SetValue(False)
                        
                        data_defs_remove.append(label)
                    
                    except KeyError:
                        pass
                
                try:
                    lst_categories = GetField(self, listid.CAT)
                    categories = tuple(data_defs[u'Categories'].split(u';'))
                    for C in categories:
                        lst_categories.InsertStringItem(lst_categories.GetItemCount(), C)
                    
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
                        
                        if not TextIsEmpty(filename):
                            Logger.Debug(__name__, u'Setting custom filename: {}'.format(filename))
                            
                            GetField(self, inputid.FNAME).SetValue(filename)
                            GetField(self, chkid.FNAME).SetValue(False)
                        
                        # Remove so not added to misc. list
                        misc_defs.pop(index)
                        
                        continue
                
                if misc_defs:
                    GetField(self, inputid.OTHER).SetValue(u'\n'.join(sorted(misc_defs)))
                
                self.OnToggle()
