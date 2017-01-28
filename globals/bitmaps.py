# -*- coding: utf-8 -*-

## \package globals.bitmaps

# MIT licensing
# See: docs/LICENSE.txt


from dbr.image      import GetBitmap
from globals.paths  import ConcatPaths
from globals.paths  import PATH_bitmaps


LOGO = ConcatPaths((PATH_bitmaps, u'icon/64/logo.png'))

ICON_ERROR = GetBitmap(u'error', 64, u'icon')
ICON_EXCLAMATION = ICON_ERROR
ICON_QUESTION = GetBitmap(u'question', 64, u'icon')
ICON_INFORMATION = GetBitmap(u'info', 64, u'icon')
ICON_WARNING = GetBitmap(u'warn', 64, u'icon')

ICON_CLOCK = GetBitmap(u'clock', 16, u'icon')
ICON_GLOBE = GetBitmap(u'globe', 16, u'icon')
ICON_LOGO = GetBitmap(u'logo', 16, u'icon')
