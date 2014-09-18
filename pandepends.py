# Page defining dependencies

import wxversion
wxversion.select(['2.6', '2.7', '2.8'])
import wx, wx.lib.mixins.listctrl as LC, db

ID = wx.NewId()

ID_Append = wx.NewId()
ID_Delete = wx.NewId()

class Panel(wx.Panel):
    def __init__(self, parent, id=ID):
        wx.Panel.__init__(self, parent, id, name=_('Dependencies and Conflicts'))
        
        # For identifying page to parent
        #self.ID = "DEP"
        
        # Allows calling parent methods
        self.parent = parent
        
        # ----- Tool Tips
        dep_tip = wx.ToolTip(_('Package will need to be installed'))
        pre_tip = wx.ToolTip(_('Package will need to be installed and configured first'))
        rec_tip = wx.ToolTip(_('Package is highly recommended and will be installed by default'))
        sug_tip = wx.ToolTip(_('Package may be useful but is not necessary and will not be installed by default'))
        enh_tip = wx.ToolTip(_('This package may be useful to enhanced package'))
        con_tip = wx.ToolTip(_('Package will be removed from the system if it is installed'))
        rep_tip = wx.ToolTip(_('Package or its files may be overwritten'))
        break_tip = wx.ToolTip(_('Package conflicts and will be de-configured'))
#        syn_tip = wx.ToolTip("Breifly summarize the purpose of the application")
#        desc_tip = wx.ToolTip("Here you can give a more detailed explanation\n\n\
#If you need help open \"Help/Example Control\" for details on formatting")
        
        
        # Display a nice title
#		self.title = wx.StaticText(self, -1) #Title for dependencies and conflictions
#		self.title.SetFont(parent.BoldFont)
        
        # --- DEPENDS
        self.dep_chk = wx.RadioButton(self, -1, _('Depends'), name='Depends', style=wx.RB_GROUP)
        self.dep_chk.SetToolTip(dep_tip)
        
        # --- PRE-DEPENDS
        self.pre_chk = wx.RadioButton(self, -1, _('Pre-Depends'), name='Pre-Depends')
        self.pre_chk.SetToolTip(pre_tip)
        
        # --- RECOMMENDS
        self.rec_chk = wx.RadioButton(self, -1, _('Recommends'), name='Recommends')
        self.rec_chk.SetToolTip(rec_tip)
        
        # --- SUGGESTS
        self.sug_chk = wx.RadioButton(self, -1, _('Suggests'), name='Suggests')
        self.sug_chk.SetToolTip(sug_tip)
        
        # --- ENHANCES
        self.enh_chk = wx.RadioButton(self, -1, _('Enhances'), name='Enhances')
        self.enh_chk.SetToolTip(enh_tip)
        
        # --- CONFLICTS
        self.con_chk = wx.RadioButton(self, -1, _('Conflicts'), name='Conflicts')
        self.con_chk.SetToolTip(con_tip)
        
        # --- REPLACES
        self.rep_chk = wx.RadioButton(self, -1, _('Replaces'), name='Replaces')
        self.rep_chk.SetToolTip(rep_tip)
        
        # --- BREAKS
        self.break_chk = wx.RadioButton(self, -1, _('Breaks'), name='Breaks')
        self.break_chk.SetToolTip(break_tip)
        
        
        # Input for dependencies
        self.pack_text = wx.StaticText(self, -1, _('Package'))
        self.dep_name = wx.TextCtrl(self, -1, size=(300,25))
        self.oper_options = (">=", "<=", "=", ">>", "<<")
        self.ver_text = wx.StaticText(self, -1, _('Version'))
        self.dep_oper = wx.Choice(self, -1, choices=self.oper_options)
        self.dep_ver = wx.TextCtrl(self, -1)
        
        depH1 = wx.FlexGridSizer(2, 3, hgap=5)
        depH1.AddGrowableCol(2)
        depH1.Add(self.pack_text, 0, wx.LEFT, 2)
        depH1.AddSpacer(0)
        depH1.Add(self.ver_text, 1, wx.EXPAND|wx.LEFT, 2)
        depH1.Add(self.dep_name)
        depH1.Add(self.dep_oper)
        depH1.Add(self.dep_ver, 1, wx.EXPAND)
        
        self.dep_name.SetSize((100,50))
        
        # Add KEY_DOWN events to text areas
        wx.EVT_KEY_DOWN(self.dep_name, self.SetDepends)
        wx.EVT_KEY_DOWN(self.dep_ver, self.SetDepends)
        
        # Buttons to add and remove dependencies from the list
        self.depadd = db.ButtonAdd(self)
        self.depapp = db.ButtonPipe(self, ID_Append)
        self.deprem = db.ButtonDel(self, ID_Delete) # Change the id from wx.WXK_DELETE as workaround
        self.depclr = db.ButtonClear(self)
        
        wx.EVT_BUTTON(self.depadd, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depapp, -1, self.SetDepends)
        wx.EVT_BUTTON(self.deprem, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depclr, -1, self.SetDepends)
        
        # ----- List
        self.dep_area = AutoListCtrl(self, -1)
        self.dep_area.InsertColumn(0, _('Category'), width=150)
        self.dep_area.InsertColumn(1, _('Package(s)'))
        self.dep_area.SetColumnWidth(100, -1)
        
        wx.EVT_KEY_DOWN(self.dep_area, self.SetDepends)
        
        # Start some sizing
        radio_box = wx.StaticBoxSizer(wx.StaticBox(self, -1, _('Categories')), wx.VERTICAL)
        rg1 = wx.GridSizer(4, 2, 5, 5)
        rg1.AddMany( [
        (self.dep_chk, 0),
        (self.pre_chk, 0),
        (self.rec_chk, 0),
        (self.sug_chk, 0),
        (self.enh_chk, 0),
        (self.con_chk, 0),
        (self.rep_chk, 0),
        (self.break_chk, 0) ])
        
        radio_box.Add(rg1, 0)
        
        depH2 = wx.BoxSizer(wx.HORIZONTAL)
        depH2.Add(radio_box, 0, wx.RIGHT, 5)
        depH2.Add(self.depadd, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        depH2.Add(self.depapp, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        depH2.Add(self.deprem, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        depH2.Add(self.depclr, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        
        self.border = wx.StaticBox(self, -1)
        border_box = wx.StaticBoxSizer(self.border, wx.VERTICAL)
        border_box.Add(depH1, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        border_box.AddSpacer(5)
        border_box.Add(depH2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        
        depH3 = wx.BoxSizer(wx.HORIZONTAL)
        depH3.Add(self.dep_area, 1, wx.EXPAND)
        
        # ----- Main Sizer
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page_sizer.AddSpacer(10)
#		page_sizer.Add(self.title, 0, wx.ALIGN_CENTER)
#		page_sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)
#		page_sizer.AddSpacer(10)
#		page_sizer.Add(depH1, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
#		page_sizer.AddSpacer(5)
#		page_sizer.Add(depH2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        page_sizer.Add(border_box, 0, wx.LEFT, 5)
        page_sizer.Add(depH3, 1, wx.EXPAND|wx.ALL, 5)
        
        # ----- Layout
        self.SetAutoLayout(True)
        self.SetSizer(page_sizer)
        self.Layout()
        
        # ----- List not needed anymore
        self.setlabels = {	self.border: "Border", self.pack_text: "Pack", self.ver_text: "Ver",
                            self.depadd: "Add", self.depapp: "App", self.deprem: "Rem"}
        
        self.categories = {	self.dep_chk: "Depends", self.pre_chk: "Pre-Depends", self.rec_chk: "Recommends",
                            self.sug_chk: "Suggests", self.enh_chk: "Enhances", self.con_chk: "Conflicts",
                            self.rep_chk: "Replaces", self.break_chk: "Breaks"}
    
    
    def SetLanguage(self):
        lang = languages.Depends()
        
        # Set to language changing to
        if self.parent.parent.lang_en.IsChecked():
            cur_lang = "English"
        elif self.parent.parent.lang_es.IsChecked():
            cur_lang = "Spanish"
        
        # Grab widgets from lists
        for item in self.setlabels:
            item.SetLabel(lang.GetLanguage(self.setlabels[item], cur_lang))
        for item in self.categories:
            item.SetLabel(lang.GetLanguage(self.categories[item], cur_lang))
        
        # Refresh widget layout
        self.Layout()
    
    def SelectAll(self):
        total_items = self.dep_area.GetItemCount()
        count = -1
        while count < total_items:
            count += 1
            self.dep_area.Select(count)
    
    def SetDepends(self, event):
        # Set language to display for dialog
#		dia_lang = languages.ConfirmDialog()
#		if self.GetGrandParent().lang_en.IsChecked():
#			cur_lang = "English"
#		elif self.GetGrandParent().lang_es.IsChecked():
#			cur_lang = "Spanish"
        
        try:
            mod = event.GetModifiers()
            id = event.GetKeyCode()
        except AttributeError:
            mod = None
            id = event.GetEventObject().GetId()
        
        addname = self.dep_name.GetValue()
        oper = self.oper_options[self.dep_oper.GetCurrentSelection()]
        ver = self.dep_ver.GetValue()
        addver = "(%s%s)" % (oper, ver)
            
        if id == wx.WXK_RETURN or id == wx.WXK_NUMPAD_ENTER:
            for item in self.categories:
                if item.GetValue() == True:
                    if addname != "":
                        self.dep_area.InsertStringItem(0, self.categories[item])
                        if ver == "":
                            self.dep_area.SetStringItem(0, 1, addname)
                        else:
                            self.dep_area.SetStringItem(0, 1, "%s %s" % (addname, addver))
        
        elif id == ID_Append:
            listrow = self.dep_area.GetFocusedItem()  # Get row of selected item
            colitem = self.dep_area.GetItem(listrow, 1)  # Get item from second column
            prev_text = colitem.GetText()  # Get the text from that item
            if addname != "":
                if ver != "":
                    self.dep_area.SetStringItem(listrow, 1, "%s | %s %s" % (prev_text, addname, addver))
                else:
                    self.dep_area.SetStringItem(listrow, 1, "%s | %s" % (prev_text, addname))
        
        elif id == ID_Delete: # wx.WXK_DELETE:
            selected = None
            while selected != -1:
                selected = self.dep_area.GetFirstSelected()
                self.dep_area.DeleteItem(selected)
        
        elif id == 65 and mod == 2:
            self.SelectAll()
        
        elif id == wx.WXK_ESCAPE:
            # Create the dialog
#			title = dia_lang.GetLanguage("Message Title", cur_lang)
#			text = dia_lang.GetLanguage("Message Text", cur_lang)
            confirm = wx.MessageDialog(self, _('Clear all dependencies?'), _('Confirm'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if confirm.ShowModal() == wx.ID_YES:
                self.dep_area.DeleteAllItems()
#			confirm = dialogs.Confirm(self)
#			if cur_lang == "English":
#				confirm.SetTitle("Confirm")
#				confirm.SetText(lang.GetLanguage("Message Text", cur_lang))
#				confirm.SetButtonText(lang.GetLanguage("Button Yes", cur_lang), lang.GetLanguage("Button No", cur_lang))
#			elif cur_lang == "Spanish":
#				confirm.SetTitle("Confirmar")
#				confirm.SetText(lang.GetLanguage("Message Text", cur_lang))
#				confirm.SetButtonText(lang.GetLanguage("Button Yes", cur_lang), lang.GetLanguage("Button No", cur_lang))
#			
#			if confirm.DisplayModal():
#				self.dep_area.DeleteAllItems()
        
        event.Skip()
        
        
    def ResetAllFields(self):
        self.dep_chk.SetValue(True)
        self.dep_name.Clear()
        self.dep_oper.SetSelection(0)
        self.dep_ver.Clear()
        self.dep_area.DeleteAllItems()
    
    def SetFieldData(self, data):
        self.dep_area.DeleteAllItems()
        for item in data:
            item_count = len(item)
            while item_count > 1:
                item_count -= 1
                self.dep_area.InsertStringItem(0, item[0])
                self.dep_area.SetStringItem(0, 1, item[item_count])
    


class AutoListCtrl(wx.ListCtrl, LC.ListCtrlAutoWidthMixin):
    """A ListCtrl that automatically expands columns"""
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, style=wx.BORDER_SIMPLE|wx.LC_REPORT)
        LC.ListCtrlAutoWidthMixin.__init__(self)