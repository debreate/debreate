# -*- coding: utf-8 -*-

## \package ui.menu

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.wizardhelper import GetTopWindow


## A menu bar that stores an ID along with a menu
#  
#  \param parent
#    \b \e wx.Window : Parent window of the menu bar
#        If not None, automatically sets itself as parent's menu bar
#  \param style
#    \b \e int : Menu bar style
class MenuBar(wx.MenuBar):
    def __init__(self, parent=None, style=0):
        wx.MenuBar.__init__(self, style)
        
        self.id_list = []
        
        if isinstance(parent, wx.Frame):
            parent.SetMenuBar(self)
    
    
    ## Append a menu to the end of menu bar
    #  
    #  \override wx.MenuBar.Append
    #  \param menu
    #    \b \e wx.Menu : Menu to be appended
    #  \param title
    #    \b \e unicode|str : Text to be displayed in the menu bar
    #  \param ID
    #    \b \e int : ID to store for menu
    def Append(self, menu, title, ID):
        self.id_list.append(ID)
        
        return wx.MenuBar.Append(self, menu, title)
    
    
    ## Finds a wx.Menu by ID
    #  
    #  \param ID
    #    \b \e int : ID to search for in menu bar
    #  \return
    #    The wx.Menu with ID
    def GetMenuById(self, ID):
        m_index = self.id_list.index(ID)
        
        return self.GetMenu(m_index)
    
    
    ## Insert a menu to a specified position in the menu bar
    #  
    #  \override wx.MenuBar.Insert
    #  \param index
    #    \b \e int : Position index to insert menu
    #  \param menu
    #    \b \e wx.Menu : Menu to be inserted
    #  \param title
    #    \b \e unicode|str : Text to be displayed in the menu bar
    #  \param ID
    #    \b \e int : ID to store for menu
    def Insert(self, index, menu, title, ID):
        self.id_list.insert(index, ID)
        
        return wx.MenuBar.Insert(self, index, menu, title)


## A custom menu designed for use with PanelMenuBar
class PanelMenu(wx.StaticText):
    def __init__(self, parent=None, win_id=wx.ID_ANY, label=wx.EmptyString, name=u'menu'):
        if not parent:
            parent = GetTopWindow()
        
        wx.StaticText.__init__(self, parent, win_id, name=name)


## A custom menu bar designed for use in wx.Panel
class PanelMenuBar(wx.Panel):
    def __init__(self, parent, win_id=wx.ID_ANY, name=u'menubar'):
        wx.Panel.__init__(self, parent, win_id, name=name)
        
        lyt_main = wx.BoxSizer(wx.HORIZONTAL)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
    
    
    ## TODO: Doxygen
    def Add(self, menu, label=None):
        if label:
            menu.SetLabel(label)
        
        if not menu.Parent == self:
            menu.Reparent(self)
        
        lyt = self.GetSizer()
        lyt.Add(menu)
        
        self.Layout()
