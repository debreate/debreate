
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.panel

import wx

from wx.lib.scrolledpanel import ScrolledPanel as sp

from libdebreate.ident import inputid
from ui.helper         import GetField
from ui.layout         import BoxSizer
from ui.style          import PANEL_BORDER


## Global function for setting & updating scrolled window scrollbars
#
#  @param window
#    \b \e wx.ScrolledWindow to be set
#  @return
#    \b \e True if scrollbars were set
def SetScrollbars(window):
  if isinstance(window, wx.ScrolledWindow):
    window.SetScrollbars(20, 20, 0, 0)
    return True
  return False


## Abstract class
class PanelBase:
  ## Checks if the instance has children windows
  def HasChildren(self):
    if isinstance(self, wx.Window):
      return len(self.GetChildren()) > 0
    return False


## A wx.Panel with a border
#
#  This is to work around differences in wx 3.0 with older versions
class BorderedPanel(wx.Panel, PanelBase):
  def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL, name=wx.PanelNameStr):
    wx.Panel.__init__(self, parent, ID, pos, size, style|PANEL_BORDER, name)

  ## Hide the panel's border
  def HideBorder(self):
    return self.ShowBorder(False)

  ## Show or hide the panel's border
  #
  #  @param show
  #    If \b \e True, show border, otherwise hide
  #  @return
  #    \b \e True if border visible state changed
  def ShowBorder(self, show=True):
    style = self.GetWindowStyleFlag()
    if show:
      if not style & PANEL_BORDER:
        self.SetWindowStyleFlag(style|PANEL_BORDER)
        return True
    elif style & PANEL_BORDER:
      self.SetWindowStyleFlag(style&~PANEL_BORDER)
      return True
    return False


## A wx.ScrolledWindow that sets scrollbars by default
class ScrolledPanel(sp, PanelBase):
  def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.HSCROLL|wx.VSCROLL, name="scrolledPanel"):
    sp.__init__(self, parent, win_id, pos, size, style, name)
    sp.SetupScrolling(self)


## A ui.panel.ScrolledPanel that defines methods to add child sections
class SectionedPanel(ScrolledPanel):
  def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
        scrollDir=wx.VERTICAL, name="sectionedPanel"):

    style = wx.VSCROLL
    if scrollDir == wx.HORIZONTAL:
      style = wx.HSCROLL

    ScrolledPanel.__init__(self, parent, win_id, pos, size, style, name)

    # *** Event Handling *** #

    self.Bind(wx.EVT_CHECKBOX, self.OnSelect)

    # *** Layout *** #

    lyt_main = BoxSizer(scrollDir)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)

  ## @todo Doxygen
  def AddSection(self, panel):
    pnl_fields = panel.GetChildren()
    if pnl_fields:
      lyt_panel = None
      for FIELD in pnl_fields:
        lyt_panel = FIELD.GetContainingSizer()
        if lyt_panel:
          break
      if lyt_panel:
        padding = 0
        if self.HasSections():
          padding = 5

        # Section orientation should be opposite of main
        orient = wx.HORIZONTAL
        sz = self.GetSizer()
        if sz.GetOrientation() == wx.HORIZONTAL:
          orient = wx.VERTICAL

        lyt_sect = BoxSizer(orient)
        lyt_sect.Add(lyt_panel, 1, wx.EXPAND)
        lyt_sect.Add(wx.CheckBox(panel, inputid.CHECK), 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)

        panel.SetAutoLayout(True)
        panel.SetSizer(lyt_sect)
        panel.Layout()

        sz.Add(panel, 0, wx.EXPAND|wx.TOP, padding)
        self.Layout()

        return True
    return False

  ## @todo Doxygen
  def GetSection(self, index):
    return self.GetChildren()[index]

  ## Retrieves number of sections
  def GetSectionCount(self):
    return len(self.GetSizer().GetChildWindows())

  ## @todo Doxygen
  def GetSectionIndex(self, item):
    sections = self.GetChildren()
    if item in sections:
      return sections.index(item)

  ## Check if any sections have been added
  def HasSections(self):
    return self.GetSectionCount() > 0

  ## Checks if any sections are selected
  def HasSelected(self):
    for SECT in self.GetChildren():
      if self.IsSelected(SECT):
        return True
    return False

  ## Checks if section check box state is 'checked'
  def IsSelected(self, section):
    if isinstance(section, int):
      section = self.GetSection(section)
    return GetField(section, inputid.CHECK).GetValue()

  ## @todo Doxygen
  def OnSelect(self, event=None):
    self.PostCheckBoxEvent()

  ## @todo Doxygen
  def PostCheckBoxEvent(self, target=None):
    if not target:
      target = self.Parent
    wx.PostEvent(target, wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, self.Id))

  ## @todo Doxygen
  def RemoveSection(self, item):
    if isinstance(item, int):
      item = self.GetSection(item)

    sz = self.GetSizer()
    sz.Detach(item)
    removed = item.Destroy()

    # Remove padding of first item
    first_section = sz.GetItemAtIndex(0)
    if first_section:
      sz.Detach(first_section)
      sz.Insert(0, first_section, 0, wx.EXPAND)

    self.Layout()
    return removed

  ## Removes all sections that are selected
  def RemoveSelected(self):
    for SECT in reversed(self.GetChildren()):
      selected = self.IsSelected(SECT)

      if selected:
        self.RemoveSection(SECT)


## Class designed for custom controls parented with a BorderedPanel
class ControlPanel:
  MainCtrl = None

  ## Retrieve main child of panel
  #
  #  Intended for use in input.essential.EssentialField
  def GetMainControl(self):
    return self.MainCtrl
