# -*- coding: utf-8 -*-

import wx

import dbr


# Buttons
ButtonAdd = dbr.ButtonAdd
ButtonBrowse = dbr.ButtonBrowse
ButtonBrowse64 = dbr.ButtonBrowse64
ButtonBuild = dbr.ButtonBuild
ButtonBuild64 = dbr.ButtonBuild64
ButtonCancel = dbr.ButtonCancel
ButtonClear = dbr.ButtonClear
ButtonConfirm = dbr.ButtonConfirm
ButtonDel = dbr.ButtonDel
ButtonImport = dbr.ButtonImport
ButtonPipe = dbr.ButtonPipe
ButtonPreview = dbr.ButtonPreview
ButtonPreview64 = dbr.ButtonPreview64
ButtonQuestion64 = dbr.ButtonQuestion64
ButtonSave = dbr.ButtonSave
ButtonSave64 = dbr.ButtonSave64


# Wizard
Wizard = dbr.Wizard

# Message Dialog
class MessageDialog(dbr.MessageDialog):
    def __init__(self, parent, id=wx.ID_ANY, title="Message", icon=dbr.ICON_ERROR, text=wx.EmptyString,
            details=wx.EmptyString):
        dbr.MessageDialog.__init__(self, parent, id, title, icon, text, details)

# Path text controls
PathCtrl = dbr.PathCtrl
PATH_DEFAULT = dbr.PATH_DEFAULT
PATH_WARN = dbr.PATH_WARN

# Character controls
CharCtrl = dbr.CharCtrl
