# -*- coding: utf-8 -*-

## \package wiz_bin.depends


import wx
from wx.lib.mixins import listctrl as wxMixinListCtrl

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonAppend
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonDel
from dbr.language       import GT
from dbr.log            import Logger
from dbr.wizard         import WizardPage
from globals.ident      import ID_DEPENDS, ID_APPEND
from globals.tooltips   import SetPageToolTips


class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_DEPENDS)
        
        # Bypass checking this page for build
        self.prebuild_check = False
        
        # --- DEPENDS
        self.dep_chk = wx.RadioButton(self, -1, GT(u'Depends'), name=u'Depends', style=wx.RB_GROUP)
        #self.dep_chk.SetToolTip(dep_tip)
        #SetToolTip(TT_depends[u'depends'], self.dep_chk)
        
        # --- PRE-DEPENDS
        self.pre_chk = wx.RadioButton(self, -1, GT(u'Pre-Depends'), name=u'Pre-Depends')
        #self.pre_chk.SetToolTip(pre_tip)
        
        # --- RECOMMENDS
        self.rec_chk = wx.RadioButton(self, -1, GT(u'Recommends'), name=u'Recommends')
        #self.rec_chk.SetToolTip(rec_tip)
        
        # --- SUGGESTS
        self.sug_chk = wx.RadioButton(self, -1, GT(u'Suggests'), name=u'Suggests')
        #self.sug_chk.SetToolTip(sug_tip)
        
        # --- ENHANCES
        self.enh_chk = wx.RadioButton(self, -1, GT(u'Enhances'), name=u'Enhances')
        #self.enh_chk.SetToolTip(enh_tip)
        
        # --- CONFLICTS
        self.con_chk = wx.RadioButton(self, -1, GT(u'Conflicts'), name=u'Conflicts')
        #self.con_chk.SetToolTip(con_tip)
        
        # --- REPLACES
        self.rep_chk = wx.RadioButton(self, -1, GT(u'Replaces'), name=u'Replaces')
        #self.rep_chk.SetToolTip(rep_tip)
        
        # --- BREAKS
        self.break_chk = wx.RadioButton(self, -1, GT(u'Breaks'), name=u'Breaks')
        #self.break_chk.SetToolTip(break_tip)
        
        
        # Input for dependencies
        self.ver_text = wx.StaticText(self, -1, GT(u'Version'), name=u'version')
        self.pack_text = wx.StaticText(self, -1, GT(u'Package'), name=u'package')
        
        self.dep_name = wx.TextCtrl(self, -1, size=(300,25), name=u'package')
        
        self.oper_options = (u'>=', u'<=', u'=', u'>>', u'<<')
        self.dep_oper = wx.Choice(self, -1, choices=self.oper_options)
        self.dep_oper.SetSelection(0)
        
        self.dep_ver = wx.TextCtrl(self, -1, name=u'version')
        
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
        self.depadd = ButtonAdd(self)
        self.depadd.SetName(u'add')
        self.depapp = ButtonAppend(self)
        self.depapp.SetName(u'append')
        self.deprem = ButtonDel(self)
        self.deprem.SetName(u'remove')
        self.depclr = ButtonClear(self)
        self.depclr.SetName(u'clear')
        
        wx.EVT_BUTTON(self.depadd, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depapp, -1, self.SetDepends)
        wx.EVT_BUTTON(self.deprem, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depclr, -1, self.SetDepends)
        
        # ----- List
        self.dep_area = AutoListCtrl(self)
        self.dep_area.SetName(u'list')
        self.dep_area.InsertColumn(0, GT(u'Category'), width=150)
        self.dep_area.InsertColumn(1, GT(u'Package(s)'))
        # FIXME: wx. 3.0
        if (wx.MAJOR_VERSION < 3):
            self.dep_area.SetColumnWidth(100, wx.LIST_AUTOSIZE)
        
        wx.EVT_KEY_DOWN(self.dep_area, self.SetDepends)
        
        # Start some sizing
        radio_box = wx.StaticBoxSizer(wx.StaticBox(self, -1, GT(u'Categories')), wx.VERTICAL)
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
        
        
        SetPageToolTips(self)
    
    
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
        
        elif key_id == ID_APPEND:
            listrow = self.dep_area.GetFocusedItem()  # Get row of selected item
            colitem = self.dep_area.GetItem(listrow, 1)  # Get item from second column
            prev_text = colitem.GetText()  # Get the text from that item
            if addname != u'':
                if ver != u'':
                    self.dep_area.SetStringItem(listrow, 1, u'%s | %s %s' % (prev_text, addname, addver))
                else:
                    self.dep_area.SetStringItem(listrow, 1, u'%s | %s' % (prev_text, addname))
        
        elif key_id == wx.ID_DELETE: # wx.WXK_DELETE:
            selected = None
            while selected != -1:
                selected = self.dep_area.GetFirstSelected()
                self.dep_area.DeleteItem(selected)
        
        elif key_id == 65 and key_mod == 2:
            self.SelectAll()
        
        elif key_id == wx.WXK_ESCAPE:
            # Create the dialog
            confirm = wx.MessageDialog(self, GT(u'Clear all dependencies?'), GT(u'Confirm'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if confirm.ShowModal() == wx.ID_YES:
                self.dep_area.DeleteAllItems()
        
        event.Skip()
    
    
    # FIXME: deprecated
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
    
    
    def ImportPageInfo(self, d_type, d_string):
        Logger.Debug(__name__, GT(u'Importing {}: {}'.format(d_type, d_string)))
        
        values = d_string.split(u', ')
        
        for V in values:
            self.dep_area.InsertStringItem(0, d_type)
            self.dep_area.SetStringItem(0, 1, V)
    
    
    ## Resets all fields on page to default values
    def ResetPageInfo(self):
        self.dep_area.DeleteAllItems()
    


## A ListCtrl that automatically expands columns
class AutoListCtrl(wx.ListCtrl, wxMixinListCtrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, window_id=wx.ID_ANY):
        wx.ListCtrl.__init__(self, parent, window_id, style=wx.BORDER_SIMPLE|wx.LC_REPORT)
        wxMixinListCtrl.ListCtrlAutoWidthMixin.__init__(self)
        
        self.prev_width = self.Size[0]
        
        if wx.MAJOR_VERSION == 3 and wx.MINOR_VERSION == 0:
            wx.EVT_SIZE(self, self.OnResize)
    
    
    ## Fixes sizing problems with ListCtrl in wx 3.0
    def OnResize(self, event):
        if event:
            event.Skip(True)
        
        # FIXME: -10 should be a dynamic number set by the sizer's padding
        self.SetSize(wx.Size(self.GetParent().Size[0] - 10, self.Size[1]))
