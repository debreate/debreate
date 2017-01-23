# -*- coding: utf-8 -*-

## \package ui.checklist

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from dbr.log            import Logger
from globals.strings    import TextIsEmpty
from ui.button          import ButtonCancel
from ui.button          import ButtonClear
from ui.button          import ButtonConfirm
from ui.layout          import BoxSizer


class CheckList(wx.Panel):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.TAB_TRAVERSAL, name=wx.PanelNameStr):
        wx.Panel.__init__(self, parent, ID, pos, size, style=style|wx.BORDER_THEME, name=name)
        
        self.SetBackgroundColour(u'white')
        
        self.scrolled_panel = wx.ScrolledWindow(self, style=wx.VSCROLL|wx.BORDER_NONE)
        self.scrolled_panel.SetBackgroundColour(self.GetBackgroundColour())
        self.scrolled_panel.SetScrollbars(20, 20, 50, 50)
        
        self.layout_scrolled = BoxSizer(wx.VERTICAL)
        
        self.scrolled_panel.SetSizer(self.layout_scrolled)
        self.scrolled_panel.SetAutoLayout(True)
        
        layout_main = BoxSizer(wx.VERTICAL)
        layout_main.Add(self.scrolled_panel, 1, wx.EXPAND)
        
        self.SetSizer(layout_main)
        self.SetAutoLayout(True)
        self.Layout()
    
    
    def AddItem(self, label, checked=False):
        # Yield for progress dialog pulse updates
        wx.Yield()
        
        # FIXME: Static lines are counted
        item_index = self.GetItemCount()
        
        #Logger.Debug(__name__, GT(u'Lintian tag: {}; Set checked: {}').format(label, checked))
        
        self.layout_scrolled.Add(wx.CheckBox(self.scrolled_panel, label=label), 1, wx.EXPAND)
        self.layout_scrolled.Add(wx.StaticLine(self.scrolled_panel, style=wx.LI_HORIZONTAL), 0, wx.EXPAND)
        
        if checked:
            check_box = self.GetItem(item_index)
            
            if isinstance(check_box, wx.CheckBox):
                check_box.SetValue(True)
        
        self.scrolled_panel.Layout()
        self.Layout()
    
    
    def AddItems(self, labels, checked=False):
        for l in labels:
            Logger.Debug(__name__, u'Adding item: {} (checked={})'.format(l, checked))
            
            self.AddItem(l, checked)
    
    
    def Clear(self):
        for C in self.scrolled_panel.GetChildren():
            if isinstance(C, wx.CheckBox) and C.GetValue():
                C.SetValue(False)
    
    
    def GetCheckedCount(self):
        checked_count = 0
        for C in self.scrolled_panel.GetChildren():
            if isinstance(C, wx.CheckBox) and C.GetValue():
                checked_count += 1
        
        return checked_count
    
    
    def GetCheckedLabels(self):
        checked_list = []
        
        for C in self.scrolled_panel.GetChildren():
            if isinstance(C, wx.CheckBox) and C.IsChecked():
                Logger.Debug(__name__, GT(u'Retrieving checked label: {}').format(C.GetLabel()))
                
                checked_list.append(C.GetLabel())
        
        return tuple(checked_list)
    
    
    def GetItem(self, index):
        return self.scrolled_panel.GetChildren()[index]
    
    
    def GetItemCount(self):
        if wx.MAJOR_VERSION > 2:
            return self.layout_scrolled.GetItemCount()
        
        return len(self.layout_scrolled.GetChildren())
    
    
    def LabelExists(self, label):
        for C in self.scrolled_panel.GetChildren():
            if isinstance(C, wx.CheckBox):
                if label == C.GetLabel():
                    return True
        
        return False
    
    
    def ScrollToEnd(self):
        self.scrolled_panel.SetScrollPos(wx.VERTICAL, self.scrolled_panel.GetScrollLines(wx.VERTICAL))
        self.scrolled_panel.Refresh()
        self.Refresh()
    
    
    ## TODO: Define & Doxygen
    def SetItemCheckedByLabel(self, label, checked=True):
        # FIXME: Should use a more efficient method to index & retrieve items
        for C in self.scrolled_panel.GetChildren():
            if isinstance(C, wx.CheckBox) and C.GetLabel() == label:
                C.SetValue(checked)
                
                break



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
        custom_label = unicode(self.input_add_custom.GetValue()).strip(u' ').replace(u' ', u'_')
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
