# -*- coding: utf-8 -*-

## \package ui.menu

# MIT licensing
# See: docs/LICENSE.txt


import wx

from ui.layout  import BoxSizer
from ui.panel   import BorderedPanel
from wiz.helper import GetMainWindow


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


## A custom menu designed for use with PanelMenuBar
class PanelMenu(wx.StaticText):
    ## Constructor
    #
    #  \param parent
    #    <b><i>wx.Window</i></b> parent instance
    #  \param winId
    #    <b><i>Integer</i></b> identifier for menu item
    #  \param label
    #    Text label displayed for menu item
    #  \param name
    #    The menu's name attribute
    def __init__(self, parent=None, winId=wx.ID_ANY, label=wx.EmptyString, name=u'menu'):
        if not parent:
            parent = GetMainWindow()
        
        wx.StaticText.__init__(self, parent, winId, label, name=name)
        
        self.fg_orig = self.GetForegroundColour()
        
        # Begin with deselected state
        self.Selected = False
        
        self.Menu = wx.Menu()
        
        # *** Event Handling *** #
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnSelect)
        
        self.Bind(wx.EVT_MENU, self.OnMenuClose)
        self.Bind(wx.EVT_MENU_CLOSE, self.OnMenuClose)
    
    
    ## Append an item the the menu
    #
    #  \param menuId
    #    Unique <b><i>integer</i></b> identifier
    #  \param label
    #    Text label displayed for menu item
    def Append(self, menuId, label):
        self.Menu.Append(menuId, label)
    
    
    ## Checks if menu is in selected state
    def IsSelected(self):
        return self.Selected
    
    
    ## Handles action to take when a menu is closed/collapsed
    def OnMenuClose(self, event=None):
        self.Select(False)
        
        if event:
            event.Skip()
    
    
    ## Passes the event to be handled by the parent instance
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
    ## Constructor
    #
    #  \param parent
    #    <b><i>wx.Window</i></b> parent instance
    #  \param winId
    #    <b><i>Integer</i></b> identifier used for menu bar
    def __init__(self, parent, winId=wx.ID_ANY, name=u'menubar'):
        BorderedPanel.__init__(self, parent, winId, name=name)
        
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
    #  \param winId
    #    <b><i>Integer</i></b> identifier to use for menu
    def Add(self, label, winId=wx.ID_ANY):
        new_menu = PanelMenu(self, winId, label)
        self.AddItem(new_menu)
    
    
    ## Add a PanelMenu instance to menu bar
    #
    #  \param menu
    #    ui.menu.PanelMenu instance to be added
    #  \param label
    #    Optional <b><i>string</i></b> label to override menu label
    def AddItem(self, menu, label=None):
        if label:
            menu.SetLabel(label)
        
        if not menu.Parent == self:
            menu.Reparent(self)
        
        lyt = self.GetSizer()
        lyt.Add(menu, 0, wx.ALL, self.Padding)
        
        self.Layout()
    
    
    ## Alias for ui.menu.PanelMenuBar.Add
    def Append(self, label, winId=wx.ID_ANY):
        self.Add(label, winId)
    
    
    ## Alias for ui.menu.PanelMenuBar.AddItem
    def AppendItem(self, menu, label=None):
        self.AddItem(menu, label)
    
    
    ## Find a menu within the menu bar that matches a given ID
    #
    #  \param winId
    #    <b><i>Integer</i></b> identifier to scan for
    #  \return
    #    ui.menu.PanelMenu instance matching winId or <b><i>None</i></b>
    def GetMenuById(self, win_id):
        for M in self.GetMenuList():
            if M.GetId() == win_id:
                return M
    
    
    ## Find a menu within the menu bar at given index
    #
    #  \param index
    #    <b><i>Integer</i></b> index of menu item to return
    #  \return
    #    <b><i>ui.menu.PanelMenu</i></b> instance at menu index
    def GetMenuByIndex(self, index):
        return self.GetMenuList()[index]
    
    
    ## Find a menu within the menu bar that matches a given label
    #
    #  \param label
    #    Text label to scan for
    #  \return
    #    ui.menu.PanelMenu instance with matching label or <b><i>None</i></b>
    def GetMenuByLabel(self, label):
        for M in self.GetMenuList():
            if M.GetLabel() == label:
                return M
    
    
    ## Find the index within the menu bar of a give item
    #
    #  \param menu
    #    The ui.menu.PanelMenu instance
    #  \return
    #    <b><i>Integer</i></b> index of panel menu
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
    #
    #  \return
    #    <b><i>Tuple</i></b> list of found menus
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
    #  TODO: Define
    def OnSelect(self, event=None):
        if event:
            # DEBUG: Start
            print(u'DEBUGGING: PanelMenuBar.OnSelect')
            
            self.GetMenuByIndex(0).ToggleSelected()
            # DEBUG: End
