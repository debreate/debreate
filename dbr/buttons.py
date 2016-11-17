# -*- coding: utf-8 -*-


import wx

from dbr.language   import GT
from globals.paths  import PATH_app


# *** Buttons *** #
class ButtonAdd(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_RETURN):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/add32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Add')))

class ButtonBrowse(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/browse32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))

class ButtonBrowse64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/browse64.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))

class ButtonBuild(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/build32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Build')))

class ButtonBuild64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/build64.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Build')))

class ButtonCancel(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_CANCEL):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/cancel32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Cancel')))

class ButtonClear(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_CLEAR):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/clear32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Clear')))

class ButtonConfirm(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_OK):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/confirm32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Ok')))

class ButtonDel(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_DELETE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/del32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Remove')))

class ButtonImport(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/import32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Import')))

class ButtonNext(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/next32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Next')))

class ButtonPipe(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/pipe32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Append')))

class ButtonPrev(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/prev32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Previous')))

class ButtonPreview(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/preview32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))

class ButtonPreview64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/preview64.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))

class ButtonQuestion64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_HELP):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/question64.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Help')))

class ButtonSave(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/save32.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Save')))

class ButtonSave64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'%s/bitmaps/save64.png' % PATH_app),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Save')))