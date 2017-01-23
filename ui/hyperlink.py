# -*- coding: utf-8 -*-

## \package ui.hyperlink

# MIT licensing
# See: docs/LICENSE.txt


import webbrowser, wx

from ui.layout import BoxSizer


## Control for opening a webpage with a mouse click
#  
#  wx.HyperlinkCtrl seems to have some issues in wx 3.0,
#    so this class is used instead.
#  \param parent
#        \b \e wx.Window : Parend window
#  \param ID
#        \b \e int : Identifier
#  \param label
#        \b \e unicode|str : Text displayed on hyperlink
#  \param url
#        \b \e unicode|str : Link to open when hyperlink clicked
class Hyperlink(wx.Panel):
    def __init__(self, parent, ID, label, url):
        wx.Panel.__init__(self, parent, ID)
        
        self.url = url
        self.text_bg = wx.Panel(self)
        self.text = wx.StaticText(self.text_bg, label=label)
        
        self.clicked = False
        
        self.FONT_DEFAULT = self.text.GetFont()
        self.FONT_HIGHLIGHT = self.text.GetFont()
        self.FONT_HIGHLIGHT.SetUnderlined(True)
        
        wx.EVT_LEFT_DOWN(self.text, self.OnLeftClick)
        wx.EVT_ENTER_WINDOW(self.text_bg, self.OnMouseOver)
        wx.EVT_LEAVE_WINDOW(self.text_bg, self.OnMouseOut)
        
        self.text.SetForegroundColour(wx.Colour(0, 0, 255))
        
        layout_V1 = BoxSizer(wx.VERTICAL)
        layout_V1.AddSpacer(1, wx.EXPAND)
        layout_V1.Add(self.text_bg, 0, wx.ALIGN_CENTER)
        layout_V1.AddSpacer(1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_V1)
        self.Layout()
    
    
    ## TODO: Doxygen
    def OnLeftClick(self, event=None):
        webbrowser.open(self.url)
        
        if not self.clicked:
            self.text.SetForegroundColour(u'purple')
            self.clicked = True
        
        if event:
            event.Skip(True)
    
    
    ## TODO: Doxygen
    def OnMouseOut(self, event=None):
        self.SetCursor(wx.NullCursor)
        self.text.SetFont(self.FONT_DEFAULT)
    
    
    ## TODO: Doxygen
    def OnMouseOver(self, event=None):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.text.SetFont(self.FONT_HIGHLIGHT)
        
        if event:
            event.Skip(True)
    
    
    ## TODO: Doxygen
    def SetDefaultFont(self, font):
        self.FONT_DEFAULT = font
    
    
    ## TODO: Doxygen
    def SetHighlightFont(self, font):
        self.FONT_HIGHLIGHT = font
