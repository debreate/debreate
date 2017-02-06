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
    ALGN_T = wx.ALIGN_TOP
    ALGN_B = wx.ALIGN_BOTTOM
    
    ALGN_L = wx.ALIGN_LEFT
    ALGN_LT = ALGN_L|ALGN_T
    ALGN_LB = ALGN_L|ALGN_B

    ALGN_R = wx.ALIGN_RIGHT
    ALGN_RT = ALGN_R|ALGN_T
    ALGN_RB = ALGN_R|ALGN_B
    
    ALGN_C = wx.ALIGN_CENTER
    ALGN_CH = wx.ALIGN_CENTER_HORIZONTAL
    ALGN_CV = wx.ALIGN_CENTER_VERTICAL
    ALGN_CL = ALGN_CV|ALGN_L
    ALGN_CR = ALGN_CV|ALGN_R
    ALGN_CT = ALGN_CH|ALGN_T
    ALGN_CB = ALGN_CH|ALGN_B
    
    PAD_LT = wx.LEFT|wx.TOP
    PAD_LB = wx.LEFT|wx.BOTTOM
    PAD_LTB = PAD_LT|wx.BOTTOM
    PAD_RT = wx.RIGHT|wx.TOP
    PAD_RB = wx.RIGHT|wx.BOTTOM
    PAD_RTB = PAD_RT|wx.BOTTOM
    PAD_LR = wx.LEFT|wx.RIGHT
    PAD_LRB = PAD_LR|wx.BOTTOM
    PAD_LRT = PAD_LR|wx.TOP
    PAD_TB = wx.TOP|wx.BOTTOM
