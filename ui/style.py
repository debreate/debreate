# -*- coding: utf-8 -*-

## \package ui.style

# MIT licensing
# See: docs/LICENSE.txt


import wx


if wx.MAJOR_VERSION > 2:
    PANEL_BORDER = wx.BORDER_THEME

else:
    PANEL_BORDER = wx.BORDER_MASK


## Layout styles for sizers
class layout:
    ALGN_C = wx.ALIGN_CENTER
    ALGN_CH = wx.ALIGN_CENTER_HORIZONTAL
    ALGN_CV = wx.ALIGN_CENTER_VERTICAL
    ALGN_LB = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
    ALGN_RB = wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM
    PAD_LR = wx.LEFT|wx.RIGHT
    PAD_LRB = PAD_LR|wx.BOTTOM
    PAD_LRT = PAD_LR|wx.TOP
