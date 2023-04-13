
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## @module util.depends

import sys

from libdbr.logger  import Logger
from libdbr.modules import getModule


logger = Logger(__name__)

__wx_version = None

def getWxVersion():
  global wx, __wx_version
  wx = getModule("wx")
  if __wx_version != None:
    return __wx_version
  ver = []
  for v in wx.__version__.split("."):
    ver.append(int(v))
  __wx_version = tuple(ver)
  return __wx_version

def checkWx():
  wx_min = [4, 0, 7]
  wx_rec = [4, 2, 0]
  wx_ver = list(getWxVersion())
  if wx_ver < wx_min:
    tmp = ".".join(str(wx_min).strip("[]").split(", "))
    msg = "wxPython minimum required version is {}, found {}".format(tmp, wx.__version__)
    logger.error(msg)
    # attempt to show a dialog
    try:
      app = wx.App()
      dialog = wx.MessageDialog(None, msg, "wx Version Error", wx.OK|wx.ICON_ERROR)
      app.SetTopWindow(dialog)
      dialog.ShowModal()
      dialog.Destroy()
      app.MainLoop()
    except:
      pass
    sys.exit(1)
  if wx_ver < wx_rec:
    tmp = ".".join(str(wx_rec).strip("[]").split(", "))
    logger.warn("minimum recommened version of wxPython is {}, but found {}, app may not function as intended".format(tmp, wx.__version__))
