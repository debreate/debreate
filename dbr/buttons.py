# -*- coding: utf-8 -*-

## \package dbr.buttons
#  
#  Custom buttons for application


import wx
from wx import ID_ANY, ID_OPEN
from wx import ID_CANCEL
from wx import ID_HELP
from wx import ID_OK
from wx import ID_SAVE
from wx import WXK_DELETE
from wx import WXK_ESCAPE
from wx import WXK_RETURN

from dbr.language   import GT
from globals.paths  import PATH_app
from globals.ident  import ID_PREV, ID_APPEND, ID_BUILD
from globals.ident  import ID_NEXT


# *** Buttons *** #
class ButtonAdd(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, WXK_RETURN, wx.Bitmap(u'{}/bitmaps/add32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Add')))

class ButtonBrowse(wx.BitmapButton):
    def __init__(self, parent, ID=ID_OPEN):
        wx.BitmapButton.__init__(self, parent, ID, wx.Bitmap(u'{}/bitmaps/browse32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))

class ButtonBrowse64(wx.BitmapButton):
    def __init__(self, parent, ID=ID_OPEN):
        wx.BitmapButton.__init__(self, parent, ID, wx.Bitmap(u'{}/bitmaps/browse64.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))

class ButtonBuild(wx.BitmapButton):
    def __init__(self, parent, ID=ID_BUILD):
        wx.BitmapButton.__init__(self, parent, ID, wx.Bitmap(u'{}/bitmaps/build32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Build')))

class ButtonBuild64(wx.BitmapButton):
    def __init__(self, parent, ID=ID_BUILD):
        wx.BitmapButton.__init__(self, parent, ID, wx.Bitmap(u'{}/bitmaps/build64.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Build')))

class ButtonCancel(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_CANCEL, wx.Bitmap(u'{}/bitmaps/cancel32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Cancel')))

class ButtonClear(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, WXK_ESCAPE, wx.Bitmap(u'{}/bitmaps/clear32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Clear')))

class ButtonConfirm(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_OK, wx.Bitmap(u'{}/bitmaps/confirm32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Ok')))

class ButtonDel(wx.BitmapButton):
    def __init__(self, parent, ID=WXK_DELETE):
        wx.BitmapButton.__init__(self, parent, ID, wx.Bitmap(u'{}/bitmaps/del32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Remove')))

class ButtonImport(wx.BitmapButton):
    def __init__(self, parent, ID=ID_ANY):
        wx.BitmapButton.__init__(self, parent, ID, wx.Bitmap(u'{}/bitmaps/import32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Import')))

class ButtonNext(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_NEXT, wx.Bitmap(u'{}/bitmaps/next32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Next')))

class ButtonPipe(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_APPEND, wx.Bitmap(u'{}/bitmaps/pipe32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Append')))

class ButtonPrev(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_PREV, wx.Bitmap(u'{}/bitmaps/prev32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Previous')))

class ButtonPreview(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_ANY, wx.Bitmap(u'{}/bitmaps/preview32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))

class ButtonPreview64(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_ANY, wx.Bitmap(u'{}/bitmaps/preview64.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))

class ButtonQuestion64(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_HELP, wx.Bitmap(u'{}/bitmaps/question64.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Help')))

class ButtonSave(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_SAVE, wx.Bitmap(u'{}/bitmaps/save32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Save')))

class ButtonSave64(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_SAVE, wx.Bitmap(u'{}/bitmaps/save64.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Save')))