# -*- coding: utf-8 -*-

# Page defining dependencies

import wx

from dbr.buttons    import ButtonAdd
from dbr.buttons    import ButtonClear
from dbr.buttons    import ButtonDel
from dbr.buttons    import ButtonPipe
from dbr.functions  import TextIsEmpty
from dbr.language   import GT
from dbr.listinput  import ListCtrlPanel
from globals.ident  import ID_APPEND
from globals.ident  import ID_DEPENDS


## TODO: Doxygen
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_DEPENDS, name=GT(u'Dependencies and Conflicts'))
        
        self.SetScrollbars(20, 20, 0, 0)
        
        # ----- Tool Tips
        dep_tip = GT(u'Package will need to be installed')
        pre_tip = GT(u'Package will need to be installed and configured first')
        rec_tip = GT(u'Package is highly recommended and will be installed by default')
        sug_tip = GT(u'Package may be useful but is not necessary and will not be installed by default')
        enh_tip = GT(u'This package may be useful to enhanced package')
        con_tip = GT(u'Package will be removed from the system if it is installed')
        rep_tip = GT(u'Package or its files may be overwritten')
        break_tip = GT(u'Package conflicts and will be de-configured')
        
        
        txt_version = wx.StaticText(self, label=GT(u'Version'))
        txt_pack = wx.StaticText(self, label=GT(u'Dependency/Conflict Package Name'))
        
        self.input_pack = wx.TextCtrl(self, size=(300,25))
        
        tt_pack = GT(u'Name of dependency/conflicting package')
        txt_pack.SetToolTipString(tt_pack)
        self.input_pack.SetToolTipString(tt_pack)
        
        opts_oper = (u'>=', u'<=', u'=', u'>>', u'<<')
        self.select_oper = wx.Choice(self, choices=opts_oper)
        self.select_oper.SetSelection(0)
        self.input_version = wx.TextCtrl(self)
        
        tt_oper = GT(u'Operator')
        self.select_oper.SetToolTipString(tt_oper)
        
        tt_ver = GT(u'Version corresponing to package name and operator')
        txt_version.SetToolTipString(tt_ver)
        self.input_version.SetToolTipString(tt_ver)
        
        depH1 = wx.FlexGridSizer(2, 3, hgap=5)
        depH1.AddGrowableCol(2)
        depH1.Add(txt_pack, 0, wx.LEFT, 2)
        depH1.AddSpacer(0)
        depH1.Add(txt_version, 1, wx.EXPAND|wx.LEFT, 2)
        depH1.Add(self.input_pack)
        depH1.Add(self.select_oper)
        depH1.Add(self.input_version, 1, wx.EXPAND)
        
        self.input_pack.SetSize((100,50))
        
        # --- DEPENDS
        self.rb_dep = wx.RadioButton(self, label=GT(u'Depends'), name=u'Depends', style=wx.RB_GROUP)
        self.rb_dep.SetToolTipString(dep_tip)
        
        # --- PRE-DEPENDS
        self.rb_pre = wx.RadioButton(self, label=GT(u'Pre-Depends'), name=u'Pre-Depends')
        self.rb_pre.SetToolTipString(pre_tip)
        
        # --- RECOMMENDS
        self.rb_rec = wx.RadioButton(self, label=GT(u'Recommends'), name=u'Recommends')
        self.rb_rec.SetToolTipString(rec_tip)
        
        # --- SUGGESTS
        self.rb_sug = wx.RadioButton(self, label=GT(u'Suggests'), name=u'Suggests')
        self.rb_sug.SetToolTipString(sug_tip)
        
        # --- ENHANCES
        self.rb_enh = wx.RadioButton(self, label=GT(u'Enhances'), name=u'Enhances')
        self.rb_enh.SetToolTipString(enh_tip)
        
        # --- CONFLICTS
        self.rb_con = wx.RadioButton(self, label=GT(u'Conflicts'), name=u'Conflicts')
        self.rb_con.SetToolTipString(con_tip)
        
        # --- REPLACES
        self.rb_rep = wx.RadioButton(self, label=GT(u'Replaces'), name=u'Replaces')
        self.rb_rep.SetToolTipString(rep_tip)
        
        # --- BREAKS
        self.rb_break = wx.RadioButton(self, label=GT(u'Breaks'), name=u'Breaks')
        self.rb_break.SetToolTipString(break_tip)
        
        
        # Buttons to add and remove dependencies from the list
        self.depadd = ButtonAdd(self)
        self.depapp = ButtonPipe(self)
        self.deprem = ButtonDel(self, wx.ID_DELETE) # Change the id from wx.WXK_DELETE as workaround
        self.depclr = ButtonClear(self)
        
        self.depadd.SetToolTipString(GT(u'Add to package list'))
        self.depapp.SetToolTipString(GT(u'Add as alternative to selected packages in list'))
        self.deprem.SetToolTipString(GT(u'Remove selected packages from list'))
        self.depclr.SetToolTipString(GT(u'Clear package list'))
        
        # ----- List
        self.dep_area = ListCtrlPanel(self, style=wx.LC_REPORT)
        self.dep_area.InsertColumn(0, GT(u'Category'), width=150)
        self.dep_area.InsertColumn(1, GT(u'Package(s)'))
        self.dep_area.SetColumnWidth(0, 100)
        
        self.categories = {	self.rb_dep: u'Depends', self.rb_pre: u'Pre-Depends', self.rb_rec: u'Recommends',
                            self.rb_sug: u'Suggests', self.rb_enh: u'Enhances', self.rb_con: u'Conflicts',
                            self.rb_rep: u'Replaces', self.rb_break: u'Breaks'}
        
        # *** Layout *** #
        
        radio_box = wx.StaticBoxSizer(wx.StaticBox(self, label=GT(u'Categories')), wx.VERTICAL)
        rg1 = wx.GridSizer(4, 2, 5, 5)
        
        rg1.AddMany( [
        (self.rb_dep, 0),
        (self.rb_pre, 0),
        (self.rb_rec, 0),
        (self.rb_sug, 0),
        (self.rb_enh, 0),
        (self.rb_con, 0),
        (self.rb_rep, 0),
        (self.rb_break, 0)
        ] )
        
        radio_box.Add(rg1, 0)
        
        layout_H2 = wx.BoxSizer(wx.HORIZONTAL)
        layout_H2.Add(radio_box, 0, wx.RIGHT, 5)
        layout_H2.Add(self.depadd, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        layout_H2.Add(self.depapp, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        layout_H2.Add(self.deprem, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        layout_H2.Add(self.depclr, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
        
        self.border = wx.StaticBox(self)
        border_box = wx.StaticBoxSizer(self.border, wx.VERTICAL)
        border_box.Add(depH1, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        border_box.AddSpacer(5)
        border_box.Add(layout_H2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        
        layout_H3 = wx.BoxSizer(wx.HORIZONTAL)
        layout_H3.Add(self.dep_area, 1, wx.EXPAND)
        
        layout_main = wx.BoxSizer(wx.VERTICAL)
        layout_main.AddSpacer(10)
        layout_main.Add(border_box, 0, wx.LEFT, 5)
        layout_main.Add(layout_H3, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_main)
        self.Layout()
        
        # *** Events *** #
        
        wx.EVT_KEY_DOWN(self.input_pack, self.SetDepends)
        wx.EVT_KEY_DOWN(self.input_version, self.SetDepends)
        
        self.depadd.Bind(wx.EVT_BUTTON, self.SetDepends)
        self.depapp.Bind(wx.EVT_BUTTON, self.SetDepends)
        self.deprem.Bind(wx.EVT_BUTTON, self.SetDepends)
        self.depclr.Bind(wx.EVT_BUTTON, self.SetDepends)
        
        wx.EVT_KEY_DOWN(self.dep_area, self.SetDepends)
    
    
    ## Add a category & dependency to end of list
    #  
    #  \param category
    #        \b \e unicode|str : Category label
    #  \param value
    #        \b \e unicode|str : Dependency value
    def AppendDependency(self, category, value):
        self.dep_area.AppendStringItem((category, value))
    
    
    ## TODO: Doxygen
    def GetDefaultCategory(self):
        return self.rb_dep.GetName()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.rb_dep.SetValue(True)
        self.input_pack.Clear()
        self.select_oper.SetSelection(0)
        self.input_version.Clear()
        self.dep_area.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetDepends(self, event=None):
        try:
            key_id = event.GetKeyCode()
        
        except AttributeError:
            key_id = event.GetEventObject().GetId()
        
        addname = self.input_pack.GetValue()
        oper = self.select_oper.GetStringSelection()
        ver = self.input_version.GetValue()
        addver = u'({}{})'.format(oper, ver)
            
        if key_id == wx.WXK_RETURN or key_id == wx.WXK_NUMPAD_ENTER:
            if TextIsEmpty(addname):
                return
            
            category = self.GetDefaultCategory()
            for C in self.categories:
                if C.GetValue():
                    category = C.GetName()
                    break
            
            if TextIsEmpty(ver):
                self.AppendDependency(category, addname)
            
            else:
                self.AppendDependency(category, u'{} {}'.format(addname, addver))
        
        elif key_id == ID_APPEND:
            selected_count = self.dep_area.GetSelectedItemCount()
            if not TextIsEmpty(addname) and self.dep_area.GetItemCount() and selected_count:
                listrow = None
                for X in range(selected_count):
                    if listrow == None:
                        listrow = self.dep_area.GetFirstSelected()
                    
                    else:
                        listrow = self.dep_area.GetNextSelected(listrow)
                    
                    colitem = self.dep_area.GetItem(listrow, 1)  # Get item from second column
                    prev_text = colitem.GetText()  # Get the text from that item
                    
                    if not TextIsEmpty(ver):
                        self.dep_area.SetStringItem(listrow, 1, u'{} | {} {}'.format(prev_text, addname, addver))
                    
                    else:
                        self.dep_area.SetStringItem(listrow, 1, u'{} | {}'.format(prev_text, addname))
        
        elif key_id == wx.ID_DELETE:
            self.dep_area.RemoveSelected()
        
        elif key_id == wx.ID_CLEAR:
            if self.dep_area.GetItemCount():
                confirm = wx.MessageDialog(self, GT(u'Clear all dependencies?'), GT(u'Confirm'),
                        wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                if confirm.ShowModal() == wx.ID_YES:
                    self.dep_area.DeleteAllItems()
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def SetFieldData(self, data):
        self.dep_area.DeleteAllItems()
        for item in data:
            item_count = len(item)
            while item_count > 1:
                item_count -= 1
                self.dep_area.InsertStringItem(0, item[0])
                self.dep_area.SetStringItem(0, 1, item[item_count])
