# -*- coding: utf-8 -*-

# Page defining dependencies

import wx
from wx.lib.mixins import listctrl as LC

from dbr.buttons    import ButtonAdd
from dbr.buttons    import ButtonClear
from dbr.buttons    import ButtonDel
from dbr.buttons    import ButtonPipe
from dbr.functions  import TextIsEmpty
from dbr.language   import GT
from globals.ident  import ID_DEPENDS


ID_Append = wx.NewId()
ID_Delete = wx.NewId()


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
        
        
        # Input for dependencies
        self.pack_text = wx.StaticText(self, -1, GT(u'Dependency/Conflict Package Name'))
        self.dep_name = wx.TextCtrl(self, -1, size=(300,25))
        
        tt_pack = GT(u'Name of dependency/conflicting package')
        self.pack_text.SetToolTipString(tt_pack)
        self.dep_name.SetToolTipString(tt_pack)
        
        self.oper_options = (u'>=', u'<=', u'=', u'>>', u'<<')
        self.ver_text = wx.StaticText(self, -1, GT(u'Version'))
        self.dep_oper = wx.Choice(self, -1, choices=self.oper_options)
        self.dep_oper.SetSelection(0)
        self.dep_ver = wx.TextCtrl(self, -1)
        
        tt_oper = GT(u'Operator')
        self.dep_oper.SetToolTipString(tt_oper)
        
        tt_ver = GT(u'Version corresponing to package name and operator')
        self.ver_text.SetToolTipString(tt_ver)
        self.dep_ver.SetToolTipString(tt_ver)
        
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
        
        # --- DEPENDS
        self.dep_chk = wx.RadioButton(self, -1, GT(u'Depends'), name=u'Depends', style=wx.RB_GROUP)
        self.dep_chk.SetToolTipString(dep_tip)
        
        # --- PRE-DEPENDS
        self.pre_chk = wx.RadioButton(self, -1, GT(u'Pre-Depends'), name=u'Pre-Depends')
        self.pre_chk.SetToolTipString(pre_tip)
        
        # --- RECOMMENDS
        self.rec_chk = wx.RadioButton(self, -1, GT(u'Recommends'), name=u'Recommends')
        self.rec_chk.SetToolTipString(rec_tip)
        
        # --- SUGGESTS
        self.sug_chk = wx.RadioButton(self, -1, GT(u'Suggests'), name=u'Suggests')
        self.sug_chk.SetToolTipString(sug_tip)
        
        # --- ENHANCES
        self.enh_chk = wx.RadioButton(self, -1, GT(u'Enhances'), name=u'Enhances')
        self.enh_chk.SetToolTipString(enh_tip)
        
        # --- CONFLICTS
        self.con_chk = wx.RadioButton(self, -1, GT(u'Conflicts'), name=u'Conflicts')
        self.con_chk.SetToolTipString(con_tip)
        
        # --- REPLACES
        self.rep_chk = wx.RadioButton(self, -1, GT(u'Replaces'), name=u'Replaces')
        self.rep_chk.SetToolTipString(rep_tip)
        
        # --- BREAKS
        self.break_chk = wx.RadioButton(self, -1, GT(u'Breaks'), name=u'Breaks')
        self.break_chk.SetToolTipString(break_tip)
        
        
        # Buttons to add and remove dependencies from the list
        self.depadd = ButtonAdd(self)
        self.depapp = ButtonPipe(self, ID_Append)
        self.deprem = ButtonDel(self, ID_Delete) # Change the id from wx.WXK_DELETE as workaround
        self.depclr = ButtonClear(self)
        
        self.depadd.SetToolTipString(GT(u'Add to package list'))
        self.depapp.SetToolTipString(GT(u'Add as alternative to selected packages in list'))
        self.deprem.SetToolTipString(GT(u'Remove selected packages from list'))
        self.depclr.SetToolTipString(GT(u'Clear package list'))
        
        wx.EVT_BUTTON(self.depadd, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depapp, -1, self.SetDepends)
        wx.EVT_BUTTON(self.deprem, -1, self.SetDepends)
        wx.EVT_BUTTON(self.depclr, -1, self.SetDepends)
        
        # ----- List
        self.dep_area = AutoListCtrl(self, -1)
        self.dep_area.InsertColumn(0, GT(u'Category'), width=150)
        self.dep_area.InsertColumn(1, GT(u'Package(s)'))
        self.dep_area.SetColumnWidth(0, 100)
        
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
    
    
    ## TODO: Doxygen
    def GetDefaultCategory(self):
        return self.dep_chk.GetName()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.dep_chk.SetValue(True)
        self.dep_name.Clear()
        self.dep_oper.SetSelection(0)
        self.dep_ver.Clear()
        self.dep_area.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetDepends(self, event):
        try:
            key_id = event.GetKeyCode()
        
        except AttributeError:
            key_id = event.GetEventObject().GetId()
        
        addname = self.dep_name.GetValue()
        oper = self.oper_options[self.dep_oper.GetCurrentSelection()]
        ver = self.dep_ver.GetValue()
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
                self.dep_area.AppendDependency(category, addname)
            
            else:
                self.dep_area.AppendDependency(category, u'{} {}'.format(addname, addver))
        
        elif key_id == ID_Append:
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
        
        elif key_id == ID_Delete:
            self.dep_area.RemoveSelected()
        
        elif key_id == wx.ID_CLEAR:
            if self.dep_area.GetItemCount():
                confirm = wx.MessageDialog(self, GT(u'Clear all dependencies?'), GT(u'Confirm'),
                        wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                if confirm.ShowModal() == wx.ID_YES:
                    self.dep_area.DeleteAllItems()
        
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


## A ListCtrl that automatically expands columns
class AutoListCtrl(wx.ListView, LC.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID=wx.ID_ANY):
        wx.ListView.__init__(self, parent, ID, style=wx.BORDER_SIMPLE|wx.LC_REPORT)
        LC.ListCtrlAutoWidthMixin.__init__(self)
        
        wx.EVT_KEY_DOWN(self, self.OnSelectAll)
    
    
    ## Add a category & dependency to end of list
    #  
    #  \param category
    #        \b \e unicode|str : Category label
    #  \param value
    #        \b \e unicode|str : Dependency value
    def AppendDependency(self, category, value):
        row_index = self.GetItemCount()
        self.InsertStringItem(row_index, category)
        self.SetStringItem(row_index, 1, value)
    
    
    ## Adds an item to the end of the list
    #  
    #  \param item
    #        \b \e unicode|str : String item to append
    def AppendStringItem(self, item):
        self.InsertStringItem(self.GetItemCount(), item)
    
    
    ## TODO: Doxygen
    def GetSelectedIndexes(self):
        selected_indexes = []
        selected = None
        for X in range(self.GetSelectedItemCount()):
            if X == 0:
                selected = self.GetFirstSelected()
            
            else:
                selected = self.GetNextSelected(selected)
            
            selected_indexes.append(selected)
        
        if selected_indexes:
            return tuple(sorted(selected_indexes))
        
        return None
    
    
    ## TODO: Doxygen
    def OnSelectAll(self, event=None):
        select_all = False
        if isinstance(event, wx.KeyEvent):
            if event.GetKeyCode() == 65 and event.GetModifiers() == 2:
                select_all = True
        
        if select_all:
            for X in range(self.GetItemCount()):
                self.Select(X)
    
    
    ## Removes all selected rows in descending order
    def RemoveSelected(self):
        selected_indexes = self.GetSelectedIndexes()
        if selected_indexes != None:
            for index in reversed(selected_indexes):
                self.DeleteItem(index)
