# -*- coding: utf-8 -*-

# Menu Page

import os, shutil, wx

import db
from dbr.buttons import ButtonAdd
from dbr.buttons import ButtonBrowse64
from dbr.buttons import ButtonClear
from dbr.buttons import ButtonDel
from dbr.buttons import ButtonPreview64
from dbr.buttons import ButtonSave64


ID = wx.NewId()

class Panel(wx.Panel):
    def __init__(self, parent, id=ID, name=_('Menu Launcher')):
        wx.Panel.__init__(self, parent, id, name=_('Menu Launcher'))
        
        # Allows executing parent methods
        self.parent = parent
        
        # --- Tool Tips --- #
        DF_tip = wx.ToolTip(_('Open launcher file'))
        icon_tip = wx.ToolTip(_('Icon to be displayed for the launcher'))
        m_name_tip = wx.ToolTip(_('Text for the launcher'))
        #m_ver_tip = wx.ToolTip("The version of your application")
        m_com_tip = wx.ToolTip(_('Text displayed when mouse hovers over launcher'))
        m_exec_tip = wx.ToolTip(_('Executable to be launched'))
        m_mime_tip = wx.ToolTip(_('Specifies the MIME types that the application can handle'))
        #m_enc_tip = wx.ToolTip("Specifies the encoding of the desktop entry file")
        #m_type_tip = wx.ToolTip(_('The type of launcher'))
        m_cat_tip = wx.ToolTip("Choose which categories in which you would like your application to be displayed")
        m_term_tip = wx.ToolTip(_('Specifies whether application should be run from a terminal'))
        m_notify_tip = wx.ToolTip(_('Displays a notification in the system panel when launched'))
        m_nodisp_tip = wx.ToolTip("This options means \"This application exists, but don't display it in the menus\"")
        m_showin_tip = wx.ToolTip("Only Show In Tip")
        
        # --- Main Menu Entry --- #
        
        # --- Buttons to open/preview/save .desktop file
        self.open = ButtonBrowse64(self)
        self.open.SetToolTip(DF_tip)
        self.button_save = ButtonSave64(self)
        self.button_preview = ButtonPreview64(self)
        
        self.open.Bind(wx.EVT_BUTTON, self.OpenFile)
        wx.EVT_BUTTON(self.button_save, wx.ID_ANY, self.OnSave)
        wx.EVT_BUTTON(self.button_preview, wx.ID_ANY, self.OnPreview)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.open, 0)
        button_sizer.Add(self.button_save, 0)
        button_sizer.Add(self.button_preview, 0)
        
        # --- CHECKBOX
        self.activate = wx.CheckBox(self, -1, _('Create system menu launcher'))
        
        self.activate.Bind(wx.EVT_CHECKBOX, self.OnToggle)
        
        self.txt_filename = wx.StaticText(self, label=_('Filename'))
        self.input_filename = wx.TextCtrl(self)
        self.chk_filename = wx.CheckBox(self, label=_('Use "Name" as output filename (<name>.desktop)'))
        self.chk_filename.SetValue(True)
        
        self.chk_filename.Bind(wx.EVT_CHECKBOX, self.OnSetCustomFilename)
        
        for I in self.txt_filename, self.input_filename:
            I.SetToolTip(wx.ToolTip(_('Custom filename to use for launcher')))
        
        self.chk_filename.SetToolTip(
                wx.ToolTip(_('If checked, the lowercase value of the "Name" field will be used for the filename'))
            )
        
        # --- NAME (menu)
        self.name_text = wx.StaticText(self, -1, _('Name'))
        self.name_text.SetToolTip(m_name_tip)
        self.name_input = wx.TextCtrl(self, -1)
        
        # --- EXECUTABLE
        self.exe_text = wx.StaticText(self, -1, _('Executable'))
        self.exe_text.SetToolTip(m_exec_tip)
        self.exe_input = wx.TextCtrl(self, -1)
        
        # --- COMMENT
        self.comm_text = wx.StaticText(self, -1, _('Comment'))
        self.comm_text.SetToolTip(m_com_tip)
        self.comm_input = wx.TextCtrl(self, -1)
        
        # --- ICON
        self.icon_text = wx.StaticText(self, -1, _('Icon'))
        self.icon_text.SetToolTip(icon_tip)
        self.icon_input = wx.TextCtrl(self)
        
        # --- TYPE
        self.type_opt = ('Application', 'Link', 'FSDevice', 'Directory')
        self.type_text = wx.StaticText(self, -1, _('Type'))
        #self.type_text.SetToolTip(m_type_tip)
        self.type_choice = wx.ComboBox(self, -1, choices=self.type_opt)
        self.type_choice.SetSelection(0)
        #self.type_choice = wx.Choice(self, -1, choices=self.type_opt)
        
        # --- TERMINAL
        self.term_opt = ('true', 'false')
        self.term_text = wx.StaticText(self, -1, _('Terminal'))
        self.term_text.SetToolTip(m_term_tip)
        self.term_choice = wx.Choice(self, -1, choices=self.term_opt)
        self.term_choice.SetSelection(1)
        
        # --- STARTUP NOTIFY
        self.notify_opt = ('true', 'false')
        self.notify_text = wx.StaticText(self, -1, _('Startup Notify'))
        self.notify_text.SetToolTip(m_notify_tip)
        self.notify_choice = wx.Choice(self, -1, choices=self.notify_opt)
        self.notify_choice.SetSelection(0)
        
        # --- ENCODING
        self.enc_opt = ('UTF-1','UTF-7','UTF-8','CESU-8','UTF-EBCDIC','UTF-16','UTF-32','SCSU','BOCU-1','Punycode',
                    'GB 18030')
        self.enc_text = wx.StaticText(self, -1, _('Encoding'))
        #self.enc_text.SetToolTip(m_enc_tip)
        self.enc_input = wx.ComboBox(self, -1, choices=self.enc_opt)
        self.enc_input.SetSelection(2)
        
        # --- CATEGORIES
        self.cat_opt = ('2DGraphics','Accessibility','Application','ArcadeGame','Archiving','Audio','AudioVideo',
                        'BlocksGame','BoardGame','Calculator','Calendar','CardGame','Compression',
                        'ContactManagement','Core','DesktopSettings','Development','Dictionary','DiscBurning',
                        'Documentation','Email','FileManager','FileTransfer','Game','GNOME','Graphics','GTK',
                        'HardwareSettings','InstantMessaging','KDE','LogicGame','Math','Monitor','Network','OCR',
                        'Office','P2P','PackageManager','Photography','Player','Presentation','Printing','Qt',
                        'RasterGraphics','Recorder','RemoteAccess','Scanning','Screensaver','Security','Settings',
                        'Spreadsheet','System','Telephony','TerminalEmulator','TextEditor','Utility',
                        'VectorGraphics','Video','Viewer','WordProcessor','Wine','Wine-Programs-Accessories',
                        'X-GNOME-NetworkSettings','X-GNOME-PersonalSettings','X-GNOME-SystemSettings','X-KDE-More',
                        'X-Red-Hat-Base','X-SuSE-ControlCenter-System')
        self.cat_text = wx.StaticText(self, -1, _('Category'))
        self.cat_choice = wx.ComboBox(self, -1, value=self.cat_opt[0], choices=self.cat_opt)
        self.cat_add = ButtonAdd(self)
        self.cat_del = ButtonDel(self)
        self.cat_clr = ButtonClear(self)
        
        if wx.MAJOR_VERSION > 2:
            self.categories = wx.ListCtrl(self, -1)
            self.categories.SetSingleStyle(wx.LC_SINGLE_SEL|wx.LC_REPORT)
        else:
            self.categories = wx.ListCtrl(self, -1, style=wx.LC_SINGLE_SEL|wx.BORDER_SIMPLE)
        
        self.categories.InsertColumn(0, "")
        
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
        self.misc_text = wx.StaticText(self, -1, _('Other'))
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
            self.open, self.button_save, self.button_preview, self.chk_filename, self.icon_input,
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
        self.standards = {    "name": self.name_input, "type": self.type_choice, "exec": self.exe_input,
                            "comment": self.comm_input, "terminal": self.term_choice,
                            "startupnotify": self.notify_choice, "encoding": self.enc_input,
                            "categories": self.categories
                            }
        
        # Lists of widgets that change language
        self.setlabels = {    self.activate: "Menu", self.open: "Open", self.border: "Border",
                            self.icon_text: "Icon",
                            self.name_text: "Name", self.comm_text: "Comm", self.exe_text: "Exec",
                            self.enc_text: "Enc", self.type_text: "Type", self.cat_text: "Cat",
                            self.term_text: "Term", self.notify_text: "Notify"}
    
    
    def OnToggle(self, event):
        if self.activate.IsChecked():
            for item in self.menu_list:
                item.Enable()
        
        else:
            for item in self.menu_list:
                item.Disable()
        
        self.OnSetCustomFilename(None)
    
    
    def GetMenuInfo(self):
        # Create list to store info
        desktop_list = ["[Desktop Entry]"]
        
        # Add Name
        name = self.name_input.GetValue()
        desktop_list.append("Name=%s" % name)
        
        # Add Version
        desktop_list.append("Version=1.0")
        
        # Add Executable
        exe = self.exe_input.GetValue()
        desktop_list.append("Exec=%s" % exe)
        
        # Add Comment
        comm = self.comm_input.GetValue()
        desktop_list.append("Comment=%s" % comm)
        
        # Add Icon
        icon = self.icon_input.GetValue()
        desktop_list.append("Icon=%s" % icon)
        
        # Add Type
        #type = self.type_opt[self.type_choice.GetSelection()]
        _type = self.type_choice.GetValue()
        desktop_list.append("Type=%s" % _type)
        
        # Add Terminal
        if self.term_choice.GetSelection() == 0:
            desktop_list.append("Terminal=true")
        else:
            desktop_list.append("Terminal=false")
        
        # Add Startup Notify
        if self.notify_choice.GetSelection() == 0:
            desktop_list.append("StartupNotify=true")
        else:
            desktop_list.append("StartupNotify=false")
        
        # Add Encoding
        enc = self.enc_input.GetValue()
        desktop_list.append("Encoding=%s" % enc)
        
        # Add Categories
        cat_list = []
        cat_total = self.categories.GetItemCount()
        count = 0
        while count < cat_total:
            cat_list.append(self.categories.GetItemText(count))
            count += 1
        # Add a final semi-colon if categories is not empty
        if cat_list != []:
            cat_list[-1] = "%s;" % cat_list[-1]
        desktop_list.append("Categories=%s" % ";".join(cat_list))
        
        # Add Misc
        if self.misc.GetValue() != wx.EmptyString:
            desktop_list.append(self.misc.GetValue())
        
        return "\n".join(desktop_list)
    
    
    def SetCategory(self, event):
        try:
            id = event.GetKeyCode()
        except AttributeError:
            id = event.GetEventObject().GetId()
        
        cat = self.cat_choice.GetValue()
        cat = cat.split()
        cat = "".join(cat)
        
        if id == wx.WXK_RETURN or id == wx.WXK_NUMPAD_ENTER:
            self.categories.InsertStringItem(0, cat)
        
        elif id == wx.WXK_DELETE:
            cur_cat = self.categories.GetFirstSelected()
            self.categories.DeleteItem(cur_cat)
        
        elif id == wx.WXK_ESCAPE:
            confirm = wx.MessageDialog(self, _('Delete all categories?'), _('Confirm'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if confirm.ShowModal() == wx.ID_YES:
                self.categories.DeleteAllItems()
        event.Skip()
    
    
    # *** OPEN/SAVE *** #
    def OnSave(self, event):
        # Get data to write to control file
        menu_data = self.GetMenuInfo().encode('utf-8')
        
        # Saving?
        cont = False
        
        # Open a "Save Dialog"
        if self.parent.parent.cust_dias.IsChecked():
            dia = db.SaveFile(self, _('Save Launcher'))
#            dia.SetFilename("control")
            if dia.DisplayModal():
                cont = True
                path = "%s/%s" % (dia.GetPath(), dia.GetFilename())
        else:
            dia = wx.FileDialog(self, _('Save Launcher'), os.getcwd(),
                style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
#            dia.SetFilename("control")
            if dia.ShowModal() == wx.ID_OK:
                cont = True
                path = dia.GetPath()
        
        if cont:
            filename = dia.GetFilename()
            
            # Create a backup file
            overwrite = False
            if os.path.isfile(path):
                backup = '%s.backup' % path
                shutil.copy(path, backup)
                overwrite = True
            
            file = open(path, "w")
            try:
                file.write(menu_data)
                file.close()
                if overwrite:
                    os.remove(backup)
            except UnicodeEncodeError:
                serr = _('Save failed')
                uni = _('Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                UniErr = wx.MessageDialog(self, '%s\n\n%s' % (serr, uni), _('Unicode Error'), style=wx.OK|wx.ICON_EXCLAMATION)
                UniErr.ShowModal()
                file.close()
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
    
    
    def OpenFile(self, event):
        cont = False
        if self.parent.parent.cust_dias.IsChecked():
            dia = db.OpenFile(self, _('Open Launcher'))
            if dia.DisplayModal():
                cont = True
        else:
            dia = wx.FileDialog(self, _('Open Launcher'), os.getcwd(),
                style=wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
        
        if cont == True:
            path = dia.GetPath()
            file = open(path, "r")
            text = file.read()
            file.close()
            data = text.split("\n")
            if data[0] == "[Desktop Entry]":
                data = data[1:]
                # First line needs to be changed to "1"
            data.insert(0, '1')
            self.SetFieldData("\n".join(data))
        
    def OnPreview(self, event):
        # Show a preview of the .desktop config file
        config = self.GetMenuInfo()
        
        dia = wx.Dialog(self, -1, _('Preview'), size=(500,400))
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
                ("Name", self.name_input), ("Exec", self.exe_input), ("Comment", self.comm_input),
                ("Icon", self.icon_input)
                )
            
            # Fields using SetSelection() function
            set_selection_fields = (
                ("Terminal", self.term_choice, self.term_opt),
                ("StartupNotify", self.notify_choice, self.notify_opt)
                )
            
            # Fields using either SetSelection() or SetValue()
            set_either_fields = (
                ("Type", self.type_choice, self.type_opt),
                ("Encoding", self.enc_input, self.enc_opt)
                )
            
            lines = data.split("\n")
            
            # Leave leftover text in this list to dump into misc field
            leftovers = lines[:]
            
            # Remove 1st line (1) from leftovers
            leftovers = leftovers[1:]
            
            # Remove Version field since is not done below
            try:
                leftovers.remove("Version=1.0")
            except ValueError:
                pass
            
            for line in lines:
                f1 = line.split("=")[0]
                f2 = "=".join(line.split("=")[1:])
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
                if f1 == "Categories":
                    leftovers.remove(line)
                    categories = f2.split(";")
                    cat_count = len(categories)-1
                    while cat_count > 0:
                        cat_count -= 1
                        self.categories.InsertStringItem(0, categories[cat_count])
            if len(leftovers) > 0:
                self.misc.SetValue("\n".join(leftovers))
        self.OnToggle(None)
    
    def GatherData(self):
        if self.activate.GetValue():
            data = self.GetMenuInfo()
            data = "\n".join(data.split("\n")[1:])
            
            if not self.chk_filename.GetValue():
                data = "[Filename={}]\n{}".format(self.input_filename.GetValue(), data)
            
            return "<<MENU>>\n1\n%s\n<</MENU>>" % data
        
        else:
            return "<<MENU>>\n0\n<</MENU>>"
