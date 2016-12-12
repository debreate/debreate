# -*- coding: utf-8 -*-

## \package wiz_bin.depends

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.lib.mixins import listctrl as LC

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonAppend
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonRemove
from dbr.functions      import TextIsEmpty
from dbr.help           import HelpButton
from dbr.language       import GT
from dbr.listinput      import ListCtrlPanel
from dbr.log            import Logger
from dbr.wizard         import WizardPage
from globals            import ident
from globals.tooltips   import SetPageToolTips


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.DEPENDS)
        
        # Bypass checking this page for build
        self.prebuild_check = False
        
        
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        txt_package = wx.StaticText(self, label=GT(u'Dependency/Conflict Package Name'), name=u'package')
        
        self.input_package = wx.TextCtrl(self, size=(300,25), name=u'package')
        
        opts_oper = (u'>=', u'<=', u'=', u'>>', u'<<')
        self.select_oper = wx.Choice(self, choices=opts_oper)
        self.select_oper.SetSelection(0)
        
        self.input_version = wx.TextCtrl(self, name=u'version')
        
        # Button to display help information about this page
        btn_help = HelpButton(self)
        
        self.input_package.SetSize((100,50))
        
        categories_panel = wx.Panel(self, style=wx.BORDER_THEME)
        
        rb_dep = wx.RadioButton(categories_panel, label=GT(u'Depends'), name=u'Depends', style=wx.RB_GROUP)
        rb_pre = wx.RadioButton(categories_panel, label=GT(u'Pre-Depends'), name=u'Pre-Depends')
        rb_rec = wx.RadioButton(categories_panel, label=GT(u'Recommends'), name=u'Recommends')
        rb_sug = wx.RadioButton(categories_panel, label=GT(u'Suggests'), name=u'Suggests')
        rb_enh = wx.RadioButton(categories_panel, label=GT(u'Enhances'), name=u'Enhances')
        rb_con = wx.RadioButton(categories_panel, label=GT(u'Conflicts'), name=u'Conflicts')
        rb_rep = wx.RadioButton(categories_panel, label=GT(u'Replaces'), name=u'Replaces')
        rb_break = wx.RadioButton(categories_panel, label=GT(u'Breaks'), name=u'Breaks')
        
        self.categories = (
            rb_dep, rb_pre, rb_rec,
            rb_sug, rb_enh, rb_con,
            rb_rep, rb_break,
        )
        
        # Buttons to add and remove dependencies from the list
        self.depadd = ButtonAdd(self)
        self.depadd.SetName(u'add')
        self.depapp = ButtonAppend(self)
        self.depapp.SetName(u'append')
        self.deprem = ButtonRemove(self)
        self.deprem.SetName(u'remove')
        self.depclr = ButtonClear(self)
        self.depclr.SetName(u'clear')
        
        # ----- List
        self.dep_area = ListCtrlPanel(self, ident.F_LIST, style=wx.LC_REPORT, name=u'list')
        self.dep_area.InsertColumn(0, GT(u'Category'), width=150)
        self.dep_area.InsertColumn(1, GT(u'Package(s)'))
        
        # wx 3.0 compatibility
        if wx.MAJOR_VERSION < 3:
            self.dep_area.SetColumnWidth(100, wx.LIST_AUTOSIZE)
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        layout_G1 = wx.GridBagSizer()
        
        # Row 1
        layout_G1.Add(txt_package, pos=(0, 0), flag=wx.ALIGN_BOTTOM, border=0)
        layout_G1.Add(txt_version, pos=(0, 2), flag=wx.ALIGN_BOTTOM)
        
        # Row 2
        layout_G1.Add(self.input_package, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        layout_G1.Add(self.select_oper, pos=(1, 1))
        layout_G1.Add(self.input_version, pos=(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        layout_H1 = wx.BoxSizer(wx.HORIZONTAL)
        layout_H1.Add(layout_G1, 0, wx.ALIGN_BOTTOM)
        layout_H1.AddStretchSpacer(1)
        layout_H1.Add(btn_help)
        
        layout_categories = wx.GridSizer(4, 2, 5, 5)
        
        for C in self.categories:
            layout_categories.Add(C, 0)
        
        categories_panel.SetSizer(layout_categories)
        categories_panel.SetAutoLayout(True)
        categories_panel.Layout()
        
        layout_buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        layout_buttons.AddMany( (
            (self.depadd, 0, wx.ALIGN_CENTER_VERTICAL),
            (self.depapp, 0, wx.ALIGN_CENTER_VERTICAL),
            (self.deprem, 0, wx.ALIGN_CENTER_VERTICAL),
            (self.depclr, 0, wx.ALIGN_CENTER_VERTICAL),
            ) )
        
        layout_G2 = wx.GridBagSizer(5, 5)
        layout_G2.SetCols(2)
        
        layout_G2.Add(wx.StaticText(self, label=u'Categories'), (0, 0), (1, 1))
        layout_G2.Add(categories_panel, (1, 0), flag=wx.RIGHT, border=5)
        layout_G2.Add(layout_buttons, (1, 1), flag=wx.ALIGN_BOTTOM)
        
        layout_H3 = wx.BoxSizer(wx.HORIZONTAL)
        layout_H3.Add(self.dep_area, 1, wx.EXPAND)
        
        layout_main = wx.BoxSizer(wx.VERTICAL)
        layout_main.Add(layout_H1, 0, wx.EXPAND|wx.ALL, 5)
        layout_main.Add(layout_G2, 0, wx.ALL, 5)
        layout_main.Add(layout_H3, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_main)
        self.Layout()
        
        # *** Events *** #
        
        wx.EVT_KEY_DOWN(self.input_package, self.SetDepends)
        wx.EVT_KEY_DOWN(self.input_version, self.SetDepends)
        
        self.depadd.Bind(wx.EVT_BUTTON, self.SetDepends)
        self.depapp.Bind(wx.EVT_BUTTON, self.SetDepends)
        self.deprem.Bind(wx.EVT_BUTTON, self.SetDepends)
        self.depclr.Bind(wx.EVT_BUTTON, self.SetDepends)
        
        wx.EVT_KEY_DOWN(self.dep_area, self.SetDepends)
    
    
    ## TODO: Doxygen
    def GetDefaultCategory(self):
        return GT(u'Depends')
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, d_type, d_string):
        Logger.Debug(__name__, GT(u'Importing {}: {}'.format(d_type, d_string)))
        
        values = d_string.split(u', ')
        
        for V in values:
            self.dep_area.InsertStringItem(0, d_type)
            self.dep_area.SetStringItem(0, 1, V)
    
    
    ## Resets all fields on page to default values
    def ResetPageInfo(self):
        self.dep_area.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetDepends(self, event=None):
        try:
            key_id = event.GetKeyCode()
        
        except AttributeError:
            key_id = event.GetEventObject().GetId()
        
        addname = self.input_package.GetValue()
        oper = self.select_oper.GetStringSelection()
        ver = self.input_version.GetValue()
        addver = u'({}{})'.format(oper, ver)
            
        if key_id in (wx.ID_ADD, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
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
        
        elif key_id == ident.APPEND:
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
    def SetFieldDataLegacy(self, data):
        self.dep_area.DeleteAllItems()
        for item in data:
            item_count = len(item)
            while item_count > 1:
                item_count -= 1
                self.dep_area.InsertStringItem(0, item[0])
                self.dep_area.SetStringItem(0, 1, item[item_count])
