# -*- coding: utf-8 -*-

## \package wiz_bin.menu


# System imports
import wx, os, shutil

# Local imports
import dbr
from dbr.constants import ID_MENU
from dbr.wizard import WizardPage


class Panel(wx.Panel, WizardPage):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, ID_MENU, name=_(u'Menu Launcher'))
        WizardPage.__init__(self)
        
        # Allows executing parent methods
        self.parent = parent
        
        # --- Tool Tips --- #
        DF_tip = wx.ToolTip(_(u'Open launcher file'))
        icon_tip = wx.ToolTip(_(u'Icon to be displayed for the launcher'))
        m_name_tip = wx.ToolTip(_(u'Text for the launcher'))
        #m_ver_tip = wx.ToolTip(u'The version of your application')
        m_com_tip = wx.ToolTip(_(u'Text displayed when mouse hovers over launcher'))
        m_exec_tip = wx.ToolTip(_(u'Executable to be launched'))
        m_mime_tip = wx.ToolTip(_(u'Specifies the MIME types that the application can handle'))
        #m_enc_tip = wx.ToolTip(u'Specifies the encoding of the desktop entry file')
        #m_type_tip = wx.ToolTip(_(u'The type of launcher'))
        m_cat_tip = wx.ToolTip(u'Choose which categories in which you would like your application to be displayed')
        m_term_tip = wx.ToolTip(_(u'Specifies whether application should be run from a terminal'))
        m_notify_tip = wx.ToolTip(_(u'Displays a notification in the system panel when launched'))
        m_nodisp_tip = wx.ToolTip(u'This options means "This application exists, but don\'t display it in the menus"')
        m_showin_tip = wx.ToolTip(u'Only Show In Tip')
        
        # --- Main Menu Entry --- #
        
        # --- Buttons to open/preview/save .desktop file
        self.open = dbr.ButtonBrowse64(self)
        self.open.SetToolTip(DF_tip)
        self.button_save = dbr.ButtonSave64(self)
        self.button_preview = dbr.ButtonPreview64(self)
        
        self.open.Bind(wx.EVT_BUTTON, self.OpenFile)
        wx.EVT_BUTTON(self.button_save, wx.ID_ANY, self.OnSave)
        wx.EVT_BUTTON(self.button_preview, wx.ID_ANY, self.OnPreview)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.open, 0)
        button_sizer.Add(self.button_save, 0)
        button_sizer.Add(self.button_preview, 0)
        
        # --- CHECKBOX
        self.activate = wx.CheckBox(self, -1, _(u'Create system menu launcher'))
        
        self.activate.Bind(wx.EVT_CHECKBOX, self.OnToggle)
        
        # --- NAME (menu)
        self.name_text = wx.StaticText(self, -1, _(u'Name'))
        self.name_text.SetToolTip(m_name_tip)
        self.name_input = wx.TextCtrl(self, -1)
        #self.name_input.SetBackgroundColour(dbr.Mandatory)
        
        # --- EXECUTABLE
        self.exe_text = wx.StaticText(self, -1, _(u'Executable'))
        self.exe_text.SetToolTip(m_exec_tip)
        self.exe_input = wx.TextCtrl(self, -1)
        
        # --- COMMENT
        self.comm_text = wx.StaticText(self, -1, _(u'Comment'))
        self.comm_text.SetToolTip(m_com_tip)
        self.comm_input = wx.TextCtrl(self, -1)
        
        # --- ICON
        self.icon_text = wx.StaticText(self, -1, _(u'Icon'))
        self.icon_text.SetToolTip(icon_tip)
        self.icon_input = wx.TextCtrl(self)
        
        # --- TYPE
        self.type_opt = (u'Application', u'Link', u'FSDevice', u'Directory')
        self.type_text = wx.StaticText(self, -1, _(u'Type'))
        #self.type_text.SetToolTip(m_type_tip)
        self.type_choice = wx.ComboBox(self, -1, choices=self.type_opt)
        self.type_choice.SetSelection(0)
        
        # --- TERMINAL
        self.term_opt = (u'true', u'false')
        self.term_text = wx.StaticText(self, -1, _(u'Terminal'))
        self.term_text.SetToolTip(m_term_tip)
        self.term_choice = wx.Choice(self, -1, choices=self.term_opt)
        self.term_choice.SetSelection(1)
        
        # --- STARTUP NOTIFY
        self.notify_opt = (u'true', u'false')
        self.notify_text = wx.StaticText(self, -1, _(u'Startup Notify'))
        self.notify_text.SetToolTip(m_notify_tip)
        self.notify_choice = wx.Choice(self, -1, choices=self.notify_opt)
        
        # --- ENCODING
        self.enc_opt = (u'UTF-1',u'UTF-7',u'UTF-8',u'CESU-8',u'UTF-EBCDIC',
                u'UTF-16',u'UTF-32',u'SCSU',u'BOCU-1',u'Punycode', u'GB 18030')
        self.enc_text = wx.StaticText(self, -1, _(u'Encoding'))
        #self.enc_text.SetToolTip(m_enc_tip)
        self.enc_input = wx.ComboBox(self, -1, choices=self.enc_opt)
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
        self.cat_text = wx.StaticText(self, -1, _(u'Category'))
        self.cat_choice = wx.ComboBox(self, -1, value=self.cat_opt[0], choices=self.cat_opt)
        self.cat_add = dbr.ButtonAdd(self)
        self.cat_del = dbr.ButtonDel(self)
        self.cat_clr = dbr.ButtonClear(self)
        
        # FIXME: wx. 3.0 compat
        if wx.MAJOR_VERSION > 3:
            self.categories = wx.ListCtrl(self, -1, style=wx.LC_SINGLE_SEL|wx.BORDER_SIMPLE)
            self.categories.InsertColumn(0, u'')
        
        else:
            self.categories = wx.ListCtrl(self, -1)
            self.categories.SetSingleStyle(wx.LC_SINGLE_SEL)
        
        
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
        self.misc_text = wx.StaticText(self, -1, _(u'Other'))
        self.misc = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.BORDER_SIMPLE)
        
        misc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        misc_sizer.Add(self.misc, 1, wx.EXPAND)
        
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
        border_box.Add(self.misc_text, 0, wx.LEFT, 6)
        border_box.Add(self.misc, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        
        # --- List of main menu items affected by checkbox -- used for toggling each widget
        self.menu_list = (self.open, self.button_save, self.button_preview, self.icon_input, self.name_input,
                        self.comm_input, self.exe_input, self.enc_input, self.type_choice, self.cat_choice,
                        self.categories, self.cat_add, self.cat_del, self.cat_clr, self.term_choice,
                        self.notify_choice, self.misc)
                        #, self.m_nodisp_widg, self.m_showin_widg)
        
        self.OnToggle(None) #Disable widgets
        
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
                    
        else:
            for item in self.menu_list:
                item.Disable()
    
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
        if self.misc.GetValue() != wx.EmptyString:
            desktop_list.append(self.misc.GetValue())
        
        return u'\n'.join(desktop_list)
    
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
            confirm = wx.MessageDialog(self, _(u'Delete all categories?'), _(u'Confirm'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if confirm.ShowModal() == wx.ID_YES:
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
            dia = wx.FileDialog(self, _(u'Save Launcher'), os.getcwd(),
                style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
#            dia.SetFilename(u'control')
            if dia.ShowModal() == wx.ID_OK:
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
                serr = _(u'Save failed')
                uni = _(u'Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                UniErr = wx.MessageDialog(self, u'%s\n\n%s' % (serr, uni), _(u'Unicode Error'), style=wx.OK|wx.ICON_EXCLAMATION)
                UniErr.ShowModal()
                f_opened.close()
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
            dia = wx.FileDialog(self, _(u'Open Launcher'), os.getcwd(),
                style=wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
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
            self.SetFieldData(u'\n'.join(data))
        
    def OnPreview(self, event):
        # Show a preview of the .desktop config file
        config = self.GetMenuInfo()
        
        dia = wx.Dialog(self, -1, _(u'Preview'), size=(500,400))
        preview = wx.TextCtrl(dia, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        preview.SetValue(config)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
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
            # Remove line with '[Desktop Entry]'
            data = u'\n'.join(data.split(u'\n')[1:])
            return u'<<MENU>>\n1\n%s\n<</MENU>>' % data
        else:
            return u'<<MENU>>\n0\n<</MENU>>'
    
    
    ## Retrieves Desktop Entry file information
    #  
    #  \return
    #        \b \e tuple(str, str, str) : File/Page name,
    #          string formatted menu information, & filename to output
    def GetPageInfo(self):
        if not self.activate.GetValue():
            return None
        
        return(__name__, self.GetMenuInfo(), u'MENU')
    
    ## Override parent method
    #  
    #  Changes output name 'MENU'.
    def Export(self, out_dir, out_name=wx.EmptyString):
        out_name = u'MENU'
        
        return WizardPage.Export(self, out_dir, out_name)
