# -*- coding: utf-8 -*-

## \package dbr.buttons
#  
#  Custom buttons for application

import wx, os

from dbr.constants import application_path


# *** Buttons *** #

class ButtonAdd(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_RETURN):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/add32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Add')))

class ButtonBrowse(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/browse32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Browse')))

class ButtonBrowse64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/browse64.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Browse')))

class ButtonBuild(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/build32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Build')))

class ButtonBuild64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/build64.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Build')))

class ButtonCancel(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_CANCEL):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/cancel32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Cancel')))

class ButtonClear(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_ESCAPE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/clear32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Clear')))

class ButtonConfirm(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_OK):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/confirm32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Ok')))

class ButtonDel(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_DELETE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/del32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Remove')))

class ButtonImport(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/import32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Import')))

class ButtonNext(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/next32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Next')))

class ButtonPipe(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/pipe32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Append')))

class ButtonPrev(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/prev32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Previous')))

class ButtonPreview(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/preview32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Preview')))

class ButtonPreview64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/preview64.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Preview')))

class ButtonQuestion64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_HELP):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/question64.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Help')))

class ButtonSave(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/save32.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Save')))

class ButtonSave64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap(u'{}/bitmaps/save64.png'.format(application_path)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_(u'Save')))