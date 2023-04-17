
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.hyperlink

import webbrowser, wx

from ui.layout import BoxSizer


## Control for opening a webpage with a mouse click
#
#  wx.HyperlinkCtrl seems to have some issues in wx 3.0, so this class is used instead.
#
#  @param parent
#    \b \e wx.Window : Parend window
#  @param ID
#    \b \e int : Identifier
#  @param label
#    \b \e str : Text displayed on hyperlink
#  @param url
#    \b \e str : Link to open when hyperlink clicked
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

    self.text.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
    self.text_bg.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver)
    self.text_bg.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseOut)

    self.text.SetForegroundColour(wx.Colour(0, 0, 255))

    layout_V1 = BoxSizer(wx.VERTICAL)
    layout_V1.AddStretchSpacer(1)
    layout_V1.Add(self.text_bg, 0, wx.ALIGN_CENTER)
    layout_V1.AddStretchSpacer(1)

    self.SetAutoLayout(True)
    self.SetSizer(layout_V1)
    self.Layout()

  ## @todo Doxygen
  def OnLeftClick(self, event=None):
    webbrowser.open(self.url)

    if not self.clicked:
      self.text.SetForegroundColour("purple")
      self.clicked = True

    if event:
      event.Skip(True)

  ## @todo Doxygen
  def OnMouseOut(self, event=None):
    self.SetCursor(wx.NullCursor)
    self.text.SetFont(self.FONT_DEFAULT)

  ## @todo Doxygen
  def OnMouseOver(self, event=None):
    self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
    self.text.SetFont(self.FONT_HIGHLIGHT)

    if event:
      event.Skip(True)

  ## @todo Doxygen
  def SetDefaultFont(self, font):
    self.FONT_DEFAULT = font

  ## @todo Doxygen
  def SetHighlightFont(self, font):
    self.FONT_HIGHLIGHT = font
