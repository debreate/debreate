# -*- coding: utf-8 -*-

## \package globals.bitmaps

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.paths import ConcatPaths
from globals.paths import PATH_bitmaps


LOGO = ConcatPaths((PATH_bitmaps, u'debreate64.png'))

ICON_ERROR = ConcatPaths((PATH_bitmaps, u'error64.png'))
ICON_EXCLAMATION = ICON_ERROR
ICON_QUESTION = ConcatPaths((PATH_bitmaps, u'question64.png'))
ICON_INFORMATION = ConcatPaths((PATH_bitmaps, u'information64.png'))
ICON_WARNING = ConcatPaths((PATH_bitmaps, u'warning64.png'))

ICON_CLOCK = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'clock16.png')))
ICON_GLOBE = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'globe16.png')))
ICON_LOGO = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'debreate16.png')))
