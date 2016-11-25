# -*- coding: utf-8 -*-

## \package dbr.buttons
#  
#  Custom buttons for application


import wx

from dbr.language       import GT
from globals.bitmaps    import BUTTON_REFRESH
from globals.ident      import ID_APPEND
from globals.ident      import ID_BUILD
from globals.ident      import ID_IMPORT
from globals.ident      import ID_NEXT
from globals.ident      import ID_PREV
from globals.paths      import PATH_app


class ToolTipButton(wx.BitmapButton):
    def __init__(self, parent, ID=wx.ID_ANY,
                bitmap=u'{}/bitmaps/debreate64.png'.format(PATH_app), tooltip=wx.EmptyString):
        
        if isinstance(bitmap, (unicode, str)):
            bitmap = wx.Bitmap(bitmap)
        
        wx.BitmapButton.__init__(self, parent, ID, bitmap, style=wx.NO_BORDER)
        
        if tooltip:
            if isinstance(tooltip, (unicode, str)):
                tooltip = wx.ToolTip(tooltip)
            
            self.SetToolTip(tooltip)


## The same as wx.BitmapButton but defaults to style=wx.NO_BORDER
class BitmapButton(wx.BitmapButton):
    def __init__(self, parent, bitmap, ID=wx.ID_ANY, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
            name=wx.ButtonNameStr):
        
        if not isinstance(bitmap, wx.Bitmap):
            bitmap = wx.Bitmap(bitmap)
        
        wx.BitmapButton.__init__(self, parent, ID, bitmap, pos, size, style|wx.NO_BORDER,
                validator, name)


class ButtonAdd(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Add')):
        ToolTipButton.__init__(self, parent, wx.WXK_RETURN,
                u'{}/bitmaps/add32.png'.format(PATH_app), tooltip)

class ButtonAppend(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Append')):
        ToolTipButton.__init__(self, parent, ID_APPEND,
                u'{}/bitmaps/pipe32.png'.format(PATH_app), tooltip)

class ButtonBrowse(ToolTipButton):
    def __init__(self, parent, ID=wx.ID_OPEN, tooltip=GT(u'Browse')):
        ToolTipButton.__init__(self, parent, ID,
                u'{}/bitmaps/browse32.png'.format(PATH_app), tooltip)

class ButtonBrowse64(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Browse')):
        ToolTipButton.__init__(self, parent, wx.ID_OPEN,
                u'{}/bitmaps/browse64.png'.format(PATH_app), tooltip)

class ButtonBuild(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Build')):
        ToolTipButton.__init__(self, parent, ID_BUILD,
                u'{}/bitmaps/build32.png'.format(PATH_app), tooltip)

class ButtonBuild64(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Build')):
        ToolTipButton.__init__(self, parent, ID_BUILD,
                u'{}/bitmaps/build64.png'.format(PATH_app), tooltip)

class ButtonCancel(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Cancel')):
        ToolTipButton.__init__(self, parent, wx.ID_CANCEL,
                u'{}/bitmaps/cancel32.png'.format(PATH_app), tooltip)

class ButtonClear(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Clear')):
        ToolTipButton.__init__(self, parent, wx.ID_CLEAR,
                u'{}/bitmaps/clear32.png'.format(PATH_app), tooltip)

class ButtonConfirm(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Ok')):
        ToolTipButton.__init__(self, parent, wx.ID_OK,
                u'{}/bitmaps/confirm32.png'.format(PATH_app), tooltip)

class ButtonDel(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Remove')):
        ToolTipButton.__init__(self, parent, wx.ID_DELETE,
                u'{}/bitmaps/del32.png'.format(PATH_app), tooltip)

class ButtonImport(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Import')):
        ToolTipButton.__init__(self, parent, ID_IMPORT,
                u'{}/bitmaps/import32.png'.format(PATH_app), tooltip)

class ButtonNext(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Next')):
        ToolTipButton.__init__(self, parent, ID_NEXT,
                u'{}/bitmaps/next32.png'.format(PATH_app), tooltip)

class ButtonPrev(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Previous')):
        ToolTipButton.__init__(self, parent, ID_PREV,
                u'{}/bitmaps/prev32.png'.format(PATH_app), tooltip)

class ButtonPreview(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Preview')):
        ToolTipButton.__init__(self, parent, wx.ID_PREVIEW,
                u'{}/bitmaps/preview32.png'.format(PATH_app), tooltip)

class ButtonPreview64(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Preview')):
        ToolTipButton.__init__(self, parent, wx.ID_PREVIEW,
                u'{}/bitmaps/preview64.png'.format(PATH_app), tooltip)

class ButtonQuestion64(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Help')):
        ToolTipButton.__init__(self, parent, wx.ID_HELP,
                u'{}/bitmaps/question64.png'.format(PATH_app), tooltip)

## Button for refreshing displayed controls
class ButtonRefresh(BitmapButton):
    def __init__(self, parent, name=u'refresh'):
        BitmapButton.__init__(self, parent, BUTTON_REFRESH, wx.ID_REFRESH, name=name)


class ButtonSave(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Save')):
        wx.BitmapButton.__init__(self, parent, wx.ID_SAVE, wx.Bitmap(u'{}/bitmaps/save32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(tooltip))

class ButtonSave64(ToolTipButton):
    def __init__(self, parent, tooltip=GT(u'Save')):
        ToolTipButton.__init__(self, parent, wx.ID_SAVE,
                u'{}/bitmaps/save64.png'.format(PATH_app), tooltip)
