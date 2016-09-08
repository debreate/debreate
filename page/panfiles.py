# -*- coding: utf-8 -*-

import os, wx.lib.mixins.listctrl as LC, db
from os.path import exists, isfile, isdir
#from common import *

from wximports import \
	wxNewId, wxListCtrl, wxPanel, wxBORDER_SIMPLE, wxLC_REPORT, wxMenu, wxMenuItem, \
	wxEVT_MENU, wxGenericDirCtrl, wxEVT_CONTEXT_MENU, wxEVT_BUTTON, wxRadioButton, \
	wxRB_GROUP, wxEVT_RADIOBUTTON, wxGridSizer, wxStaticBox, wxStaticBoxSizer, \
	wxHORIZONTAL, wxTextCtrl, wxEVT_KEY_DOWN, wxEVT_KEY_UP, wxBoxSizer, wxVERTICAL, \
	wxEXPAND, wxALIGN_CENTER_VERTICAL, wxLEFT, wxRIGHT, wxALL, wxBOTTOM, wxFlexGridSizer, \
	wxTOP

ID = wxNewId()

ID_pin = 100
ID_fin = 101
ID_pout = 102

ID_AddDir = 140
ID_AddFile = 141
ID_Refresh = 142

home = os.getenv("HOME")

class DList(wxListCtrl, LC.ListCtrlAutoWidthMixin):#LC.TextEditMixin):
    """Creates a ListCtrl class in which every column's text can be edited"""
    def __init__(self, parent, id):
        wxListCtrl.__init__(self, parent, id, style=wxBORDER_SIMPLE|wxLC_REPORT)
        #LC.TextEditMixin.__init__(self)
        LC.ListCtrlAutoWidthMixin.__init__(self)

class Panel(wxPanel):
    """Class defining controls for the "Paths" page"""
    def __init__(self, parent, id=ID, name=_('Files')):
        wxPanel.__init__(self, parent, id, name=_('Files'))
        
        # For identifying page to parent
        #self.ID = "FILES"
        
        # Allows calling parent methods
        self.parent = parent
        
        # Create a Context Menu
        self.menu = wxMenu()
        
        self.add_dir = wxMenuItem(self.menu, ID_AddDir, _('Add Folder'))
        self.add_file = wxMenuItem(self.menu, ID_AddFile, _('Add File'))
        self.refresh = wxMenuItem(self.menu, ID_Refresh, _('Refresh'))
        
        wxEVT_MENU(self, ID_AddDir, self.AddPath)
        wxEVT_MENU(self, ID_AddFile, self.AddPath)
        wxEVT_MENU(self, ID_Refresh, self.OnRefresh)
        
        self.menu.AppendItem(self.add_dir)
        self.menu.AppendItem(self.add_file)
        self.menu.AppendSeparator()
        self.menu.AppendItem(self.refresh)
        
        # Directory listing for importing files and folders
        self.dir_tree = wxGenericDirCtrl(self, -1, home, size=(300,20))
        
        wxEVT_CONTEXT_MENU(self.dir_tree, self.OnRightClick)
        
        # ----- Add/Remove/Clear buttons
        path_add = db.ButtonAdd(self)
        path_remove = db.ButtonDel(self)
        button_clear = db.ButtonClear(self)
        
        wxEVT_BUTTON(path_add, -1, self.AddPath)
        wxEVT_BUTTON(path_remove, -1, self.DelPath)
        wxEVT_BUTTON(button_clear, -1, self.ClearAll)
        
        # ----- Destination path
        # choices of destination
        self.radio_bin = wxRadioButton(self, -1, "/bin", style=wxRB_GROUP)
        self.radio_usrbin = wxRadioButton(self, -1, "/usr/bin")
        self.radio_usrlib = wxRadioButton(self, -1, "/usr/lib")
        self.radio_locbin = wxRadioButton(self, -1, "/usr/local/bin")
        self.radio_loclib = wxRadioButton(self, -1, "/usr/local/lib")
        self.radio_cst = wxRadioButton(self, -1, _('Custom'))
        self.radio_cst.SetValue(True)
        
        # group buttons together
        self.radio_group = (self.radio_bin, self.radio_usrbin, self.radio_usrlib, self.radio_locbin, self.radio_loclib, self.radio_cst)
        
        # create an event to enable/disable custom widget
        for item in self.radio_group:
            wxEVT_RADIOBUTTON(item, -1, self.SetDestination)
        
        # make them look pretty
        radio_sizer = wxGridSizer(3, 2, 5, 5)
        for item in self.radio_group:
            radio_sizer.Add(item, 0)
        self.radio_border = wxStaticBox(self, -1, _('Target'), size=(20,20))
        radio_box = wxStaticBoxSizer(self.radio_border, wxHORIZONTAL)
        radio_box.Add(radio_sizer, 0)
        
        self.prev_dest_value = "/usr/bin"
        self.dest_cust = wxTextCtrl(self, -1, self.prev_dest_value)
        wxEVT_KEY_DOWN(self.dest_cust, self.GetDestValue)
        wxEVT_KEY_UP(self.dest_cust, self.CheckDest)
        cust_sizer = wxBoxSizer(wxVERTICAL)  # put the textctrl in own sizer so expands horizontally
        cust_sizer.Add(self.dest_cust, 1, wxEXPAND)
        
        self.dest_browse = db.ButtonBrowse(self, ID_pout)
        
        wxEVT_BUTTON(self.dest_browse, -1, self.OnBrowse)
        
        self.path_dict = {ID_pout: self.dest_cust}
        
        path_add_sizer = wxBoxSizer(wxHORIZONTAL)
        path_add_sizer.Add(path_add, 0)
        path_add_sizer.Add(path_remove, 0)
        path_add_sizer.Add(button_clear, 0, wxALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(cust_sizer, 1, wxALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(self.dest_browse, 0, wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT, 5)
        
        
        # Display area for files added to list
        self.dest_area = DList(self, -1)
        
        # List that stores the actual paths to the files
        self.list_data = []
        
        # Set the width of first column on creation
        parent_size = self.GetGrandParent().GetSize()
        parent_width = parent_size[1]
        self.dest_area.InsertColumn(0, _('File'), width=parent_width/3-10)
        self.dest_area.InsertColumn(1, _('Target'))
        
        wxEVT_KEY_DOWN(self.dest_area, self.DelPath)
        
        LMR_sizer = wxBoxSizer(wxHORIZONTAL)
        LMR_sizer.Add(self.dest_area, 1, wxEXPAND)
        
        page_sizer = wxBoxSizer(wxVERTICAL)
        page_sizer.AddSpacer(10)
        page_sizer.Add(radio_box, 0, wxALL, 5)
        page_sizer.Add(path_add_sizer, 0, wxEXPAND|wxALL, 5)
        page_sizer.Add(LMR_sizer, 5, wxEXPAND|wxLEFT|wxRIGHT|wxBOTTOM, 5)
        
        sizer = wxFlexGridSizer(1, 2)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(1, 2)
        sizer.Add(self.dir_tree, 1, wxEXPAND|wxLEFT|wxTOP|wxBOTTOM, 5)
        sizer.Add(page_sizer, 1, wxEXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        
        # Lists of widgets that change language
        self.setlabels = {	self.dest_browse: "Custom" }
    
    
    def SetLanguage(self):
        # Get language pack for Files tab
        lang = languages.Files()
        
        # Grandparent has language settings
        cur_lang = self.GetGrandParent().GetLanguage()
        
        for item in self.setlabels:
            item.SetLabel(lang.GetLanguage(self.setlabels[item], cur_lang))
        
        # Refresh widget layout
        self.Layout()
    
    
    def OnRightClick(self, event):
        # Show a context menu for adding files and folders
        path = self.dir_tree.GetPath()
        if isdir(path):
            self.add_dir.Enable(True)
            self.add_file.Enable(False)
        elif isfile(path):
            self.add_dir.Enable(False)
            self.add_file.Enable(True)
        self.dir_tree.PopupMenu(self.menu)
    
    def OnBrowse(self, event):
        if self.parent.parent.cust_dias.IsChecked() == True:
            dia = db.OpenDir(self)
            if dia.DisplayModal() == True:
                self.dest_cust.SetValue(dia.GetPath())
        else:
            dia = wxDirDialog(self, _('Choose Target Directory'), os.getcwd(), wxDD_CHANGE_DIR)
            if dia.ShowModal() == wxID_OK:
                self.dest_cust.SetValue(dia.GetPath())
#		if dia.GetPath() == True:
#			self.dest_cust.SetValue(dia.GetPath())
#		if dia.Open == True:
#			self.dest_cust.SetValue(dia.GetPath())
    
    def GetDestValue(self, event):
        if self.dest_cust.GetValue() != wxEmptyString:
            if self.dest_cust.GetValue()[0] == "/":
                self.prev_dest_value = self.dest_cust.GetValue()
        event.Skip()
    
    def CheckDest(self, event):
        if self.dest_cust.GetValue() == wxEmptyString:
            self.dest_cust.SetValue(self.prev_dest_value)
            self.dest_cust.SetInsertionPoint(-1)
        elif self.dest_cust.GetValue()[0] != "/":
            self.dest_cust.SetValue(self.prev_dest_value)
            self.dest_cust.SetInsertionPoint(-1)
        event.Skip()
    
    def AddPath(self, event):
        total_files = 0
        pin = self.dir_tree.GetPath()
        
        for item in self.radio_group:
            if self.radio_cst.GetValue() == True:
                pout = self.dest_cust.GetValue()
            elif item.GetValue() == True:
                pout = item.GetLabel()
        if isdir(pin):
            for root, dirs, files in os.walk(pin):
                for file in files:
                    total_files += 1
            
            if total_files: # Continue if files are found
                cont = True
                count = 0
                msg_files = _('Getting files from %s')
                loading = wxProgressDialog(_('Progress'), msg_files % (pin), total_files, self,
                                            wxPD_AUTO_HIDE|wxPD_ELAPSED_TIME|wxPD_ESTIMATED_TIME|wxPD_CAN_ABORT)
                for root, dirs, files in os.walk(pin):
                    for file in files:
                        if cont == (False,False):  # If "cancel" pressed destroy the progress window
                            break
                        else:
                            sub_dir = root.split(pin)[1] # remove full path to insert into listctrl
                            if sub_dir != wxEmptyString:
                                # Add the sub-dir to dest
                                dest = "%s%s" % (pout, sub_dir)
                                #self.list_data.insert(0, ("%s/%s" % (root, file), "%s/%s" % (sub_dir[1:], file), dest))
                                self.list_data.insert(0, (u'%s/%s' % (root, file), file, dest))
                                self.dest_area.InsertStringItem(0, file)
                                self.dest_area.SetStringItem(0, 1, dest)
                            else:
                                self.list_data.insert(0, (u'%s/%s' % (root, file), file, pout))
                                self.dest_area.InsertStringItem(0, file)
                                self.dest_area.SetStringItem(0, 1, pout)
                            count += 1
                            cont = loading.Update(count)
                            if os.access("%s/%s" % (root,file), os.X_OK):
                                self.dest_area.SetItemTextColour(0, "red")
        
        elif isfile(pin):
            file = os.path.split(pin)[1]
            file = file.encode('utf-8')
            self.list_data.insert(0, (pin, file, pout))
            self.dest_area.InsertStringItem(0, file)
            self.dest_area.SetStringItem(0, 1, pout)
            if os.access(pin, os.X_OK):
                self.dest_area.SetItemTextColour(0, "red")
    
    def OnRefresh(self, event):
        path = self.dir_tree.GetPath()
#		if isfile(path):
#			path = os.path.split(path)[0]
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(path)
    
    def SelectAll(self):
        total_items = self.dest_area.GetItemCount()
        count = -1
        while count < total_items:
            count += 1
            self.dest_area.Select(count)
    
    def DelPath(self, event):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode == wxWXK_DELETE:
            selected = [] # Items to remove from visible list
            toremove = [] # Items to remove from invisible list
            total = self.dest_area.GetSelectedItemCount()
            current = self.dest_area.GetFirstSelected()
            if current != -1:
                selected.insert(0, current)
                while total > 1:
                    total = total - 1
                    prev = current
                    current = self.dest_area.GetNextSelected(prev)
                    selected.insert(0, current)
            for path in selected:
                # Remove the item from the invisible list
                for item in self.list_data:
                    file = self.dest_area.GetItemText(path)
                    dest = self.dest_area.GetItem(path, 1).GetText()
                    if file.encode('utf-8') == item[1].decode('utf-8') and dest.encode('utf-8') == item[2].decode('utf-8'):
                        toremove.append(item)
                    
                self.dest_area.DeleteItem(path) # Remove the item from the visible list
            
            for item in toremove:
                self.list_data.remove(item)
            
        elif keycode == 65 and modifier == wxMOD_CONTROL:
            self.SelectAll()
    
    
    def ClearAll(self, event):
        confirm = wxMessageDialog(self, _('Clear all files?'), _('Confirm'), wxYES_NO|wxNO_DEFAULT|wxICON_QUESTION)
        if confirm.ShowModal() == wxID_YES:
            self.dest_area.DeleteAllItems()
            self.list_data = []
    
    def SetDestination(self, event):
        # Event handler that disables the custom destination if the corresponding radio button isn't selected
        if self.radio_cst.GetValue() == True:
            self.dest_cust.Enable()
            self.dest_browse.Enable()
        else:
            self.dest_cust.Disable()
            self.dest_browse.Disable()
    
    
    def ResetAllFields(self):
        self.radio_cst.SetValue(True)
        self.SetDestination(None)
        self.dest_cust.SetValue("/usr/bin")
        self.dest_area.DeleteAllItems()
        self.list_data = []
    
    def SetFieldData(self, data):
        # Clear files list
        self.list_data = []
        self.dest_area.DeleteAllItems()
        files_data = data.split("\n")
        if int(files_data[0]):
            # Get file count from list minus first item "1"
            files_total = len(files_data)
            
            # Store missing files here
            missing_files = []
            
            while files_total > 1:
                files_total -= 1
                src = (files_data[files_total].split(" -> ")[0], False)
                
                # False changes to true if src file is executable
                if src[0][-1] == "*":
                    src = (src[0][:-1], True) # Set executable flag and remove "*"
                file = files_data[files_total].split(" -> ")[1]
                dest = files_data[files_total].split(" -> ")[2]
                
                # Check if files still exist
                if os.path.exists(src[0]):
                    self.dest_area.InsertStringItem(0, file)
                    self.dest_area.SetStringItem(0, 1, dest)
                    self.list_data.insert(0, (src[0], file, dest))
                    # Check if file is executable
                    if src[1]:
                        self.dest_area.SetItemTextColour(0, "red") # Set text color to red
                else:
                    missing_files.append(src[0])
            
            # If files are missing show a message
            if len(missing_files):
                alert = wxDialog(self, -1, _('Missing Files'))
                alert_text = wxStaticText(alert, -1, _('Could not locate the following files:'))
                alert_list = wxTextCtrl(alert, -1, style=wxTE_MULTILINE|wxTE_READONLY)
                alert_list.SetValue("\n".join(missing_files))
                button_ok = wxButton(alert, wxID_OK)
                
                alert_sizer = wxBoxSizer(wxVERTICAL)
                alert_sizer.AddSpacer(5)
                alert_sizer.Add(alert_text, 1)
                alert_sizer.Add(alert_list, 3, wxEXPAND)
                alert_sizer.Add(button_ok, 0, wxALIGN_RIGHT)
                
                alert.SetSizerAndFit(alert_sizer)
                alert.Layout()
                
                alert.ShowModal()
    
    def GatherData(self):
        file_list = []
        item_count = self.dest_area.GetItemCount()
        if item_count > 0:
            count = 0
            while count < item_count:
                item_file = self.dest_area.GetItemText(count)
                item_dest = self.dest_area.GetItem(count, 1).GetText()
                for item in self.list_data:
                    # Decode to unicode
                    i0 = item[0].encode('utf-8')
                    i1 = item[1].decode('utf-8')
                    i2 = item[2].encode('utf-8')
                    if i1 == item_file and i2.decode('utf-8') == item_dest:
                        item_src = i0
                # Populate list with tuples of ("src", "file", "dest")
                if self.dest_area.GetItemTextColour(count) == (255, 0, 0):
                    file_list.append(("%s*" % item_src, item_file, item_dest))
                else:
                    file_list.append((item_src, item_file, item_dest))
                count += 1
        
            return_list = []
            for file in file_list:
                f0 = u'%s'.encode('utf-8') % file[0]
                f1 = u'%s'.encode('utf-8') % file[1]
                f2 = u'%s'.encode('utf-8') % file[2]
                return_list.append(u'%s -> %s -> %s' % (f0, f1, f2))
            return "<<FILES>>\n1\n%s\n<</FILES>>" % "\n".join(return_list)
        else:
            # Place a "0" in FILES field if we are not saving any files
            return "<<FILES>>\n0\n<</FILES>>"