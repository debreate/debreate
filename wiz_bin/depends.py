# -*- coding: utf-8 -*-

# Page defining dependencies


# System imports
import wx
from wx.lib.mixins import \
    listctrl as wxMixinListCtrl

# Local imports
import dbr
from dbr.constants import ID_DEPENDS


ID_Append = wx.NewId()
ID_Delete = wx.NewId()

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, ID_DEPENDS, name=_(u'Dependencies and Conflicts'))
        
        # ----- Tool Tips
        dep_tip = wx.ToolTip(_(u'Package will need to be installed'))
        pre_tip = wx.ToolTip(_(u'Package will need to be installed and configured first'))
        rec_tip = wx.ToolTip(_(u'Package is highly recommended and will be installed by default'))
        sug_tip = wx.ToolTip(_(u'Package may be useful but is not necessary and will not be installed by default'))
        enh_tip = wx.ToolTip(_(u'This package may be useful to enhanced package'))
        con_tip = wx.ToolTip(_(u'Package will be removed from the system if it is installed'))
        rep_tip = wx.ToolTip(_(u'Package or its files may be overwritten'))
        break_tip = wx.ToolTip(_(u'Package conflicts and will be de-configured'))
#        syn_tip = wx.ToolTip(u'Breifly summarize the purpose of the application')
#        desc_tip = wx.ToolTip(u'Here you can give a more detailed explanation\n\n\
#If you need help open "Help/Example Control" for details on formatting')
        
        
        # Display a nice title
#		self.title = wx.StaticText(self, -1) #Title for dependencies and conflictions
#		self.title.SetFont(parent.BoldFont)
        
        # --- DEPENDS
        self.dep_chk = wx.RadioButton(self, -1, _(u'Depends'), name=u'Depends', style=wx.RB_GROUP)
        self.dep_chk.SetToolTip(dep_tip)
        
        # --- PRE-DEPENDS
        self.pre_chk = wx.RadioButton(self, -1, _(u'Pre-Depends'), name=u'Pre-Depends')
        self.pre_chk.SetToolTip(pre_tip)
        
        # --- RECOMMENDS
        self.rec_chk = wx.RadioButton(self, -1, _(u'Recommends'), name=u'Recommends')
        self.rec_chk.SetToolTip(rec_tip)
        
        # --- SUGGESTS
        self.sug_chk = wx.RadioButton(self, -1, _(u'Suggests'), name=u'Suggests')
        self.sug_chk.SetToolTip(sug_tip)
        
        # --- ENHANCES
        self.enh_chk = wx.RadioButton(self, -1, _(u'Enhances'), name=u'Enhances')
        self.enh_chk.SetToolTip(enh_tip)
        
        # --- CONFLICTS
        self.con_chk = wx.RadioButton(self, -1, _(u'Conflicts'), name=u'Conflicts')
        self.con_chk.SetToolTip(con_tip)
        
        # --- REPLACES
        self.rep_chk = wx.RadioButton(self, -1, _(u'Replaces'), name=u'Replaces')
        self.rep_chk.SetToolTip(rep_tip)
        
        # --- BREAKS
        self.break_chk = wx.RadioButton(self, -1, _(u'Breaks'), name=u'Breaks')
        self.break_chk.SetToolTip(break_tip)
        
        
        # Input for dependencies
        self.pack_text = wx.StaticText(self, -1, _(u'Package'))
        self.dep_name = wx.TextCtrl(self, -1, size=(300,25))
        self.oper_options = (u'>=', u'<=', u'=', u'>>', u'<<')
        self.ver_text = wx.StaticText(self, -1, _(u'Version'))
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
        self.depadd = dbr.ButtonAdd(self)
        self.depapp = dbr.ButtonPipe(self, ID_Append)
        self.deprem = dbr.ButtonDel(self, ID_Delete) # Change the id from wx.WXK_DELETE as workaround
        self.depclr = dbr.ButtonClear(self)
        
        wx.EVT_BUTTON(self.depadd, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depapp, -1, self.SetDepends)
        wx.EVT_BUTTON(self.deprem, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depclr, -1, self.SetDepends)
        
        # ----- List
        self.dep_area = AutoListCtrl(self, -1)
        self.dep_area.InsertColumn(0, _(u'Category'), width=150)
        self.dep_area.InsertColumn(1, _(u'Package(s)'))
        # FIXME: wx. 3.0
        if (wx.MAJOR_VERSION < 3):
            self.dep_area.SetColumnWidth(100, wx.LIST_AUTOSIZE)
        
        wx.EVT_KEY_DOWN(self.dep_area, self.SetDepends)
        
        # Start some sizing
        radio_box = wx.StaticBoxSizer(wx.StaticBox(self, -1, _(u'Categories')), wx.VERTICAL)
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
        self.setlabels = {	self.border: u'Border', self.pack_text: u'Pack', self.ver_text: u'Ver',
                            self.depadd: u'Add', self.depapp: u'App', self.deprem: u'Rem'}
        
        self.categories = {	self.dep_chk: u'Depends', self.pre_chk: u'Pre-Depends', self.rec_chk: u'Recommends',
                            self.sug_chk: u'Suggests', self.enh_chk: u'Enhances', self.con_chk: u'Conflicts',
                            self.rep_chk: u'Replaces', self.break_chk: u'Breaks'}
    
    
    def SelectAll(self):
        total_items = self.dep_area.GetItemCount()
        count = -1
        while count < total_items:
            count += 1
            self.dep_area.Select(count)
    
    def SetDepends(self, event):
        try:
            key_mod = event.GetModifiers()
            key_id = event.GetKeyCode()
        except AttributeError:
            key_mod = None
            key_id = event.GetEventObject().GetId()
        
        addname = self.dep_name.GetValue()
        oper = self.oper_options[self.dep_oper.GetCurrentSelection()]
        ver = self.dep_ver.GetValue()
        addver = u'(%s%s)' % (oper, ver)
            
        if key_id == wx.WXK_RETURN or key_id == wx.WXK_NUMPAD_ENTER:
            for item in self.categories:
                if item.GetValue() == True:
                    if addname != u'':
                        self.dep_area.InsertStringItem(0, self.categories[item])
                        if ver == u'':
                            self.dep_area.SetStringItem(0, 1, addname)
                        else:
                            self.dep_area.SetStringItem(0, 1, u'%s %s' % (addname, addver))
        
        elif key_id == ID_Append:
            listrow = self.dep_area.GetFocusedItem()  # Get row of selected item
            colitem = self.dep_area.GetItem(listrow, 1)  # Get item from second column
            prev_text = colitem.GetText()  # Get the text from that item
            if addname != u'':
                if ver != u'':
                    self.dep_area.SetStringItem(listrow, 1, u'%s | %s %s' % (prev_text, addname, addver))
                else:
                    self.dep_area.SetStringItem(listrow, 1, u'%s | %s' % (prev_text, addname))
        
        elif key_id == ID_Delete: # wx.WXK_DELETE:
            selected = None
            while selected != -1:
                selected = self.dep_area.GetFirstSelected()
                self.dep_area.DeleteItem(selected)
        
        elif key_id == 65 and key_mod == 2:
            self.SelectAll()
        
        elif key_id == wx.WXK_ESCAPE:
            # Create the dialog
            confirm = wx.MessageDialog(self, _(u'Clear all dependencies?'), _(u'Confirm'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if confirm.ShowModal() == wx.ID_YES:
                self.dep_area.DeleteAllItems()
        
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
    


class AutoListCtrl(wx.ListCtrl, wxMixinListCtrl.ListCtrlAutoWidthMixin):
    """A ListCtrl that automatically expands columns"""
    def __init__(self, parent, window_id=wx.ID_ANY):
        wx.ListCtrl.__init__(self, parent, window_id, style=wx.BORDER_SIMPLE|wx.LC_REPORT)
        wxMixinListCtrl.ListCtrlAutoWidthMixin.__init__(self)