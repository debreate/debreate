
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.bitmaps

from dbr.image     import GetBitmap
from globals.paths import getBitmapsDir
from libdbr        import paths


LOGO = paths.join(getBitmapsDir(), "icon", "64", "logo.png")

ICON_ERROR = GetBitmap("error", 64, "icon")
ICON_EXCLAMATION = ICON_ERROR
ICON_QUESTION = GetBitmap("question", 64, "icon")
ICON_INFORMATION = GetBitmap("info", 64, "icon")
ICON_WARNING = GetBitmap("warn", 64, "icon")

ICON_CLOCK = GetBitmap("clock", 16, "icon")
ICON_GLOBE = GetBitmap("globe", 16, "icon")
ICON_LOGO = GetBitmap("logo", 16, "icon")
