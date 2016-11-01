# -*- coding: utf-8 -*-

import wx

from globals.paths import PATH_app


# *** Buttons *** #
class ButtonAdd(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_RETURN):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/add32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Add')))

class ButtonBrowse(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/browse32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Browse')))

class ButtonBrowse64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/browse64.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Browse')))

class ButtonBuild(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/build32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Build')))

class ButtonBuild64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/build64.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Build')))

class ButtonCancel(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_CANCEL):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/cancel32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Cancel')))

class ButtonClear(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_ESCAPE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/clear32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Clear')))

class ButtonConfirm(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_OK):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/confirm32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Ok')))

class ButtonDel(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_DELETE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/del32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Remove')))

class ButtonImport(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/import32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Import')))

class ButtonNext(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/next32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Next')))

class ButtonPipe(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/pipe32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Append')))

class ButtonPrev(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/prev32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Previous')))

class ButtonPreview(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/preview32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Preview')))

class ButtonPreview64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/preview64.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Preview')))

class ButtonQuestion64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_HELP):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/question64.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Help')))

class ButtonSave(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/save32.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Save')))

class ButtonSave64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/save64.png" % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Save')))