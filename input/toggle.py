# -*- coding: utf-8 -*-

## \package input.toggle

# MIT licensing
# See: docs/LICENSE.txt


import wx

from input.essential import EssentialField


## Standard wx.CheckBox
class CheckBox(wx.CheckBox):
    def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr):
        
        wx.CheckBox.__init__(self, parent, win_id, label, pos, size, style, name=name)


## CheckBox class that notifies main window to mark project dirty
class CheckBoxESS(CheckBox, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr):
        
        CheckBox.__init__(self, parent, win_id, label, pos, size, style, name=name)
        EssentialField.__init__(self)
