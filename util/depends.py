
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import sys

from libdbr.logger import getLogger
from libdbr.modules import getModule


logger = getLogger()

def checkWx():
  wx = getModule("wx")
  wx_min = [4, 1, 1]
  wx_ver = []
  for v in wx.__version__.split("."):
    wx_ver.append(int(v))
  if wx_ver < wx_min:
    tmp = ".".join(str(wx_min).strip("[]").split(", "))
    logger.error("wxPython minimum required version is {}, found {}".format(tmp, wx.__version__))
    sys.exit(1)
