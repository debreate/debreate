# -*- coding: utf-8 -*-

# ============================== MIT LICENSE ==================================
#
# Copyright (c) 2015 Jordan Irwin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# =============================================================================

import wx, decor.buttons as dbbuttons, wx.lib.newevent

ID_PREV = wx.NewId()
ID_NEXT = wx.NewId()

class WizardLayout(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, page_list=None):
        super(WizardLayout, self).__init__(parent, id, page_list)

        self.parent = parent

        # List of pages available in the wizard
        self.pages = []

        # A Header for the wizard
        self.title = wx.Panel(self, style=wx.RAISED_BORDER)
        self.title.SetBackgroundColour((10, 47, 162))
        self.title_txt = wx.StaticText(self.title, -1, "Title") # Text displayed from objects "name" - object.GetName()
        self.title_txt.SetForegroundColour((255, 255, 255))

        headerfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD) # font to use in the header
        self.title_txt.SetFont(headerfont)

        # Position the text in the header
        title_sizer = wx.GridSizer(1, 1)
        title_sizer.Add(self.title_txt, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        self.title.SetSizer(title_sizer)
        self.title.Layout()

        # Previous and Next buttons
        self.button_prev = dbbuttons.ButtonPrev(self, ID_PREV)
        self.button_next = dbbuttons.ButtonNext(self, ID_NEXT)

        wx.EVT_BUTTON(self.button_prev, -1, self.ChangePage)
        wx.EVT_BUTTON(self.button_next, -1, self.ChangePage)

        self.ChangePageEvent, self.EVT_CHANGE_PAGE = wx.lib.newevent.NewCommandEvent()
        self.evt = self.ChangePageEvent(0)

        # Button sizer includes header
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddSpacer(5)
        button_sizer.Add(self.title, 1, wx.EXPAND)
        button_sizer.Add(self.button_prev)
        button_sizer.AddSpacer(5)
        button_sizer.Add(self.button_next)
        button_sizer.AddSpacer(5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(button_sizer, 0, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()

        # These widgets are put into a list so that they are not automatically hidden
        self.permanent_children = (self.title, self.button_prev, self.button_next)

    def SetPages(self, pages):
        # Make sure all pages are hidden
        children = self.GetChildren()
        for child in children:
            if child not in self.permanent_children:
                child.Hide()

        self.ClearPages() # Remove any current pages from the wizard

        # These two item are just for checking to make sure that pages is right type
        list = []
        tuple = ()
        if type(pages) not in (type(list), type(tuple)):
            raise TypeError("Argument 2 of dbwizard.SetPages() must be List or Tuple")

        for page in pages:
            self.pages.append(page)
            self.sizer.Insert(1, page, 1, wx.EXPAND)
            # Show the first page
            if page != pages[0]:
                page.Hide()
            else:
                page.Show()
                self.title_txt.SetLabel(page.GetName())

        # Disable "previous" button
        self.button_prev.Disable()
        self.Layout()

    def ShowPage(self, id):
        for p in self.pages:
            if p.GetId() != id:
                p.Hide()
            else:
                p.Show()
                name = p.GetName()
                self.title_txt.SetLabel(name)

                # Previous and next buttons
                if (name == "Information"):
                    self.button_prev.Disable()
                elif (not self.button_prev.IsEnabled()):
                    self.button_prev.Enable()

                if (name == "Build"):
                    self.button_next.Disable()
                elif (not self.button_next.IsEnabled()):
                    self.button_next.Enable()

        self.Layout()
        for child in self.GetChildren():
            wx.PostEvent(child, self.evt)

    def ChangePage(self, event):
        id = event.GetEventObject().GetId()

        index = 0;
        # Get index of currently shown page
        for page in self.pages:
            if page.IsShown():
                index = self.pages.index(page)

        if id == ID_PREV:
            if index != 0:
                index -= 1
        elif id == ID_NEXT:
            if index != len(self.pages) - 1:
                index += 1

        # Show the indexed page
        if (self.pages):
            self.ShowPage(self.pages[index].GetId());

            # Check current page in "pages menu"
            for p in self.parent.pages:
                if self.pages[index].GetId() == p.GetId():
                    p.Check()

    def ClearPages(self):
        for page in self.pages:
            self.sizer.Remove(page)
        self.pages = []
        # Re-enable the buttons if the have been disabled
        self.EnableNext()
        self.EnablePrev()

    def SetTitle(self, title):
        self.title_txt.SetLabel(title)
        self.Layout()

    def EnableNext(self, value=True):
        if type(value) in (type(True), type(1)):
            if value:
                self.button_next.Enable()
            else:
                self.button_next.Disable()
        else:
            raise TypeError("Must be bool or int value")

    def DisableNext(self):
        self.EnableNext(False)

    def EnablePrev(self, value=True):
        if type(value) in (type(True), type(1)):
            if value:
                self.button_prev.Enable()
            else:
                self.button_prev.Disable()
        else:
            raise TypeError("Must be bool or int value")

    def DisablePrev(self):
        self.EnablePrev(False)

    def GetCurrentPage(self):
        for page in self.pages:
            if page.IsShown():
                return page
