# -*- coding: utf-8 -*-

import wx, os

import dbr.application_path


# *** Buttons *** #

class ButtonAdd(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_RETURN):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/add32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Add')))

class ButtonBrowse(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/browse32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Browse')))

class ButtonBrowse64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/browse64.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Browse')))

class ButtonBuild(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/build32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Build')))

class ButtonBuild64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/build64.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Build')))

class ButtonCancel(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_CANCEL):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/cancel32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Cancel')))

class ButtonClear(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_ESCAPE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/clear32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Clear')))

class ButtonConfirm(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_OK):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/confirm32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Ok')))

class ButtonDel(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_DELETE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/del32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Remove')))

class ButtonImport(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/import32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Import')))

class ButtonNext(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/next32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Next')))

class ButtonPipe(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/pipe32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Append')))

class ButtonPrev(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/prev32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Previous')))

class ButtonPreview(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/preview32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Preview')))

class ButtonPreview64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/preview64.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Preview')))

class ButtonQuestion64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_HELP):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/question64.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Help')))

class ButtonSave(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/save32.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Save')))

class ButtonSave64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap('{}/bitmaps/save64.png'.format(dbr.application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Save')))