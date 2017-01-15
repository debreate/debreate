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
from dbr.dialogs            import ConfirmationDialog
from dbr.language           import GT
from dbr.listinput          import ListCtrlPanel
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from dbr.panel              import BorderedPanel
from dbr.wizard             import WizardPage
from globals                import ident
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetPage
from globals.wizardhelper   import GetTopWindow


## Page defining dependencies
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
        
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        
        lyt_top = wx.GridBagSizer()
        lyt_top.SetCols(6)
        lyt_top.AddGrowableCol(3)
        
        # Row 1
        lyt_top.Add(txt_package, (1, 0), flag=LEFT_BOTTOM)
        lyt_top.Add(txt_version, (1, 2), flag=LEFT_BOTTOM)
        lyt_top.Add(btn_open, (0, 3), (4, 1), wx.ALIGN_RIGHT)
        lyt_top.Add(btn_save, (0, 4), (4, 1))
        lyt_top.Add(btn_preview, (0, 5), (4, 1))
        
        # Row 2
        lyt_top.Add(self.ti_package, (2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        lyt_top.Add(self.sel_operator, (2, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        lyt_top.Add(self.ti_version, (2, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        lyt_categories = wx.GridSizer(4, 2, 5, 5)
        
        for C in self.categories:
            lyt_categories.Add(C, 0)
        
        pnl_categories.SetAutoLayout(True)
        pnl_categories.SetSizer(lyt_categories)
        pnl_categories.Layout()
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        lyt_buttons.AddMany((
            (btn_add, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_append, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_remove, 0, wx.ALIGN_CENTER_VERTICAL),
            (btn_clear, 0, wx.ALIGN_CENTER_VERTICAL),
            ))
        
        lyt_mid = wx.GridBagSizer()
        lyt_mid.SetCols(2)
        
        lyt_mid.Add(wx.StaticText(self, label=u'Categories'), (0, 0), (1, 1), LEFT_BOTTOM)
        lyt_mid.Add(pnl_categories, (1, 0), flag=wx.RIGHT, border=5)
        lyt_mid.Add(lyt_buttons, (1, 1), flag=wx.ALIGN_BOTTOM)
        
        lyt_list = wx.BoxSizer(wx.HORIZONTAL)
        lyt_list.Add(self.lst_deps, 1, wx.EXPAND)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        # Spacer is less on this page because text is aligned to bottom
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_top, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(lyt_mid, 0, wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(lyt_list, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
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
        return self.default_category
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, d_type, d_string):
        Logger.Debug(__name__, GT(u'Importing {}: {}'.format(d_type, d_string)))
        
        values = d_string.split(u', ')
        
        for V in values:
            self.lst_deps.InsertStringItem(0, d_type)
            self.lst_deps.SetStringItem(0, 1, V)
    
    
    ## Resets all fields on page to default values
    def ResetPage(self):
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
            
            Logger.Debug(__name__, u'Appending to {} items'.format(selected_count))
            
            if not TextIsEmpty(addname) and self.lst_deps.GetItemCount() and selected_count:
                selected_rows = self.lst_deps.GetSelectedIndexes()
                
                if DebugEnabled():
                    Logger.Debug(__name__, u'Selected rows:')
                    for R in selected_rows:
                        print(u'\t{}'.format(R))
                
                for listrow in selected_rows:
                    Logger.Debug(__name__, u'Setting list row: {}'.format(listrow))
                    
                    # Get item from second column
                    colitem = self.lst_deps.GetItem(listrow, 1)
                    # Get the text from that item
                    prev_text = colitem.GetText()
                    
                    if not TextIsEmpty(ver):
                        new_text = u'{} | {} {}'.format(prev_text, addname, addver)
                    
                    else:
                        new_text = u'{} | {}'.format(prev_text, addname)
                    
                    Logger.Debug(__name__, u'Appended item: {}'.format(new_text))
                    
                    self.lst_deps.SetStringItem(listrow, 1, new_text)
        
        elif key_id in (wx.ID_REMOVE, wx.WXK_DELETE):
            self.lst_deps.RemoveSelected()
        
        elif key_id == wx.ID_CLEAR:
            if self.lst_deps.GetItemCount():
                if ConfirmationDialog(GetTopWindow(), GT(u'Confirm'),
                        GT(u'Clear all dependencies?')).ShowModal() in (wx.ID_OK, wx.OK):
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
