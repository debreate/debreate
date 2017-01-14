# -*- coding: utf-8 -*-

## \package wiz_bin.depends

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.buttons            import ButtonAdd
from dbr.buttons            import ButtonAppend
from dbr.buttons            import ButtonBrowse64
from dbr.buttons            import ButtonClear
from dbr.buttons            import ButtonPreview64
from dbr.buttons            import ButtonRemove
from dbr.buttons            import ButtonSave64
from dbr.help               import HelpButton
from dbr.language           import GT
from dbr.listinput          import ListCtrlPanel
from dbr.log                import Logger
from dbr.panel              import BorderedPanel
from dbr.wizard             import WizardPage
from globals                import ident
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetPage


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.DEPENDS)
        
        # Bypass checking this page for build
        self.prebuild_check = False
        
        # Buttons to open, save, & preview control file
        btn_open = ButtonBrowse64(self)
        btn_save = ButtonSave64(self)
        btn_preview = ButtonPreview64(self)
        
        txt_package = wx.StaticText(self, label=GT(u'Dependency/Conflict Package Name'), name=u'package')
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        
        self.ti_package = wx.TextCtrl(self, size=(300,25), name=u'package')
        
        opts_operator = (
            u'>=',
            u'<=',
            u'=',
            u'>>',
            u'<<',
            )
        
        self.sel_operator = wx.Choice(self, choices=opts_operator)
        self.sel_operator.default = 0
        self.sel_operator.SetSelection(self.sel_operator.default)
        
        self.ti_version = wx.TextCtrl(self, name=u'version')
        
        # Button to display help information about this page
        btn_help = HelpButton(self)
        
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
        btn_remove = ButtonRemove(self)
        btn_clear = ButtonClear(self)
        
        # ----- List
        self.lst_deps = ListCtrlPanel(self, ident.F_LIST, name=u'list')
        self.lst_deps.SetSingleStyle(wx.LC_REPORT)
        self.lst_deps.InsertColumn(0, GT(u'Category'), width=150)
        self.lst_deps.InsertColumn(1, GT(u'Package(s)'))
        
        # wx 3.0 compatibility
        if wx.MAJOR_VERSION < 3:
            self.lst_deps.SetColumnWidth(100, wx.LIST_AUTOSIZE)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        control_page = GetPage(ident.CONTROL)
        btn_open.Bind(wx.EVT_BUTTON, control_page.OnBrowse)
        btn_save.Bind(wx.EVT_BUTTON, control_page.OnSave)
        btn_preview.Bind(wx.EVT_BUTTON, control_page.OnPreviewControl)
        
        wx.EVT_KEY_DOWN(self.ti_package, self.SetDepends)
        wx.EVT_KEY_DOWN(self.ti_version, self.SetDepends)
        
        btn_add.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_append.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_remove.Bind(wx.EVT_BUTTON, self.SetDepends)
        btn_clear.Bind(wx.EVT_BUTTON, self.SetDepends)
        
        wx.EVT_KEY_DOWN(self.lst_deps, self.SetDepends)
        
        # *** Layout *** #
        
        lyt_top = wx.GridBagSizer()
        
        # Row 1
        lyt_top.Add(txt_package, pos=(0, 0), flag=wx.ALIGN_BOTTOM, border=0)
        lyt_top.Add(txt_version, pos=(0, 2), flag=wx.ALIGN_BOTTOM)
        lyt_top.Add(btn_open, (0, 3), (4, 1), wx.ALIGN_RIGHT)
        lyt_top.Add(btn_save, (0, 4), (4, 1))
        lyt_top.Add(btn_preview, (0, 5), (4, 1))
        
        # Row 2
        lyt_top.Add(self.ti_package, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        lyt_top.Add(self.sel_operator, pos=(1, 1))
        lyt_top.Add(self.ti_version, pos=(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        layout_H1 = wx.BoxSizer(wx.HORIZONTAL)
        layout_H1.Add(lyt_top, 0, wx.ALIGN_BOTTOM)
        layout_H1.AddStretchSpacer(1)
        layout_H1.Add(btn_help)
        
        layout_categories = wx.GridSizer(4, 2, 5, 5)
        
        for C in self.categories:
            layout_categories.Add(C, 0)
        
        pnl_categories.SetSizer(layout_categories)
        pnl_categories.SetAutoLayout(True)
        pnl_categories.Layout()
        
        layout_buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        layout_buttons.AddMany( (
            (btn_add, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_append, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_remove, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_clear, 0, wx.ALIGN_CENTER_VERTICAL),
            ) )
        
        layout_G2 = wx.GridBagSizer(5, 5)
        layout_G2.SetCols(2)
        
        layout_G2.Add(wx.StaticText(self, label=u'Categories'), (0, 0), (1, 1))
        layout_G2.Add(pnl_categories, (1, 0), flag=wx.RIGHT, border=5)
        layout_G2.Add(layout_buttons, (1, 1), flag=wx.ALIGN_BOTTOM)
        
        layout_H3 = wx.BoxSizer(wx.HORIZONTAL)
        layout_H3.Add(self.lst_deps, 1, wx.EXPAND)
        
        layout_main = wx.BoxSizer(wx.VERTICAL)
        layout_main.Add(layout_H1, 0, wx.EXPAND|wx.ALL, 5)
        layout_main.Add(layout_G2, 0, wx.ALL, 5)
        layout_main.Add(layout_H3, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_main)
        self.Layout()
    
    
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
        return GT(u'Depends')
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, d_type, d_string):
        Logger.Debug(__name__, GT(u'Importing {}: {}'.format(d_type, d_string)))
        
        values = d_string.split(u', ')
        
        for V in values:
            self.lst_deps.InsertStringItem(0, d_type)
            self.lst_deps.SetStringItem(0, 1, V)
    
    
    ## Resets all fields on page to default values
    def ResetPage(self):
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
            selected_count = self.lst_deps.GetSelectedItemCount()
            if not TextIsEmpty(addname) and self.lst_deps.GetItemCount() and selected_count:
                listrow = None
                for X in range(selected_count):
                    if listrow == None:
                        listrow = self.lst_deps.GetFirstSelected()
                    
                    else:
                        listrow = self.lst_deps.GetNextSelected(listrow)
                    
                    colitem = self.lst_deps.GetItem(listrow, 1)  # Get item from second column
                    prev_text = colitem.GetText()  # Get the text from that item
                    
                    if not TextIsEmpty(ver):
                        self.lst_deps.SetStringItem(listrow, 1, u'{} | {} {}'.format(prev_text, addname, addver))
                    
                    else:
                        self.lst_deps.SetStringItem(listrow, 1, u'{} | {}'.format(prev_text, addname))
        
        elif key_id == wx.ID_REMOVE:
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
    def SetFieldDataLegacy(self, data):
        self.lst_deps.DeleteAllItems()
        for item in data:
            item_count = len(item)
            while item_count > 1:
                item_count -= 1
                self.lst_deps.InsertStringItem(0, item[0])
                self.lst_deps.SetStringItem(0, 1, item[item_count])
