# -*- coding: utf-8 -*-

## \package wiz_bin.depends

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonAppend
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonRemove
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from dbr.listinput      import ListCtrlPanel
from dbr.panel          import BorderedPanel
from globals.ident      import FID_LIST
from globals.ident      import ID_APPEND
from globals.ident      import ID_DEPENDS
from globals.tooltips   import SetPageToolTips


## Page defining dependencies
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_DEPENDS, name=GT(u'Dependencies and Conflicts'))
        
        self.SetScrollbars(20, 20, 0, 0)
        
        txt_package = wx.StaticText(self, label=GT(u'Dependency/Conflict Package Name'), name=u'package')
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        
        self.ti_package = wx.TextCtrl(self, size=(300,25), name=u'package')
        
        opts_operator = (u'>=', u'<=', u'=', u'>>', u'<<')
        self.sel_operator = wx.Choice(self, choices=opts_operator, name=u'operator')
        self.sel_operator.default = 0
        self.sel_operator.SetSelection(self.sel_operator.default)
        
        self.ti_version = wx.TextCtrl(self, name=u'version')
        
        self.ti_package.SetSize((100,50))
        
        pnl_categories = BorderedPanel(self)
        
        self.default_category = u'Depends'
        
        rb_dep = wx.RadioButton(pnl_categories, label=GT(u'Depends'), name=self.default_category, style=wx.RB_GROUP)
        rb_pre = wx.RadioButton(pnl_categories, label=GT(u'Pre-Depends'), name=u'Pre-Depends')
        rb_rec = wx.RadioButton(pnl_categories, label=GT(u'Recommends'), name=u'Recommends')
        rb_sug = wx.RadioButton(pnl_categories, label=GT(u'Suggests'), name=u'Suggests')
        rb_enh = wx.RadioButton(pnl_categories, label=GT(u'Enhances'), name=u'Enhances')
        rb_con = wx.RadioButton(pnl_categories, label=GT(u'Conflicts'), name=u'Conflicts')
        rb_rep = wx.RadioButton(pnl_categories, label=GT(u'Replaces'), name=u'Replaces')
        rb_break = wx.RadioButton(pnl_categories, label=GT(u'Breaks'), name=u'Breaks')
        
        self.categories = (
            rb_dep, rb_pre, rb_rec,
            rb_sug, rb_enh, rb_con,
            rb_rep, rb_break,
        )
        
        # Buttons to add and remove dependencies from the list
        btn_add = ButtonAdd(self)
        btn_append = ButtonAppend(self)
        btn_remove = ButtonRemove(self, wx.ID_DELETE) # Change the id from wx.WXK_DELETE as workaround
        btn_clear = ButtonClear(self)
        
        # ----- List
        self.lst_deps = ListCtrlPanel(self, FID_LIST, style=wx.LC_REPORT, name=u'list')
        self.lst_deps.InsertColumn(0, GT(u'Category'), width=150)
        self.lst_deps.InsertColumn(1, GT(u'Package(s)'))
        
        # wx 3.0 compatibility
        if wx.MAJOR_VERSION < 3:
            self.lst_deps.SetColumnWidth(100, wx.LIST_AUTOSIZE)
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        
        layt_labels = wx.GridBagSizer()
        
        # Row 1
        layt_labels.Add(txt_package, (0, 0), flag=LEFT_BOTTOM)
        layt_labels.Add(txt_version, (0, 2), flag=LEFT_BOTTOM)
        
        # Row 2
        layt_labels.Add(self.ti_package, (1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        layt_labels.Add(self.sel_operator, (1, 1))
        layt_labels.Add(self.ti_version, (1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        layt_categories = wx.GridSizer(4, 2, 5, 5)
        
        for C in self.categories:
            layt_categories.Add(C, 0)
        
        pnl_categories.SetAutoLayout(True)
        pnl_categories.SetSizer(layt_categories)
        pnl_categories.Layout()
        
        layt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        layt_buttons.AddMany((
            (btn_add, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_append, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_remove, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_clear, 0, wx.ALIGN_CENTER_VERTICAL),
            ))
        
        layt_top = wx.GridBagSizer(5, 5)
        layt_top.SetCols(2)
        
        layt_top.Add(wx.StaticText(self, label=u'Categories'), (0, 0), (1, 1), LEFT_BOTTOM)
        layt_top.Add(pnl_categories, (1, 0), flag=wx.RIGHT, border=5)
        layt_top.Add(layt_buttons, (1, 1), flag=wx.ALIGN_BOTTOM)
        
        layt_list = wx.BoxSizer(wx.HORIZONTAL)
        layt_list.Add(self.lst_deps, 1, wx.EXPAND)
        
        layt_main = wx.BoxSizer(wx.VERTICAL)
        # Spacer on this page is half because text is aligned to bottom
        layt_main.AddSpacer(5)
        layt_main.Add(layt_labels, 0, wx.EXPAND|wx.ALL, 5)
        layt_main.Add(layt_top, 0, wx.ALL, 5)
        layt_main.Add(layt_list, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        wx.EVT_KEY_DOWN(self.ti_package, self.SetDepends)
        wx.EVT_KEY_DOWN(self.ti_version, self.SetDepends)
        
        btn_add.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_append.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_remove.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_clear.Bind(wx.EVT_BUTTON, self.SetDepends)
        
        wx.EVT_KEY_DOWN(self.lst_deps, self.SetDepends)
    
    
    ## Add a category & dependency to end of list
    #  
    #  \param category
    #        \b \e unicode|str : Category label
    #  \param value
    #        \b \e unicode|str : Dependency value
    def AppendDependency(self, category, value):
        self.lst_deps.AppendStringItem((category, value))
    
    
    ## TODO: Doxygen
    def GetDefaultCategory(self):
        return self.default_category
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        for C in self.categories:
            if C.GetName() == self.default_category:
                C.SetValue(True)
                break
        
        self.ti_package.Clear()
        self.sel_operator.SetSelection(self.sel_operator.default)
        self.ti_version.Clear()
        self.lst_deps.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetDepends(self, event=None):
        try:
            key_id = event.GetKeyCode()
        
        except AttributeError:
            key_id = event.GetEventObject().GetId()
        
        addname = self.ti_package.GetValue()
        oper = self.sel_operator.GetStringSelection()
        ver = self.ti_version.GetValue()
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
            selected_count = self.lst_deps.GetSelectedItemCount()
            if not TextIsEmpty(addname) and self.lst_deps.GetItemCount() and selected_count:
                listrow = None
                for X in range(selected_count):
                    if listrow == None:
                        listrow = self.lst_deps.GetFirstSelected()
                    
                    else:
                        listrow = self.lst_deps.GetNextSelected(listrow)
                    
                    # Get item from second column
                    colitem = self.lst_deps.GetItem(listrow, 1)
                    # Get the text from that item
                    prev_text = colitem.GetText()
                    
                    if not TextIsEmpty(ver):
                        self.lst_deps.SetStringItem(listrow, 1, u'{} | {} {}'.format(prev_text, addname, addver))
                    
                    else:
                        self.lst_deps.SetStringItem(listrow, 1, u'{} | {}'.format(prev_text, addname))
        
        elif key_id == wx.ID_DELETE:
            self.lst_deps.RemoveSelected()
        
        elif key_id == wx.ID_CLEAR:
            if self.lst_deps.GetItemCount():
                confirm = wx.MessageDialog(self, GT(u'Clear all dependencies?'), GT(u'Confirm'),
                        wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                if confirm.ShowModal() == wx.ID_YES:
                    self.lst_deps.DeleteAllItems()
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def SetFieldData(self, data):
        self.lst_deps.DeleteAllItems()
        for item in data:
            item_count = len(item)
            while item_count > 1:
                item_count -= 1
                self.lst_deps.InsertStringItem(0, item[0])
                self.lst_deps.SetStringItem(0, 1, item[item_count])
