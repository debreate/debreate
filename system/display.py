## \package system.display

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.execute import GetCommandOutput
from globals.execute import GetExecutable
from globals.strings import StringIsNumeric
from libdbr.logger   import Logger


logger = Logger(__name__)

## Retrieves dimensions of primary display
#
#  TODO:
#  - use 1 or 2 alternate methods (wx.Display???)
#  - make platform independent
def GetPrimaryDisplayRect():
  rect = None

  # wx 3.0 does not recognize primary display correctly
  # FIXME: version 2 no longer supported
  if wx.MAJOR_VERSION <=2:
    primary = None

    # Try to find the primary display within first 10 displays
    for X in range(10):
      try:
        dsp = wx.Display(X)
        if dsp.IsPrimary():
          primary = dsp

          break

      except AssertionError:
        pass

    if primary:
      rect = primary.GetGeometry()

      # Reorder for compatibility with xrandr output
      rect = (rect[2], rect[3], rect[0], rect[1],)

      logger.debug("GetPrimaryDisplayRect: Using wx.Display")

  # Fall back to using xrandr
  if not rect:
    CMD_xrand = GetExecutable("xrandr")

    if not CMD_xrand:
      return None

    output = GetCommandOutput(CMD_xrand).split("\n")

    for LINE in output:
      LINE = LINE.lower()
      if "primary" in LINE:
        LINE = LINE.split("primary")[1].strip().split(" ")[0]
        posX = LINE.split("x")
        posY = posX[1].split("+")
        posX = posX[0]
        width = posY[1]
        height = posY[2]
        posY = posY[0]

        rect = [posX, posY, width, height,]
        for INDEX in range(len(rect)):
          X = rect[INDEX]
          if not StringIsNumeric(X):
            # FIXME: Break out of second loop & call continue on first?
            return None

          rect[INDEX] = int(X)

        logger.debug("GetPrimaryDisplayRect: Using xrandr")

        break

  if rect:
    return tuple(rect)


## Centers the window on the primary display
#
#  TODO:
#  - make platform independent
#
#  \param window
#  \b \e wx.Window instance to be centered
def CenterOnPrimaryDisplay(window):
  logger.debug("Attempting to center window: {} ({})".format(window.Name, window))

  display_rect = GetPrimaryDisplayRect()

  logger.debug("Primary display: {}".format(display_rect))

  if not display_rect:
    return False

  window_size = window.GetSize().Get()

  dx = display_rect[2]
  dy = display_rect[3]
  dw = display_rect[0]
  dh = display_rect[1]

  x_diff = (dw - window_size[0]) / 2
  y_diff = (dh - window_size[1]) / 2

  debug = logger.debugging()

  if debug:
    print("  X difference: {}".format(x_diff))
    print("  Y difference: {}".format(y_diff))

  # NOTE: May be a few pixels off
  pos_x = dx + x_diff
  pos_y = dy + y_diff

  if debug:
    print("\n  Theoretical position: {}".format((pos_x, pos_y,)))
    print("  Actual Position:	  {}".format(window.GetPositionTuple()))

  window.SetPosition((pos_x, pos_y))

  return True
