
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.font

import wx


def GetMonospacedFont(size):
  return wx.Font(size, wx.FONTFAMILY_TELETYPE,
        wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)


# @todo Replace with registered fonts above
SIZE_SM = 6
SIZE_MS = 7
SIZE_MD = 8
SIZE_LG = 10

# Monospaced
MONOSPACED_SM = wx.Font(SIZE_SM, wx.FONTFAMILY_TELETYPE,
              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
MONOSPACED_MS = wx.Font(SIZE_MS, wx.FONTFAMILY_TELETYPE,
              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
MONOSPACED_MD = wx.Font(SIZE_MD, wx.FONTFAMILY_TELETYPE,
              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
MONOSPACED_LG = wx.Font(SIZE_LG, wx.FONTFAMILY_TELETYPE,
              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

MONOSPACED_SM.name = "monospaced_sm"
MONOSPACED_MS.name = "monospaced_ms"
MONOSPACED_MD.name = "monospaced_md"
MONOSPACED_LG.name = "monospaced_lg"
