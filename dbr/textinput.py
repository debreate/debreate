# -*- coding: utf-8 -*-

## \package dbr.textinput

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.font       import MONOSPACED_LG
from dbr.language   import GT


MT_NO_BTN = 0
MT_BTN_TL = 1
MT_BTN_TR = 2
MT_BTN_BL = 3
MT_BTN_BR = 4

button_H_pos = {
    MT_BTN_TL: wx.ALIGN_LEFT,
    MT_BTN_TR: wx.ALIGN_RIGHT,
    MT_BTN_BL: wx.ALIGN_LEFT,
    MT_BTN_BR: wx.ALIGN_RIGHT,
}

class MonospaceTextCtrl(wx.Panel):
    def __init__(self, parent, ID=wx.ID_ANY, button=MT_NO_BTN, name=wx.EmptyString, style=wx.TE_MULTILINE):
        wx.Panel.__init__(self, parent, ID)
        
        layout_V1 = wx.BoxSizer(wx.VERTICAL)
        
        self.text_area = wx.TextCtrl(self, ID, name=name, style=style|wx.TE_MULTILINE)
        self.text_area.SetFont(MONOSPACED_LG)
        
        layout_V1.Add(self.text_area, 1, wx.EXPAND|wx.ALL, 5)
        
        if button:
            btn_font = wx.Button(self, label=GT(u'Text Size'))
            if button in (MT_BTN_TL, MT_BTN_TR):
                layout_V1.Insert(0, btn_font, 0, button_H_pos[button]|wx.LEFT|wx.RIGHT, 5)
            
            else:
                layout_V1.Add(btn_font, 0, button_H_pos[button]|wx.LEFT|wx.RIGHT, 5)
            
            btn_font.Bind(wx.EVT_BUTTON, self.OnToggleTextSize)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_V1)
        self.Layout()
    
    
    def Clear(self):
        self.text_area.Clear()
    
    
    def GetInsertionPoint(self):
        return self.text_area.GetInsertionPoint()
    
    
    def GetValue(self):
        return self.text_area.GetValue()
    
    
    def IsEmpty(self):
        return self.text_area.IsEmpty()
    
    
    def OnToggleTextSize(self, event=None):
        # Save insertion point
        insertion = self.text_area.GetInsertionPoint()
        
        sizes = {
            7: 8,
            8: 10,
            10: 11,
            11: 7,
        }
        
        font = self.text_area.GetFont()
        new_size = sizes[font.GetPointSize()]
        font.SetPointSize(new_size)
        
        self.text_area.SetFont(font)
        self.text_area.SetInsertionPoint(insertion)
        self.text_area.SetFocus()
    
    
    def SetInsertionPoint(self, point):
        self.text_area.SetInsertionPoint(point)
    
    
    def SetInsertionPointEnd(self):
        self.text_area.SetInsertionPointEnd()
    
    
    def SetValue(self, value):
        self.text_area.SetValue(value)
    
    
    def WriteText(self, text):
        self.text_area.WriteText(text)
