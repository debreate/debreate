# -*- coding: utf-8 -*-


import wx

from dbr.language       import GT
from globals            import ident
from globals.bitmaps    import BUTTON_REFRESH
from globals.paths      import PATH_app


## The same as wx.BitmapButton but defaults to style=wx.NO_BORDER
class BitmapButton(wx.BitmapButton):
    def __init__(self, parent, bitmap, ID=wx.ID_ANY, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
            name=wx.ButtonNameStr):
        
        if not isinstance(bitmap, wx.Bitmap):
            bitmap = wx.Bitmap(bitmap)
        
        wx.BitmapButton.__init__(self, parent, ID, bitmap, pos, size, style|wx.NO_BORDER,
                validator, name)


class ButtonAdd(BitmapButton):
    def __init__(self, parent, ID=wx.ID_ADD, name=u'btn add'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/add32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Add')))


class ButtonAppend(BitmapButton):
    def __init__(self, parent, ID=ident.APPEND, name=u'btn append'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/pipe32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Append')))


class ButtonBrowse(BitmapButton):
    def __init__(self, parent, ID=ident.BROWSE, name=u'btn browse'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/browse32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))


class ButtonBrowse64(BitmapButton):
    def __init__(self, parent, ID=ident.BROWSE, name=u'btn browse'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/browse64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))


class ButtonBuild(BitmapButton):
    def __init__(self, parent, ID=ident.BUILD, name=u'btn build'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/build32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Build')))


class ButtonBuild64(BitmapButton):
    def __init__(self, parent, ID=ident.BUILD, name=u'btn build'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/build64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Build')))


class ButtonCancel(BitmapButton):
    def __init__(self, parent, ID=wx.ID_CANCEL, name=u'btn cancel'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/cancel32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Cancel')))


class ButtonClear(BitmapButton):
    def __init__(self, parent, ID=wx.ID_CLEAR, name=u'btn clear'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/clear32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Clear')))


class ButtonConfirm(BitmapButton):
    def __init__(self, parent, ID=wx.ID_OK, name=u'btn confirm'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/confirm32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Confirm')))


class ButtonImport(BitmapButton):
    def __init__(self, parent, ID=wx.ID_OPEN, name=u'btn import'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/import32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Import')))


class ButtonNext(BitmapButton):
    def __init__(self, parent, ID=ident.NEXT, name=u'btn next'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/next32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Next')))


class ButtonPrev(BitmapButton):
    def __init__(self, parent, ID=ident.PREV, name=u'btn previous'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/prev32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Previous')))


class ButtonPreview(BitmapButton):
    def __init__(self, parent, ID=wx.ID_PREVIEW, name=u'btn preview'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/preview32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))


class ButtonPreview64(BitmapButton):
    def __init__(self, parent, ID=wx.ID_PREVIEW, name=u'btn preview'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/preview64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))


class ButtonQuestion64(BitmapButton):
    def __init__(self, parent, ID=wx.ID_HELP, name=u'btn help'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/question64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Help')))


## Button for refreshing displayed controls
class ButtonRefresh(BitmapButton):
    def __init__(self, parent, ID=wx.ID_REFRESH, name=u'refresh'):
        BitmapButton.__init__(self, parent, BUTTON_REFRESH,
                ID=ID, name=name)


class ButtonRemove(BitmapButton):
    def __init__(self, parent, ID=wx.ID_REMOVE, name=u'btn remove'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/del32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Remove')))


class ButtonSave(BitmapButton):
    def __init__(self, parent, ID=wx.ID_SAVE, name=u'btn save'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/save32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Save')))


class ButtonSave64(BitmapButton):
    def __init__(self, parent, ID=wx.ID_SAVE, name=u'btn save'):
        BitmapButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/save64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Save')))
