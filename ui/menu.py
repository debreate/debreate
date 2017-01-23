# -*- coding: utf-8 -*-

## \package ui.menu

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.wizardhelper   import GetTopWindow
from ui.layout              import BoxSizer
from ui.panel               import BorderedPanel


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
        
        wx.StaticText.__init__(self, parent, win_id, label, name=name)
        
        self.fg_orig = self.GetForegroundColour()
        
        # Begin with deselected state
        self.Selected = False
        
        self.Menu = wx.Menu()
        
        # *** Event Handling *** #
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnSelect)
        
        self.Bind(wx.EVT_MENU, self.OnMenuClose)
        self.Bind(wx.EVT_MENU_CLOSE, self.OnMenuClose)
    
    
    ## TODO: Doxygen
    def Append(self, menu_id, label):
        self.Menu.Append(menu_id, label)
    
    
    ## Checks if menu is in selected state
    def IsSelected(self):
        return self.Selected
    
    
    ## TODO: doxygen
    def OnMenuClose(self, event=None):
        self.Select(False)
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnSelect(self, event=None):
        if event:
            # Send event to parent PanelMenuBar instance
            wx.PostEvent(self.Parent, event)
    
    
    ## Sets menu selected state
    #  
    #  \param selected
    #    Sets state to selected value
    def Select(self, select=True):
        if select and not self.Selected:
            self.SetForegroundColour(wx.WHITE)
            self.Selected = True
            
            self.PopupMenu(self.Menu)
        
        elif not select and self.Selected:
            # Reset to deselected state
            self.SetForegroundColour(self.fg_orig)
            self.Selected = False
    
    
    ## Toggles selected state
    def ToggleSelected(self):
        self.Select(not self.Selected)


## A custom menu bar designed for use in wx.Panel
class PanelMenuBar(BorderedPanel):
    def __init__(self, parent, win_id=wx.ID_ANY, name=u'menubar'):
        BorderedPanel.__init__(self, parent, win_id, name=name)
        
        self.Padding = 5
        
        # *** Event Handling *** #
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnSelect)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.HORIZONTAL)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
    
    
    ## Create a PanelMenu instance & add it to menu bar
    #  
    #  \param label
    #    Text displayed for menu
    #  \param win_id
    #    ID to use for menu
    def Add(self, label, win_id=wx.ID_ANY):
        new_menu = PanelMenu(self, win_id, label)
        self.AddItem(new_menu)
    
    
    ## Add a PanelMenu instance to menu bar
    #  
    #  \param menu
    #    \b \e PanelMenu instance to be added
    #  \param label
    #    Optional \b \e string label to override menu label
    def AddItem(self, menu, label=None):
        if label:
            menu.SetLabel(label)
        
        if not menu.Parent == self:
            menu.Reparent(self)
        
        lyt = self.GetSizer()
        lyt.Add(menu, 0, wx.ALL, self.Padding)
        
        self.Layout()
    
    
    ## Alias for ui.menu.PanelMenuBar.Add
    def Append(self, label, win_id=wx.ID_ANY):
        self.Add(label, win_id)
    
    
    ## Alias for ui.menu.PanelMenuBar.AddItem
    def AppendItem(self, menu, label=None):
        self.AddItem(menu, label)
    
    
    ## Find a menu within the menu bar that matches a given ID
    #  
    #  \param win_id
    #    \b \e Integer ID to scan for
    #  \return
    #    \b \e PanelMenu instance matching win_id or None
    def GetMenuById(self, win_id):
        for M in self.GetMenuList():
            if M.GetId() == win_id:
                return M
    
    
    ## Find a menu within the menu bar at given index
    #  
    #  \param index
    #    Index of item to return
    #  \return
    #    \b \e PanelMenu at menu index
    def GetMenuByIndex(self, index):
        return self.GetMenuList()[index]
    
    
    ## Find a menu within the menu bar that matches a given label
    #  
    #  \param label
    #    \b \e String label to scan for
    #  \return
    #    \b \e PanelMenu instance with matching label or None
    def GetMenuByLabel(self, label):
        for M in self.GetMenuList():
            if M.GetLabel() == label:
                return M
    
    
    ## Find the index withint the menu bar of a give item
    def GetMenuIndex(self, menu):
        if menu == None:
            return None
        
        menu_list = self.GetMenuList()
        
        for M in menu_list:
            if M == menu:
                return menu_list.index(M)
    
    
    ## Retrieve number of menus in bar
    def GetMenuCount(self):
        return len(self.GetMenuList())
    
    
    ## Retrieves a standard list of all menus in menu bar
    #  
    #  FIXME: Need a failsafe for non-PanelMenu objects???
    #  \return
    #    \b \e Tuple list of found menus
    def GetMenuList(self):
        menu_list = []
        
        # Convert wx.SizerItem to PanelMenu
        for SI in self.GetSizer().GetChildren():
            menu = SI.GetWindow()
            
            if isinstance(menu, PanelMenu):
                menu_list.append(menu)
        
        return tuple(menu_list)
    
    
    ## Action to take when menu is selected
    #  
    #  FIXME: Needs to find the menu item that was selected
    def OnSelect(self, event=None):
        if event:
            # DEBUG: Start
            print(u'DEBUGGING: PanelMenuBar.OnSelect')
            
            self.GetMenuByIndex(0).ToggleSelected()
            # DEBUG: End
