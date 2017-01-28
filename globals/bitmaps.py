# -*- coding: utf-8 -*-

## \package globals.bitmaps

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.image      import GetBitmap
from globals.paths  import ConcatPaths
from globals.paths  import PATH_bitmaps


LOGO = ConcatPaths((PATH_bitmaps, u'debreate64.png'))

ICON_ERROR = GetBitmap(u'error', 64, u'icon')
ICON_EXCLAMATION = ICON_ERROR
ICON_QUESTION = GetBitmap(u'question', 64, u'icon')
ICON_INFORMATION = GetBitmap(u'info', 64, u'icon')
ICON_WARNING = GetBitmap(u'warn', 64, u'icon')

ICON_CLOCK = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'clock16.png')))
ICON_GLOBE = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'globe16.png')))
ICON_LOGO = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'debreate16.png')))
