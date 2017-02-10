# -*- coding: utf-8 -*-

## \package ui.menu

# MIT licensing
# See: docs/LICENSE.txt


import wx


## A menu bar that stores an ID along with a menu
class MenuBar(wx.MenuBar):
    ## Constructor
    #
    #  \param parent
    #    <b><i>wx.Window</i></b> parent window of the menu bar
    #    If not None, automatically sets itself as parent's menu bar
    #  \param style
    #    Menu bar style represented by an <b><i>integer</i></b> value
    def __init__(self, parent=None, style=0):
        wx.MenuBar.__init__(self, style)
        
        self.id_list = []
        
        if isinstance(parent, wx.Frame):
            parent.SetMenuBar(self)
    
    
    ## Append a menu to the end of menu bar
    #
    #  \param menu
    #    <b><i>wx.Menu</i></b> instance to be appended
    #  \param title
    #    Label to be displayed in the menu bar
    #  \param menuId
    #    Unique <b><i>integer</i></b> identifier to store for menu
    def Append(self, menu, title, menuId):
        self.id_list.append(menuId)
        
        return wx.MenuBar.Append(self, menu, title)
    
    
    ## Finds a wx.Menu by ID
    #
    #  \param menuId
    #    Menu <b><i>integer</i></b> identifier to search for in menu bar
    #  \return
    #    The <b><i>wx.Menu</i></b> with using identifier
    def GetMenuById(self, menuId):
        m_index = self.id_list.index(menuId)
        
        return self.GetMenu(m_index)
    
    
    ## Insert a menu to a specified position in the menu bar
    #
    #  \param index
    #    Position index to insert menu
    #  \param menu
    #    <b><i>wx.Menu</i></b> instance to be inserted
    #  \param title
    #    Label to be displayed in the menu bar
    #  \param menuId
    #    Unique <b><i>integer</i></b> identifier to store for menu
    def Insert(self, index, menu, title, menuId):
        self.id_list.insert(index, menuId)
        
        return wx.MenuBar.Insert(self, index, menu, title)
