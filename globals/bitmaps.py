# -*- coding: utf-8 -*-

## \package <package>

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.paths import ConcatPaths
from globals.paths import PATH_app


PATH_bitmaps = u'{}/bitmaps'.format(PATH_app)

ICON_ERROR = ConcatPaths((PATH_bitmaps, u'error64.png'))
ICON_INFORMATION = ConcatPaths((PATH_bitmaps, u'question64.png'))

BUTTON_HELP = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'question32.png')))
BUTTON_REFRESH = wx.Bitmap(ConcatPaths((PATH_bitmaps, u'btn-refresh32.png')))
