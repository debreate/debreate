
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Display handling.
#
#  @module system.display

import subprocess

import wx

from libdbr        import paths
from libdbr.logger import Logger


__logger = Logger(__name__)

## Retrieves dimensions of primary display.
#
#  @return
#    Dictionary containing x,y coordinates & width & height of primary display.
#  @todo
#    - use 1 or 2 alternate methods (wx.Display???)
#    - make platform independent
def __getPrimaryRect():
  xrandr = paths.getExecutable("xrandr")
  if not xrandr:
    __logger.info("'xrandr' not found, cannot determine center of primary display")
    return None
  res = subprocess.run([xrandr], check=True, stdout=subprocess.PIPE)
  if res.returncode != 0:
    __logger.info("'xrandr' execution failed, cannot determine center of primary display")
    return None
  disp_line = None
  for li in res.stdout.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
    if " connected primary " in li:
      disp_line = li
      break
  if not disp_line:
    __logger.info("cannot determine primary display from 'xrandr' output")
    return None
  disp = disp_line.split(" connected primary ", 1)[1].strip().split(" ")[0]
  tmp = disp.replace("x", "+", 1).split("+")
  if len(tmp) < 4:
    __logger.info("cannot determine primary display dimensions from 'xrandr' output")
    return None
  rect = {"x": int(tmp[2]), "y": int(tmp[3]), "w": int(tmp[0]), "h": int(tmp[1])}

  __logger.info("display rect '{}'".format(rect))

  return rect


## Centers the window on the primary display.
#
#  @param window
#    wx.Window instance to be centered.
#  @param size
#    Override detected size from window.
#  @todo
#    - make platform independent
def centerOnPrimary(window, size=None):
  __logger.debug("Attempting to center window: {} ({})".format(window.Name, window))

  rect = __getPrimaryRect()
  if not rect:
    # fallback to built-in method
    window.Center()
    return

  w_size = window.GetSize() if not size else size
  pos_x = int((rect["w"] - w_size.GetWidth()) / 2)
  pos_y = int((rect["h"] - w_size.GetHeight()) / 2)

  window.SetPosition(wx.Point(pos_x, pos_y))

  __logger.debug("theoretical position: {}".format((pos_x, pos_y,)))
  __logger.debug("Actual Position:      {}".format(window.GetPosition().Get()))
