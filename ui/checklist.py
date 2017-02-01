# -*- coding: utf-8 -*-

## \package ui.checklist

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language           import GT
from dbr.log                import Logger
from globals.ident          import genid
from globals.strings        import GS
from globals.strings        import TextIsEmpty
from globals.wizardhelper   import GetField
from ui.button              import ButtonCancel
from ui.button              import ButtonClear
from ui.button              import ButtonConfirm
from ui.layout              import BoxSizer
from ui.panel               import BorderedPanel
from ui.panel               import ScrolledPanel


## A checkable list
class CheckList(BorderedPanel):
    def __init__(self, parent, ID=wx.ID_ANY, items=[], pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.VSCROLL, name=wx.PanelNameStr):
        
        BorderedPanel.__init__(self, parent, ID, pos, size, name=name)
        
        self.SetBackgroundColour(u'white')
        
        pnl_bg = ScrolledPanel(self, genid.BGPANEL, style=style|wx.TAB_TRAVERSAL|wx.BORDER_NONE)
        pnl_bg.SetBackgroundColour(self.GetBackgroundColour())
        pnl_bg.SetScrollbars(20, 20, 50, 50)
        
        # *** Event Handling *** #
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckItem)
        
        # *** Layout *** #
        
        lyt_bg = BoxSizer(wx.VERTICAL)
        
        pnl_bg.SetSizer(lyt_bg)
        pnl_bg.SetAutoLayout(True)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(pnl_bg, 1, wx.EXPAND)
        
        self.SetSizer(lyt_main)
        self.SetAutoLayout(True)
        self.Layout()
        
        # *** Post-Layout Actions *** #
        
        if items:
            self.AddItems(items)
    
    
    ## Add a single item to the list
    #
    #  \param label
    #    Item's displayed text
    #  \param checked
    #    Sets item checked if True
    def AddItem(self, label, checked=False):
        # Yield for progress dialog pulse updates
        wx.Yield()
        
        # FIXME: Static lines are counted
        item_index = self.GetItemCount()
        
        #Logger.Debug(__name__, GT(u'Lintian tag: {}; Set checked: {}').format(label, checked))
        
        pnl_bg = GetField(self, genid.BGPANEL)
        lyt_bg = pnl_bg.GetSizer()
        
        lyt_bg.Add(wx.CheckBox(pnl_bg, label=label), 1, wx.EXPAND)
        lyt_bg.Add(wx.StaticLine(pnl_bg, style=wx.LI_HORIZONTAL), 0, wx.EXPAND)
        
        if checked:
            check_box = self.GetItem(item_index)
            
            if isinstance(check_box, wx.CheckBox):
                check_box.SetValue(True)
        
        pnl_bg.Layout()
        self.Layout()
    
    
    ## Adds multiple items to the list
    #
    #  \param labels
    #    List of text labels to be displayed
    #  \param checked
    #    Sets items as checked if True
    def AddItems(self, labels, checked=False):
        for l in labels:
            Logger.Debug(__name__, u'Adding item: {} (checked={})'.format(l, checked))
            
            self.AddItem(l, checked)
    
    
    ## Sets all item states to 'unchecked'
    def Clear(self):
        changed = False
        
        for CHK in self.GetAllItems():
            if CHK.GetValue():
                CHK.SetValue(False)
                changed = True
        
        if changed:
            self.PostCheckBoxEvent()
    
    
    ## Retrieves all check boxes
    #
    #  \return
    #    Tuple containing all children check box instances
    def GetAllItems(self):
        pnl_bg = GetField(self, genid.BGPANEL)
        items = []
        
        for item in pnl_bg.GetChildren():
            if isinstance(item, wx.CheckBox):
                items.append(item)
        
        return tuple(items)
    
    
    ## Retrieves all item labels
    #
    #  \return
    #    Tuple of all check box labels
    def GetAllLabels(self):
        labels = []
        
        for CHK in self.GetAllItems():
            labels.append(CHK.GetLabel())
        
        return tuple(labels)
    
    
    ## Retrieves number of items in list that set as 'checked'
    def GetCheckedCount(self):
        checked_count = 0
        for CHK in self.GetAllItems():
            if CHK.GetValue():
                checked_count += 1
        
        return checked_count
    
    
    ## Retrieves list of items that are set as 'checked'
    def GetCheckedLabels(self):
        checked_list = []
        
        for CHK in self.GetAllItems():
            if CHK.IsChecked():
                label = CHK.GetLabel()
                
                Logger.Debug(__name__, GT(u'Retrieving checked label: {}').format(label))
                
                checked_list.append(label)
        
        return tuple(checked_list)
    
    
    ## Retrieves a single item
    #
    #  \param index
    #    Retrieve item at index
    #  \return
    #    True if label is found
    def GetItem(self, index):
        return self.GetAllItems()[index]
    
    
    ## Retrieves an item using a label
    #
    #  \param label
    #    Text label to search for
    def GetItemByLabel(self, label):
        labels = self.GetAllLabels()
        
        if label in labels:
            return self.GetItem(labels.index(label))
    
    
    ## Retrieves number of items in list
    def GetItemCount(self):
        return len(self.GetAllItems())
    
    
    ## Retrieves the checked state of an item
    #
    #  \param index
    #    \b \e Integer index of of item to check
    def GetValue(self, index):
        return self.GetItem(index).GetValue()
    
    
    ## Retrieves the checked state of an item
    #
    #  \param label
    #    Label whose value to get
    #  \return
    #    \b \e True if label's state is 'checked'
    def GetValueByLabel(self, label):
        item = self.GetItemByLabel(label)
        
        if item:
            return item.GetValue()
        
        return False
    
    
    ## Checks if any item's state is 'checked'
    #
    #  \return
    #    \b \e True if any item's state is 'checked'
    def HasSelected(self):
        for CHK in self.GetAllItems():
            if CHK.GetValue():
                return True
        
        return False
    
    
    ## Check if an item's state is 'checked'
    #
    #  \param label
    #    Label of item to check
    def IsSelected(self, label):
        return label in self.GetCheckedLabels()
    
    
    ## Checks if a label is in the list
    #
    #  \param label
    #    Text label to search for
    def LabelExists(self, label):
        for LABEL in self.GetAllLabels():
            if LABEL == label:
                return True
        
        return False
    
    
    ## Handles check box events
    def OnCheckItem(self, event=None):
        self.PostCheckBoxEvent()
    
    
    ## Propagates check box event to parent or target
    #
    #  \param target
    #    \b \e wx.Window instance to post event to
    def PostCheckBoxEvent(self, target=None):
        if not target:
            target = self.Parent
        
        wx.PostEvent(target, wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, self.Id))
    
    
    ## TODO: Doxygen
    def ScrollToEnd(self):
        pnl_bg = GetField(self, genid.BGPANEL)
        
        pnl_bg.SetScrollPos(wx.VERTICAL, pnl_bg.GetScrollLines(wx.VERTICAL))
        
        pnl_bg.Refresh()
        self.Refresh()
    
    
    ## TODO: Define & Doxygen
    def SetItemCheckedByLabel(self, label, checked=True):
        # FIXME: Should use a more efficient method to index & retrieve items
        for C in self.GetAllItems():
            if C.GetLabel() == label:
                C.SetValue(checked)
                
                break
    
    
    ## Sets the 'checked' state of an item
    #
    #  \param index
    #    \b \e Integer index of item to manipulate
    #  \param checked
    #    State to set item
    def SetValue(self, index, checked):
        return self.GetItem(index).SetValue(checked)


## TODO: Doxygen
class CheckListDialog(wx.Dialog):
    def __init__(self, parent, ID=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr,
            allow_custom=False):
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style=style|wx.RESIZE_BORDER,
                name=name)
        
        self.check_list = CheckList(self)
        
        # *** Buttons *** #
        
        layout_buttons = BoxSizer(wx.HORIZONTAL)
        
        btn_clear = ButtonClear(self)
        btn_confirm = ButtonConfirm(self)
        btn_cancel = ButtonCancel(self)
        
        btn_clear.Bind(wx.EVT_BUTTON, self.OnClearList)
        
        # FIXME: Correct button order?
        layout_buttons.Add(btn_clear, 0, wx.LEFT, 5)
        layout_buttons.AddStretchSpacer(1)
        layout_buttons.Add(btn_confirm, 0, wx.RIGHT, 5)
        layout_buttons.Add(btn_cancel, 0, wx.RIGHT, 5)
        
        # *** Layout *** #
        
        layout_main = BoxSizer(wx.VERTICAL)
        
        layout_main.Add(self.check_list, 1, wx.EXPAND|wx.ALL, 5)
        layout_main.Add(layout_buttons, 0, wx.EXPAND|wx.BOTTOM, 5)
        
        if allow_custom:
            btn_add_custom = wx.Button(self, label=GT(u'Add custom'))
            btn_add_custom.Bind(wx.EVT_BUTTON, self.OnAddCustom)
            
            self.input_add_custom = wx.TextCtrl(self)
            
            layout_add_custom = BoxSizer(wx.HORIZONTAL)
            layout_add_custom.Add(btn_add_custom, 0, wx.LEFT|wx.RIGHT, 5)
            layout_add_custom.Add(self.input_add_custom, 1, wx.RIGHT, 5)
            
            layout_main.Insert(1, layout_add_custom, 0, wx.EXPAND)
        
        self.SetSizer(layout_main)
        self.SetAutoLayout(True)
        self.Layout()
        
        self.CenterOnParent()
    
    
    def AddItem(self, label, checked=False):
        self.check_list.AddItem(label, checked)
    
    
    def GetCheckedCount(self):
        return self.check_list.GetCheckedCount()
    
    
    def GetCheckedLabels(self):
        return self.check_list.GetCheckedLabels()
    
    
    def InitCheckList(self, labels, checked=False):
        self.check_list.AddItems(labels, checked)
    
    
    def OnAddCustom(self, event=None):
        custom_label = GS(self.input_add_custom.GetValue()).strip(u' ').replace(u' ', u'_')
        if not TextIsEmpty(custom_label) and not self.check_list.LabelExists(custom_label):
            self.check_list.AddItem(custom_label, True)
            self.check_list.ScrollToEnd()
    
    
    def OnClearList(self, event=None):
        if self.GetCheckedCount():
            warn_dialog = wx.MessageDialog(self, GT(u'Clear Lintian overrides list?'), GT(u'Warning'),
                    style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING)
            warn_dialog.CenterOnParent()
            
            if warn_dialog.ShowModal() == wx.ID_YES:
                self.check_list.Clear()
    
    
    def SetItemCheckedByLabel(self, label, checked=True):
        self.check_list.SetItemCheckedByLabel(label, checked)
    
    
    ## TODO: Doxygen
    def ShowModal(self):
        # wx 2.8 doesn't automatically center on parent
        if self.Parent:
            self.CenterOnParent()
        
        return wx.Dialog.ShowModal(self)
