# -*- coding: utf-8 -*-

## \package dbr.buttons
#  
#  Custom buttons for application


from wx import ID_ANY
from wx import ID_CANCEL
from wx import ID_HELP
from wx import ID_OK
from wx import ID_OPEN
from wx import ID_REFRESH
from wx import ID_SAVE
from wx import WXK_DELETE
from wx import WXK_ESCAPE
from wx import WXK_RETURN
import wx

from dbr.language   import GT
from dbr.log        import Logger
from globals.ident  import ID_APPEND
from globals.ident  import ID_BUILD
from globals.ident  import ID_NEXT
from globals.ident  import ID_PREV
from globals.paths  import PATH_app


class ImageButton(wx.BitmapButton):
    def __init__(self, parent, ID=wx.ID_ANY,
                bitmap=u'{}/bitmaps/debreate64.png'.format(PATH_app)):
        
        if isinstance(bitmap, (unicode, str)):
            bitmap = wx.Bitmap(bitmap)
        
        wx.BitmapButton.__init__(self, parent, ID, bitmap, style=wx.NO_BORDER)


class ToolTipButton(ImageButton):
    def __init__(self, parent, ID=wx.ID_ANY,
                bitmap=u'{}/bitmaps/debreate64.png'.format(PATH_app), tooltip=wx.EmptyString):
        ImageButton.__init__(self, parent, ID, bitmap)
        
        if tooltip:
            
            if isinstance(tooltip, (unicode, str)):
                tooltip = wx.ToolTip(tooltip)
            
            self.SetToolTip(tooltip)
        
        Logger.Debug(__name__, GT(u'ToolTip type: {}').format(type(tooltip)))
        


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

class ButtonBuild64(ToolTipButton):
    def __init__(self, parent, ID=ID_BUILD,
                bitmap=wx.Bitmap(u'{}/bitmaps/build64.png'.format(PATH_app)), tooltip=GT(u'Build')):
        ToolTipButton.__init__(self, parent, ID, bitmap, tooltip)

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

## Button for refreshing displayed controls
#  
#  TODO: Use wx.BitmapButton
class ButtonRefresh(wx.Button):
    def __init__(self, parent, ID=ID_REFRESH, tooltip=wx.EmptyString):
        wx.Button.__init__(self, parent, ID)
        
        self.SetToolTip(tooltip)


class ButtonSave(wx.BitmapButton):
    def __init__(self, parent, ID=ID_SAVE, tooltip=GT(u'Save')):
        wx.BitmapButton.__init__(self, parent, ID, wx.Bitmap(u'{}/bitmaps/save32.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(tooltip))

class ButtonSave64(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, ID_SAVE, wx.Bitmap(u'{}/bitmaps/save64.png'.format(PATH_app)),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(GT(u'Save')))