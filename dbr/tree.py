# -*- coding: utf-8 -*-

## \package dbr.tree

# MIT licensing
# See: docs/LICENSE.txt


import os, traceback, wx

from dbr.colors             import COLOR_executable
from dbr.colors             import COLOR_warn
from dbr.dialogs            import ConfirmationDialog
from dbr.dialogs            import ShowErrorDialog
from dbr.functions          import MouseInsideWindow
from dbr.image              import GetCursor
from dbr.imagelist          import sm_DirectoryImageList as ImageList
from dbr.language           import GT
from dbr.log                import Logger
from dbr.panel              import BorderedPanel
from globals                import ident
from globals.commands       import CMD_trash
from globals.commands       import ExecuteCommand
from globals.devices        import GetMountedStorageDevices
from globals.mime           import GetFileMimeType
from globals.paths          import ConcatPaths
from globals.paths          import PATH_home
from globals.wizardhelper   import GetTopWindow


## A wxcustom tree item
#  
#  \param item
#    The \b \e wx.TreeItemId to be associated with this instance
#  \param path
#    \b \e string : The filename path to be associated with this instance
class PathItem:
    def __init__(self, item, path, label=None):
        if path == None:
            # So that calls to os.path.exists(PathItem.Path) do not raise exception
            path = wx.EmptyString
        
        self.Item = item
        self.Path = path
        self.Label = label
        self.Children = []
        self.Type = None
        
        if self.Path:
            self.Type = GetFileMimeType(self.Path)
            
            executables_binary = (
                u'x-executable',
                )
            
            executables_text = (
                u'x-python',
                u'x-shellscript',
                )
            
            # Don't use MIME type 'inode' for directories (symlinks are inodes)
            if os.path.isdir(self.Path):
                self.Type = u'folder'
            
            elif self.Type.startswith(u'image'):
                self.Type = u'image'
            
            elif self.Type.startswith(u'audio'):
                self.Type = u'audio'
            
            elif self.Type.startswith(u'video'):
                self.Type = u'video'
            
            else:
                # Exctract second part of MIME type
                self.Type = self.Type.split(u'/')[-1]
                
                if self.Type in executables_binary:
                    self.Type = u'executable-binary'
                
                elif self.Type in executables_text:
                    self.Type = u'executable-script'
            
            self.ImageIndex = ImageList.GetImageIndex(self.Type)
            
            # Use generic 'file' image as default
            if self.ImageIndex == ImageList.GetImageIndex(u'failsafe'):
                self.ImageIndex = ImageList.GetImageIndex(u'file')
            
            Logger.Debug(__name__, u'PathItem type: {} ({})'.format(self.Type, self.Path))
    
    
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
        
        self.root_item = self.AddRoot(GT(u'System'), ImageList.GetImageIndex(u'computer'))
        
        self.COLOR_default = self.GetItemBackgroundColour(self.root_item)
        
        # List of sub-root items that shouldn't be deleted if they exist on filesystem
        # FIXME: Should not need to use a root list now with GetDeviceMountPoints function
        self.root_list = []
        
        # Failsafe conditional in case of errors reading user home directory
        home_exists = os.path.isdir(PATH_home)
        if home_exists:
            self.root_home = self.AppendItem(self.root_item, GT(u'Home directory'), PATH_home,
                    ImageList.GetImageIndex(u'folder-home'),
                    expImage=ImageList.GetImageIndex(u'folder-home-open'))
            
            self.root_list.append(self.root_home)
        
        # List storage devices currently mounted on system
        stdevs = GetMountedStorageDevices()
        
        for DEV in stdevs:
            add_item = os.path.ismount(DEV.MountPoint)
            
            if add_item:
                for PITEM in self.root_list:
                    if DEV.MountPoint == PITEM.Path:
                        add_item = False
                        break
            
            if add_item:
                Logger.Debug(__name__, u'Adding new sub-root PathItem instance: {}'.format(DEV.Label))
                
                self.root_list.append(self.AppendItem(self.root_item, DEV.Label, DEV.MountPoint,
                        ImageList.GetImageIndex(DEV.Type)))
                continue
            
            else:
                Logger.Debug(__name__, u'PathItem instance for "{}" directory already exists'.format(DEV.MountPoint))
        
        self.ctx_menu = wx.Menu()
        
        mitm_add = wx.MenuItem(self.ctx_menu, wx.ID_ADD, GT(u'Add to project'))
        mitm_expand = wx.MenuItem(self.ctx_menu, ident.EXPAND, GT(u'Expand'))
        mitm_rename = wx.MenuItem(self.ctx_menu, ident.RENAME, GT(u'Rename'))
        mitm_refresh = wx.MenuItem(self.ctx_menu, wx.ID_REFRESH, GT(u'Refresh'))
        
        self.ctx_menu.AppendItem(mitm_add)
        self.ctx_menu.AppendItem(mitm_expand)
        self.ctx_menu.AppendItem(mitm_rename)
        self.ctx_menu.AppendSeparator()
        self.ctx_menu.AppendItem(mitm_refresh)
        
        if CMD_trash:
            mitm_delete = wx.MenuItem(self.ctx_menu, wx.ID_DELETE, GT(u'Trash'))
            self.ctx_menu.InsertItem(2, mitm_delete)
        
        # Tells app if user is currently dragging an item from tree
        self.dragging = False
        
        # *** Event handlers *** #
        
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        wx.EVT_KEY_DOWN(self, self.OnDoubleClick)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpand)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapse)
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelect)
        
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
        wx.EVT_MENU(self, ident.EXPAND, self.OnMenuSelect)
        wx.EVT_MENU(self, ident.RENAME, self.OnMenuSelect)
        wx.EVT_MENU(self, wx.ID_DELETE, self.OnMenuSelect)
        wx.EVT_MENU(self, wx.ID_REFRESH, self.OnRefresh)
        
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndLabelEdit)
        
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragBegin)
        self.Bind(wx.EVT_LEFT_UP, self.OnDragEnd)
        
        # *** Post-layout/event actions *** #
        
        # Expand the user's home directory
        if home_exists:
            self.InitDirectoryLayout()
    
    
    ## Override inherited method to return custom PathItem instances
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
    def AddRoot(self, label, image=-1, selImage=-1, data=None):
        root_item = wx.TreeCtrl.AddRoot(self, label, image, selImage, data)
        
        # Root item should always have children unless errors found on filesystem
        self.SetItemHasChildren(root_item)
        
        return root_item
    
    
    ## Override inherited method to return custom PathItem instances
    def AppendItem(self, parent, label, path, image=-1, selImage=-1, expImage=-1, data=None):
        if isinstance(parent, PathItem):
            parent = parent.GetBaseItem()
        
        base_item = wx.TreeCtrl.AppendItem(self, parent, label, image, selImage, data)
        
        if expImage >= 0:
            self.SetItemImage(base_item, expImage, wx.TreeItemIcon_Expanded)
        
        tree_item = PathItem(base_item, path, label)
        
        if os.path.isdir(path):
            # ???: Does this cause PathItem instance to be overwritten with wx.TreeItemId ...
            #      or other errors?
            self.SetItemHasChildren(tree_item)
        
        elif os.access(path, os.X_OK):
            self.SetItemTextColour(base_item, COLOR_executable)
        
        self.item_list.append(tree_item)
        
        return tree_item
    
    
    ## Make sure image list cannot be changed
    def AssignImageList(self):
        return wx.TreeCtrl.AssignImageList(self, ImageList)
    
    
    ## Override inherited method to avoid TypeError
    def Collapse(self, item):
        if isinstance(item, PathItem):
            item = item.GetBaseItem()
        
        return wx.TreeCtrl.Collapse(self, item)
    
    
    ## Override inherited method to delete item & base item
    #  
    #  TODO: Test if PathItem is actually removed from memory
    def Delete(self, item):
        Logger.Debug(__name__, u'Deleting item type: {}'.format(type(item)))
        
        if item:
            deleted = wx.TreeCtrl.Delete(self, item.GetBaseItem())
            
            item_index = 0
            for I in self.item_list:
                if I == item:
                    break
                
                item_index += 1
            
            # Delete children of deleted item
            if self.item_list[item_index].HasChildren():
                pass
            
            self.item_list.pop(item_index)
            del item
            
            return deleted
    
    
    ## Overrides inherited method to not delete root item & clear item list
    #  
    #  FIXME: Need to make sure PathItem instances are removed from memory
    def DeleteAllItems(self):
        for I in self.root_list:
            if isinstance(I, PathItem):
                self.DeleteChildren(I.GetBaseItem())
                I.RemoveChildren()
            
            else:
                self.DeleteChildren(I)
        
        # ???: Redundant
        for I in reversed(self.item_list):
            del I
        
        # Reset item list to only contain sub-root items
        self.item_list = list(self.root_list)
    
    
    ## Delete the listed items
    def DeleteItems(self, item_list):
        # FIXME: App crashes when trying to delete child of item already deleted
        for I in item_list:
            self.Delete(I)
    
    
    ## Override inherited method so children are filled out
    #  
    #  NOTE: Only items representing directories should expand
    #  FIXME: Change icon when expanded/collapsed
    def Expand(self, item):
        if isinstance(item, PathItem):
            if item.IsFile():
                return False
            
            dirs = []
            files = []
            
            if not self.ItemHasChildren(item):
                # FIXME: Should use regular expressions for filter
                item_path = item.GetPath()
                
                try:
                    for LABEL in os.listdir(item_path):
                        # Ignore filtered items
                        filtered = False
                        for FILTER in self.exclude_pattern:
                            if LABEL.startswith(FILTER):
                                filtered = True
                                break
                        
                        if not filtered:
                            child_path = ConcatPaths((item_path, LABEL))
                            
                            if os.path.isdir(child_path) and os.access(child_path, os.R_OK):
                                dirs.append((LABEL, child_path,))
                            
                            elif os.path.isfile(child_path) and os.access(child_path, os.R_OK):
                                files.append((LABEL, child_path,))
                    
                    # Sort directories first
                    for DIR, PATH in sorted(dirs):
                        child = self.AppendItem(item, DIR, PATH)
                        self.SetItemImage(child, ImageList.GetImageIndex(u'folder'), wx.TreeItemIcon_Normal)
                        self.SetItemImage(child, ImageList.GetImageIndex(u'folder-open'), wx.TreeItemIcon_Expanded)
                        
                        item.AddChild(child)
                    
                    for FILE, PATH in sorted(files):
                        child = self.AppendItem(item, FILE, PATH)
                        self.SetItemImage(child, child.ImageIndex, wx.TreeItemIcon_Normal)
                        
                        item.AddChild(child)
                
                except OSError:
                    Logger.Warning(__name__, u'No such file or directory: {}'.format(item_path))
        
        # Recursively expand parent items
        parent = self.GetItemParent(item)
        if parent:
            self.Expand(parent)
        
        if isinstance(item, PathItem):
            item = item.GetBaseItem()
        
        return wx.TreeCtrl.Expand(self, item)
    
    
    ## TODO: Doxygen
    def GetAllItems(self):
        return tuple(self.item_list)
    
    
    ## Override to ensure return value of DirectoryImageList instance
    def GetImageList(self):
        #return wx.TreeCtrl.GetImageList(self)
        
        return ImageList
    
    
    ## TODO: Doxygen
    def GetItemParent(self, item):
        if isinstance(item, wx.TreeItemId) and item == self.root_item:
            # Root item does not have parent
            return None
        
        if isinstance(item, PathItem):
            item = item.GetBaseItem()
        
        parent = wx.TreeCtrl.GetItemParent(self, item)
        
        # Root item is not in item list
        if parent == self.root_item:
            return parent
        
        # Convert to PathItem
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
            # Ensure that all selected items are PathItem instances
            if isinstance(S, PathItem):
                paths.append(S.Path)
        
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
        
        # Return root item if it is only thing selected
        if len(base_selected) == 1 and self.root_item in base_selected:
            return tuple(base_selected)
        
        selected = []
        
        # Convert wx.TreeItemId instances to PathItem.
        # Also omits any selected items that are not PathItem instances.
        for BASE in base_selected:
            for ITEM in self.item_list:
                if ITEM.GetBaseItem() == BASE:
                    selected.append(ITEM)
        
        return tuple(selected)
    
    
    ## Expands the user's home directory
    def InitDirectoryLayout(self):
        # Don't call self.Expand directly
        self.OnExpand(item=self.root_home)
    
    
    ## TODO: Doxygen
    def IsExpanded(self, item):
        if isinstance(item, PathItem):
            item = item.GetBaseItem()
        
        return wx.TreeCtrl.IsExpanded(self, item)
    
    
    ## Override inherited method to extract base item
    def ItemHasChildren(self, item):
        # Root item should always have children
        if isinstance(item, wx.TreeItemId) and item == self.root_item:
            return True
        
        # FIXME: HasChildren method returns a list ...
        #        Should return a boolean
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
    
    
    ## Open a context menu for manipulating tree files & directories
    def OnContextMenu(self, event=None):
        removed_expand = None
        
        allow_rename = True
        allow_trash = True
        
        selected = self.GetSelections()
        
        if len(selected) > 1:
            allow_rename = False
            # REMOVEME: App crashes when deleting child & parent paths.
            #           Disabled for multiple items until fixed.
            allow_trash = False
            
            removed_expand = self.ctx_menu.Remove(ident.EXPAND)
        
        elif isinstance(selected[0], PathItem) and selected[0].Type != u'folder':
            removed_expand = self.ctx_menu.Remove(ident.EXPAND)
        
        elif selected:
            # Set expand menu item label dependent on item state
            if self.IsExpanded(selected[0]):
                self.ctx_menu.SetLabel(ident.EXPAND, GT(u'Collapse'))
            
            else:
                self.ctx_menu.SetLabel(ident.EXPAND, GT(u'Expand'))
            
            if isinstance(selected[0], wx.TreeItemId) and selected[0] == self.root_item:
                Logger.Debug(__name__, u'Root item selected')
                
                # Only allow expand/collapse & refresh for root item
                removed_menus = []
                for MENU_ID in (wx.ID_ADD, None, ident.RENAME, wx.ID_DELETE):
                    if not MENU_ID:
                        removed_menus.append(None)
                    
                    else:
                        removed_menus.append(self.ctx_menu.Remove(MENU_ID))
                
                self.PopupMenu(self.ctx_menu)
                
                for INDEX in range(len(removed_menus)):
                    menu = removed_menus[INDEX]
                    if menu:
                        self.ctx_menu.InsertItem(INDEX, menu)
                
                return
        
        if selected:
            for ITEM in self.root_list:
                if ITEM in selected:
                    allow_rename = False
                    allow_trash = False
                    break
            
            self.ctx_menu.Enable(ident.RENAME, allow_rename)
            self.ctx_menu.Enable(wx.ID_DELETE, allow_trash)
            
            self.PopupMenu(self.ctx_menu)
            
            # Re-enable expand menu item
            if removed_expand:
                self.ctx_menu.InsertItem(1, removed_expand)
        
        else:
            Logger.Debug(__name__, u'No items were selected')
    
    
    ## TODO: Doxygen
    def OnDoubleClick(self, event=None):
        if event and isinstance(event, wx.KeyEvent):
            # Allow double-click behavior for return & enter keys
            if event.GetKeyCode() not in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER,):
                event.Skip()
                return
        
        selected = list(self.GetSelections())
        
        if selected:
            if len(selected) == 1 and (self.ItemHasChildren(selected[0]) or os.path.isdir(selected[0].Path)):
                selected = selected[0]
                
                # Normally we could just call event.Skip() here which executes default
                # double-click behavior of expanding directories. However, in order to
                # allow keyboard events the same behavior we must explicitly call
                # self.Expand or self.Collapse.
                if self.IsExpanded(selected):
                    self.Collapse(selected)
                
                else:
                    self.Expand(selected)
            
            else:
                # FIXME: Better method?
                self.Parent.Parent.OnImportFromTree()
                
                # Return focus to tree for keyboard control
                self.SetFocus()
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: File list does not receive EVT_ENTER_WINDOW during drag
    def OnDragBegin(self, event=None):
        if event:
            event.Allow()
            
            self.dragging = True
            
            Logger.Debug(__name__, u'Dragging!!!')
            
            # Show a 'dragging' cursor
            self.UpdateCursor()
            
            # Skipping drag event & using mouse release event for drop looks better
            event.Skip()
    
    
    ## TODO: Doxygen
    #  
    # FIXME: Should send event to Files page???
    def OnDragEnd(self, event=None):
        if event and self.dragging:
            self.dragging = False
            
            # Reset cursor to default
            self.UpdateCursor(True)
            
            target_window = self.Parent.Parent.GetListInstance()
            dropped = MouseInsideWindow(target_window)
            
            Logger.Debug(__name__, u'Dropped inside file list: {}'.format(dropped))
            
            if dropped:
                self.Parent.Parent.OnImportFromTree()
            
            # WARNING: Skipping event causes selection to change in directory tree
            #          if multiple items selected.
            #event.Skip()
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Paths can use forward slashes if a directory exists to move item into.
    #         Tree does not update to show that the item has been moved.
    def OnEndLabelEdit(self, event=None):
        if event:
            if event.IsEditCancelled():
                Logger.Debug(__name__, u'Vetoing due to cancelled edit')
                
                event.Veto()
                return
            
            item = event.GetItem()
            for I in self.item_list:
                if I.GetBaseItem() == item:
                    item = I
                    break
            
            new_label = event.GetLabel()
            item_dir = os.path.dirname(item.Path)
            new_path = ConcatPaths((item_dir, new_label))
            
            try:
                if os.path.exists(new_path):
                    msg_l1 = GT(u'Name already exists:')
                    ShowErrorDialog(u'{}\n\n{}'.format(msg_l1, new_path))
                    
                    event.Veto()
                    return
                
                os.rename(item.Path, new_path)
                
                ## ???: Another way to test if rename was successful?
                if os.path.exists(new_path):
                    # Items path must be updated
                    I.Path = new_path
            
            except OSError:
                Logger.Debug(__name__, u'Item not renamed, traceback details below:\n\n{}'.format(traceback.format_exc()))
                
                event.Veto()
            
            Logger.Debug(__name__, u'New item path: {}'.format(item.Path))
    
    
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
    
    
    ## Catch mouse left down event for custom selection behavior
    #  
    #  Resets selection to only currently selected item if modifiers are not present.
    #  This behavior is not present by default if the newly selected item was
    #  previously selected.
    def OnLeftDown(self, event=None):
        if event and isinstance(event, wx.MouseEvent):
            modifiers = event.ControlDown() or event.ShiftDown()
            if not modifiers and len(self.GetSelections()) > 1:
                self.ResetSelected()
            
            event.Skip()
    
    
    ## Actions for menu events
    def OnMenuSelect(self, event=None):
        if event:
            event_id = event.GetId()
            
            if event_id == ident.EXPAND:
                selection = self.GetSelection()
                if self.IsExpanded(selection):
                    self.Collapse(selection)
                
                else:
                    self.Expand(selection)
            
            elif event_id == ident.RENAME:
                selected = self.GetSelection()
                self.EditLabel(selected.GetBaseItem())
            
            elif event_id == wx.ID_DELETE:
                selected = self.GetSelections()
                self.SendToTrash(selected)
    
    
    ## Catches menu event to refresh/recreate tree
    def OnRefresh(self, event=None):
        self.ReCreateTree()
    
    
    ## Sets the current path to the newly selected item's path
    #  
    #  FIXME: Behavior is different between wx 2.8 & 3.0.
    #         2.8 behavior is preferred.
    def OnSelect(self, event=None):
        selected = self.GetSelection()
        
        if isinstance(selected, PathItem):
            base_item = selected.GetBaseItem()
            
            if selected.Path != self.current_path:
                self.SetPath(selected.Path)
            
            if not os.path.exists(selected.Path):
                self.SetItemBackgroundColour(base_item, COLOR_warn)
            
            elif self.GetItemBackgroundColour(base_item) == COLOR_warn:
                self.SetItemBackgroundColour(base_item, self.COLOR_default)
        
        if event:
            event.Skip()
    
    
    ## Refreshes the tree's displayed layout
    #  
    #  FIXME: Should rescan /dev for new or removed devices
    def ReCreateTree(self):
        selected = self.GetSelection()
        
        if isinstance(selected, PathItem):
            selected_path = selected.Path
            expanded = self.IsExpanded(selected)
        
        else:
            selected_path = PATH_home
            expanded = True
        
        self.DeleteAllItems()
        
        # Recreate tree
        self.InitDirectoryLayout()
        
        Logger.Debug(__name__, u'Selected path: {}'.format(selected_path))
        
        for I in self.item_list:
            if I.Path == selected_path:
                if expanded:
                    self.Expand(I)
                
                break
            
            elif I.Path in selected_path:
                self.Expand(I)
    
    
    ## Clears all selected items except latest selected
    def ResetSelected(self):
        selected = self.GetSelection()
        if selected:
            self.UnselectAll()
            
            if isinstance(selected, PathItem):
                selected = selected.GetBaseItem()
            
            self.SelectItem(selected)
    
    
    ## Send that selected item's path to trash
    def SendToTrash(self, item_list):
        path_list = []
        for I in item_list:
            if not os.access(I.Path, os.W_OK):
                ShowErrorDialog(GT(u'Cannot move "{}" to trash, no write access').format(I.Path),
                        warn=True)
                
                return False
            
            path_list.append(I.Path)
        
        msg_l1 = GT(u'Move the following items to trash?')
        msg_l2 = u'\n'.join(path_list)
        if ConfirmationDialog(GetTopWindow(), GT(u'Delete'),
                u'{}\n\n{}'.format(msg_l1, msg_l2)).Confirmed():
            
            arg_list = list(path_list)
            # Use 'force' argument to avoid crash on non-existing paths
            arg_list.insert(0, u'-f')
            ExecuteCommand(CMD_trash, arg_list)
            
            Logger.Debug(__name__, u'Paths deleted')
            
            self.DeleteItems(item_list)
            
            Logger.Debug(__name__, u'Items deleted')
            
            # Confirm that paths were removed
            for P in path_list:
                if os.path.exists(P):
                    Logger.Debug(__name__, u'Failed to remove "{}"'.format(P))
                    
                    return False
            
            Logger.Debug(__name__, u'Items successfully moved to trash')
            
            return True
        
        return False
    
    
    ## Make sure image list cannot be changed
    def SetImageList(self):
        return wx.TreeCtrl.SetImageList(self, ImageList)
    
    
    ## TODO: Doxygen
    def SetItemHasChildren(self, item, has_children=True):
        if isinstance(item, PathItem):
            item = item.GetBaseItem()
        
        return wx.TreeCtrl.SetItemHasChildren(self, item, has_children)
    
    
    ## Override inherited method to extract wx.TreeItemId instance
    #  
    #  \param item
    #    \b \e PathItem or \b \e wx.TreeItemId instance
    #  \param image_index
    #    Image \b \e integer index to set for item
    #  \param state
    #    Item state for which to use image
    def SetItemImage(self, item, image_index, state):
        if isinstance(item, PathItem):
            item = item.GetBaseItem()
        
        return wx.TreeCtrl.SetItemImage(self, item, image_index, state)
    
    
    ## Sets the currently selected path
    #  
    #  \param path
    #    \b \e string : New path to be set
    def SetPath(self, path):
        self.current_path = path
    
    
    ## Sets the visible cursor on the Files page dependent on drag-&-drop state
    #  
    #  FIXME: Does not work for wx 2.8
    #  \param reset
    #    \b \e bool : Resets cursor back to default if True
    def UpdateCursor(self, reset=False):
        try:
            if reset:
                wx.SetCursor(wx.NullCursor)
                return
            
            new_cursor = u'drag-file'
            for I in self.GetSelections():
                if os.path.isdir(I.Path):
                    new_cursor = u'drag-folder'
                    break
            
            wx.SetCursor(GetCursor(new_cursor, 24))
        
        except TypeError:
            err_l1 = GT(u'Failed to set cursor')
            err_l2 = GT(u'Details below:')
            Logger.Error(__name__, u'\n    {}\n    {}\n\n{}'.format(err_l1, err_l2, traceback.format_exc()))


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
