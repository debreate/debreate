# -*- coding: utf-8 -*-

## \package dbr.tree

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.panel      import BorderedPanel
from globals.paths  import PATH_home


## Customized directory tree control
class DirectoryTree(wx.GenericDirCtrl):
    def __init__(self, parent, w_id=wx.ID_ANY, path=PATH_home, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DIRCTRL_3D_INTERNAL|wx.SUNKEN_BORDER,
            f_filter=wx.EmptyString, defaultFilter=0, name=wx.TreeCtrlNameStr):
        
        FORCED_STYLE = wx.DIRCTRL_EDIT_LABELS
        
        # Versions of wx older than 3.0 do not support multi-select
        if wx.MAJOR_VERSION > 2:
            FORCED_STYLE = FORCED_STYLE|wx.DIRCTRL_MULTIPLE
        
        wx.GenericDirCtrl.__init__(self, parent, w_id, path, pos, size,
                style=style|FORCED_STYLE, filter=f_filter,
                defaultFilter=defaultFilter, name=name)
    
    
    ## Retrieve all selected paths
    #  
    #  The original method doesn't seem to be working for wxPython 3.0.
    #  Does not exist for older versions.
    #  
    #  \override wx.GenericDirCtrl.GetFilePaths
    def GetFilePaths(self):
        tree = self.GetTreeCtrl()
        selected_items = tree.GetSelections()
        
        path_list = []
        
        for I in selected_items:
            tree.SelectItem(I)
            path_list.append(self.GetPath())
        
        return tuple(path_list)


## A directgory tree for legacy versions of wx
#  
#  TODO: Work-in-progress
class DirectoryTreeLegacy(BorderedPanel):
    def __init__(self, parent, w_id=wx.ID_ANY, path=PATH_home, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, name=wx.TreeCtrlNameStr):
        BorderedPanel.__init__(self, parent, w_id, pos, size, name=name)
        
        tree_ctrl = wx.TreeCtrl(self, style=wx.TR_EDIT_LABELS|wx.TR_MULTIPLE|wx.TR_HAS_BUTTONS)
        
        tree_ctrl.AddRoot(u'Home directory')
        
        self.InitDirectoryLayout()
        
        # Expand to set initial width
        tree_ctrl.ExpandAll()
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(tree_ctrl, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        tree_ctrl.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpandItem)
    
    
    ## TODO: Doxygen
    def SetDirectoryLayout(self, parent, directory=None):
        tree_ctrl = self.GetTreeCtrl()
        
        if not directory:
            self.SetDirectoryLayout(parent, PATH_home)
            return
        
        dirs = []
        files = []
        
        for I in os.listdir(directory):
            if not I.startswith(u'.'):
                path = u'{}/{}'.format(directory, I)
                
                if os.path.isdir(path) and os.access(path, os.R_OK):
                    dirs.append(I)
                
                elif os.path.isfile(path) and os.access(path, os.R_OK):
                    files.append(I)
        
        for D in sorted(dirs):
            tree_ctrl.AppendItem(parent, D)
        
        for F in sorted(files):
            tree_ctrl.AppendItem(parent, F)
    
    
    ## Retrieves wx.TreeCtrl instance
    def GetTreeCtrl(self):
        for C in self.GetChildren():
            if isinstance(C, wx.TreeCtrl):
                return C
    
    
    ## TODO: Doxygen
    def InitDirectoryLayout(self):
        tree_ctrl = self.GetTreeCtrl()
        root_item = tree_ctrl.GetRootItem()
        
        self.SetDirectoryLayout(root_item)
    
    
    ## TODO: Doxygen
    def OnExpandItem(self, event=None):
        if event:
            tree_ctrl = event.GetEventObject()
            tree_item = event.GetItem()
            
            print(u'DEBUG: Tree item type: {}'.format(type(tree_item)))
            
            if tree_item == tree_ctrl.GetRootItem():
                child = tree_ctrl.GetFirstChild(tree_item)
                while child:
                    print(u'DEBUG: Child type: {}'.format(type(child)))
                    for C in child:
                        print(u'DEBUG: Tuple item type: {}'.format(type(C)))
                    
                    if child == tree_ctrl.GetLastChild(child[0]):
                        break
                    
                    child = tree_ctrl.GetNextSibling(tree_item, child)
            
            label = event.GetLabel()
            print(u'DEBUG: Event object: {}'.format(type(tree_ctrl)))
            print(u'DEBUG: Item label: {}'.format(label))
