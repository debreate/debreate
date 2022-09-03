## \package globals.bitmaps

# MIT licensing
# See: docs/LICENSE.txt


from dbr.image      import GetBitmap
from globals.paths  import ConcatPaths
from globals.paths  import PATH_bitmaps


LOGO = ConcatPaths((PATH_bitmaps, "icon/64/logo.png"))

ICON_ERROR = GetBitmap("error", 64, "icon")
ICON_EXCLAMATION = ICON_ERROR
ICON_QUESTION = GetBitmap("question", 64, "icon")
ICON_INFORMATION = GetBitmap("info", 64, "icon")
ICON_WARNING = GetBitmap("warn", 64, "icon")

ICON_CLOCK = GetBitmap("clock", 16, "icon")
ICON_GLOBE = GetBitmap("globe", 16, "icon")
ICON_LOGO = GetBitmap("logo", 16, "icon")
