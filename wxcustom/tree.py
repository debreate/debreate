# -*- coding: utf-8 -*-

## \package dbr.tree

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.language       import GT
from dbr.log            import Logger
from dbr.panel          import BorderedPanel
from globals.paths      import PATH_home
from wxcustom.imagelist import sm_DirectoryImageList as ImageList


## A wxcustom tree item
#  
#  \param item
#    The \b \e wx.TreeItemId to be associated with this instance
#  \param path
#    \b \e string : The filename path to be associated with this instance
class PathItem:
    def __init__(self, item, path, label=None):
        self.Item = item
        self.Path = path
        self.Label = label
        self.Children = []
    
    
    ## TODO: Doxygen
    def AddChild(self, item):
        self.Children.append(item)
    
    
    ## TODO: Doxygen
    def ContainsInstance(self, item):
        return self.Item == item
    
    ## TODO: Doxygen
    def GetBaseItem(self):
        return self.Item
    
    
    ## TODO: Doxygen
    def GetChildren(self):
        return self.Children
    
    
    ## TODO: Doxygen
    def GetLabel(self):
        return self.Label
    
    
    ## TODO: Doxygen
    def GetPath(self):
        return self.Path
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Should return boolean
    def HasChildren(self):
        return self.Children
    
    
    ## TODO: Doxygen
    def IsDir(self):
        return os.path.isdir(self.Path)
    
    
    ## TODO: Doxygen
    def IsFile(self):
        return os.path.isfile(self.Path)
    
    
    ## TODO: Doxygen
    def RemoveChildren(self):
        self.Children = []
        
        return not self.Children
    
    
    ## TODO: Doxygen
    def SetChildren(self, items):
        self.Children = items
        
        return self.Children == items
    
    
    ## TODO: Doxygen
    def SetItem(self, item, path):
        self.Item = item
        self.Item.Path = path


## A customized directory tree that is compatible with older wx versions
#  
#  TODO: Add method GetFilePaths
#  TODO: Change icon when directory expanded/collapsed
#  TODO: Set current path when item selected
#  TODO: Add option for refreshing tree (ReCreateTree?)
class DirectoryTree(wx.TreeCtrl):
    def __init__(self, parent, w_id=wx.ID_ANY, path=PATH_home, exclude_pattern=[u'.*',],
            pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE,
            validator=wx.DefaultValidator, name=wx.TreeCtrlNameStr):
        
        wx.TreeCtrl.__init__(self, parent, w_id, pos, size,
                style=style|wx.TR_HAS_BUTTONS|wx.TR_MULTIPLE|wx.BORDER_NONE,
                validator=validator, name=name)
        
        self.AssignImageList()
        
        # FIXME: Use regular expressions
        #self.exclude_pattern = list(exclude_pattern)
        self.exclude_pattern = [u'.']
        
        self.current_path = path
        
        # NOTE: Use individual items children???
        self.item_list = []
        
        self.root_item = self.AddRoot(GT(u'Home directory'), path,
                ImageList.GetImageIndex(u'folder'))
        
        # *** Event handlers *** #
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpand)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapse)
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelect)
        
        # *** Post-layout/event actions *** #
        
        self.InitDirectoryLayout()
    
    
    ## Override inherited method to return wxcustom PathItem instances
    #  
    #  \override wx.TreeCtrl.AddRoot
    #  \param label
    #    \b \e string : Text shown on item
    #  \param path
    #    \b \e string : Path stored with item
    #  \param image
    #    \b \e ???
    #  \param selImage
    #    \b \e ???
    #  \param data
    #    \b \e
    def AddRoot(self, label, path, image=-1, selImage=-1, data=None):
        root_item = PathItem(wx.TreeCtrl.AddRoot(self, label, image, selImage, data), path, label)
        
        self.SetItemHasChildren(root_item)
        
        self.item_list.append(root_item)
        
        return root_item
    
    
    ## Override inherited method to return wxcustom PathItem instances
    def AppendItem(self, parent, label, path, image=-1, selImage=-1, data=None):
        base_item = wx.TreeCtrl.AppendItem(self, parent.GetBaseItem(), label, image, selImage, data)
        tree_item = PathItem(base_item, path, label)
        
        if os.path.isdir(path):
            # ???: Does this cause PathItem instance to be overwritten with wx.TreeItemId ...
            #      or other errors?
            self.SetItemHasChildren(tree_item)
        
        self.item_list.append(tree_item)
        
        return tree_item
    
    
    ## Make sure image list cannot be changed
    def AssignImageList(self):
        return wx.TreeCtrl.AssignImageList(self, ImageList)
    
    
    ## Override inherited method to avoid TypeError
    def Collapse(self, item):
        return wx.TreeCtrl.Collapse(self, item.GetBaseItem())
    
    
    ## Override inherited method to delete item & base item
    #  
    #  TODO: Test if PathItem is actually removed from memory
    def Delete(self, item):
        deleted = wx.TreeCtrl.Delete(self, item.GetBaseItem())
        
        item_index = 0
        for I in self.item_list:
            if I == item:
                break
            
            item_index += 1
        
        self.item_list.pop(item_index)
        del item
        
        return deleted
    
    
    ## Overrides inherited method to not delete root item & clear item list
    #  
    #  FIXME: Need to make sure PathItem instances are removed from memory
    def DeleteAllItems(self):
        self.DeleteChildren(self.root_item.GetBaseItem())
        self.root_item.RemoveChildren()
        
        # ???: Redundant
        for I in reversed(self.item_list):
            del I
        
        self.item_list = []
    
    
    ## Override inherited method so children are filled out
    #  
    #  NOTE: Only items representing directories should expand
    #  FIXME: Change icon when expanded/collapsed
    def Expand(self, item):
        if item.IsFile():
            return False
        
        dirs = []
        files = []
        
        if not self.ItemHasChildren(item):
            # FIXME: Should use regular expressions for filter
            item_path = item.GetPath()
            for LABEL in os.listdir(item_path):
                # Ignore filtered items
                filtered = False
                for FILTER in self.exclude_pattern:
                    if LABEL.startswith(FILTER):
                        filtered = True
                        break
                
                if not filtered:
                    child_path = u'{}/{}'.format(item_path, LABEL)
                    
                    if os.path.isdir(child_path) and os.access(child_path, os.R_OK):
                        dirs.append((LABEL, child_path,))
                    
                    elif os.path.isfile(child_path) and os.access(child_path, os.R_OK):
                        files.append((LABEL, child_path,))
            
            # Sort directories first
            for DIR, PATH in sorted(dirs):
                item.AddChild(self.AppendItem(item, DIR, PATH, ImageList.GetImageIndex(u'folder')))
            
            for FILE, PATH in sorted(files):
                item.AddChild(self.AppendItem(item, FILE, PATH, ImageList.GetImageIndex(u'file')))
        
        return wx.TreeCtrl.Expand(self, item.GetBaseItem())
    
    
    ## TODO: Doxygen
    def GetAllItems(self):
        return tuple(self.item_list)
    
    
    ## Override to ensure return value of DirectoryImageList instance
    def GetImageList(self):
        #return wx.TreeCtrl.GetImageList(self)
        
        return ImageList
    
    
    ## TODO: Doxygen
    def GetItemParent(self, item):
        base_item = None
        if not isinstance(item, PathItem):
            base_item = item
            
            for I in self.item_list:
                if I.GetBaseItem() == base_item:
                    item = I
        
        else:
            base_item = item.GetBaseItem()
        
        if item == self.root_item:
            # Root item does not have parent
            return None
        
        parent = wx.TreeCtrl.GetItemParent(self, base_item)
        
        for I in self.item_list:
            if I.GetBaseItem() == parent:
                parent = I
                break
        
        return parent
    
    
    ## Get the path of an item
    def GetItemPath(self, item):
        return item.GetPath()
    
    
    ## TODO: Doxygen
    def GetPath(self):
        return self.current_path
    
    
    ## Override inherited method to retrieve wxcustom root item with 'Path' attribute
    def GetRootItem(self):
        return self.root_item
    
    
    ## Retrieve paths of all selected tree items
    #  
    #  TODO: Define method
    def GetSelectedPaths(self):
        selected = self.GetSelections()
        paths = []
        
        for S in selected:
            paths.append(S.GetPath())
        
        return tuple(paths)
    
    
    ## Get selected item
    #  
    #  \override wx.TreeCtrl.GetSelection
    def GetSelection(self):
        # wx 3.0 does not allow use of GetSelection with TR_MULTIPLE flag
        if wx.MAJOR_VERSION <= 2:
            base_selected = wx.TreeCtrl.GetSelection(self)
        
            for ITEM in self.item_list:
                if ITEM.GetBaseItem() == base_selected:
                    return ITEM
        
        else:
            selected = self.GetSelections()
            
            # Just use previous selection
            if len(selected) > 1:
                for I in self.item_list:
                    if I.Path == self.current_path:
                        return I
            
            elif selected:
                return selected[0]
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Define
    def GetSelections(self):
        base_selected = wx.TreeCtrl.GetSelections(self)
        selected = []
        
        for BASE in base_selected:
            for ITEM in self.item_list:
                if ITEM.GetBaseItem() == BASE:
                    selected.append(ITEM)
        
        return tuple(selected)
    
    
    ## TODO: Doxygen
    def InitDirectoryLayout(self):
        root_item = self.GetRootItem()
        
        # Don't call self.Expand directly
        self.OnExpand(item=root_item)
    
    
    ## TODO: Doxygen
    def IsExpanded(self, item):
        if isinstance(item, PathItem):
            item = item.GetBaseItem()
        
        return wx.TreeCtrl.IsExpanded(self, item)
    
    
    ## Override inherited method to extract base item
    def ItemHasChildren(self, item):
        # NOTE: HasChildren method returns a list ...
        #       Should return a boolean
        return item.HasChildren()
    
    
    ## TODO: Doxygen
    def OnCollapse(self, event=None, item=None):
        if event:
            item = event.GetItem()
            
            event.Veto()
            
            for ITEM in self.GetAllItems():
                if ITEM.ContainsInstance(item):
                    item = ITEM
                    break
            
            if not isinstance(item, PathItem):
                return False
        
        if item == None:
            return False
        
        return self.Collapse(item)
    
    
    ## TODO: Doxygen
    def OnExpand(self, event=None, item=None):
        if event:
            item = event.GetItem()
            
            event.Veto()
            
            for ITEM in self.GetAllItems():
                if ITEM.ContainsInstance(item):
                    item = ITEM
                    break
            
            if not isinstance(item, PathItem):
                return False
        
        if item == None:
            return False
        
        return self.Expand(item)
    
    
    ## Sets the current path to the newly selected item's path
    #  
    #  FIXME: Behavior is different between wx 2.8 & 3.0.
    #         2.8 behavior is preferred.
    def OnSelect(self, event=None):
        selected = self.GetSelection()
        
        if selected:
            if selected.Path != self.current_path:
                self.SetPath(selected.Path)
        
        if event:
            event.Skip()
    
    
    ## Refreshes the tree's displayed layout
    def ReCreateTree(self):
        selected = self.GetSelection()
        selected_path = selected.Path
        expanded = self.IsExpanded(selected)
        
        self.DeleteAllItems()
        
        # Recreate tree
        self.InitDirectoryLayout()
        
        # DEBUG: Checking if selected still in memory
        if selected:
            Logger.Debug(__name__, u'Selected still in memory')
        
        else:
            Logger.Debug(__name__, u'Selected NOT in memory')
        
        Logger.Debug(__name__, u'Selected path: {}'.format(selected_path))
        
        #selected_path = selected_path.replace(self.root_item.Path, u'').strip(u'/').split(u'/')
        
        #Logger.Debug(__name__, u'Selected path: {}'.format(selected_path))
        
        for I in self.item_list:
            if I.Path == selected_path:
                if expanded:
                    self.Expand(I)
                
                break
            
            elif I.Path in selected_path:
                self.Expand(I)
    
    
    ## Make sure image list cannot be changed
    def SetImageList(self):
        return wx.TreeCtrl.SetImageList(self, ImageList)
    
    
    ## TODO: Doxygen
    def SetItemHasChildren(self, item, has_children=True):
        return wx.TreeCtrl.SetItemHasChildren(self, item.GetBaseItem(), has_children)
    
    
    ## Sets the currently selected path
    #  
    #  \param path
    #    \b \e string : New path to be set
    def SetPath(self, path):
        self.current_path = path


## Directory tree with a nicer border
class DirectoryTreePanel(BorderedPanel):
    def __init__(self, parent, w_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.TAB_TRAVERSAL, name=u'DirTreePnl'):
        BorderedPanel.__init__(self, parent, w_id, pos, size, style, name)
        
        self.DirTree = DirectoryTree(self)
        
        # Give easy access of instance to parent
        parent.DirTree = self.DirTree
        
        # *** Layout *** #
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.DirTree, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Retrieve DirectoryTree instance so methods can be called from within other objects
    def GetDirectoryTree(self):
        return self.DirTree
