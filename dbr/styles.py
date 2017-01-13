# -*- coding: utf-8 -*-

## \package dbr.styles

# MIT licensing
# See: docs/LICENSE.txt


import wx


if wx.MAJOR_VERSION > 2:
    PANEL_BORDER = wx.BORDER_THEME

else:
    PANEL_BORDER = wx.BORDER_MASK
