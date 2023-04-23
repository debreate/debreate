
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.tree

import os
import traceback

import wx

import libdbr.bin
import ui.app

from dbr.colors        import COLOR_executable
from dbr.colors        import COLOR_link
from dbr.colors        import COLOR_warn
from dbr.functions     import MouseInsideWindow
from dbr.image         import GetCursor
from dbr.imagelist     import sm_DirectoryImageList as ImageList
from dbr.language      import GT
from globals.devices   import GetMountedStorageDevices
from libdbr            import fileinfo
from libdbr            import paths
from libdbr.logger     import Logger
from libdebreate.ident import menuid
from ui.dialog         import ConfirmationDialog
from ui.dialog         import ShowErrorDialog
from ui.layout         import BoxSizer
from ui.panel          import BorderedPanel


logger = Logger(__name__)

## A wxcustom tree item.
#
#  @param item
#    The \b \e wx.TreeItemId to be associated with this instance
#  @param path
#    \b \e string : The filename path to be associated with this instance
class PathItem:
  def __init__(self, item, path, label=None):
    if path == None:
      # So that calls to os.path.exists(PathItem.Path) do not raise exception
      path = wx.EmptyString

    self.Item = item
    self.Path = paths.normalize(path, strict=True)
    self.Label = label
    self.Children = []
    self.Type = ""

    if self.Path:
      self.Type = fileinfo.getMimeType(self.Path)

      executables_binary = (
        "x-executable",
        )

      executables_text = (
        "x-python",
        "x-shellscript",
        )

      # Don't use MIME type 'inode' for directories (symlinks are inodes)
      if os.path.isdir(self.Path):
        self.Type = "folder"

      elif self.Type.startswith("image"):
        self.Type = "image"

      elif self.Type.startswith("audio"):
        self.Type = "audio"

      elif self.Type.startswith("video"):
        self.Type = "video"

      else:
        # Extract second part of MIME type
        self.Type = self.Type.split("/")[-1]

        if self.Type in executables_binary:
          self.Type = "executable-binary"

        elif self.Type in executables_text:
          self.Type = "executable-script"

      self.ImageIndex = ImageList.GetImageIndex(self.Type)

      # Use generic 'file' image as default
      if self.ImageIndex == ImageList.GetImageIndex("failsafe"):
        self.ImageIndex = ImageList.GetImageIndex("file")

      logger.debug("PathItem type: {} ({})".format(self.Type, self.Path))

  ## @todo Doxygen
  def AddChild(self, item):
    self.Children.append(item)

  ## @todo Doxygen
  def ContainsInstance(self, item):
    return self.Item == item

  ## @todo Doxygen
  def GetBaseItem(self):
    return self.Item

  ## @todo Doxygen
  def GetChildren(self):
    return self.Children

  ## @todo Doxygen
  def GetLabel(self):
    return self.Label

  ## @todo Doxygen
  def GetPath(self):
    return self.Path

  ## @todo Doxygen
  #  @todo FIXME: Should return boolean
  def HasChildren(self):
    return self.Children

  ## Checks if this is a child of another PathItem instance
  #
  #  @param item
  #    \b \e PathItem instance to check against
  #  @return
  #    `True` if self instance found in item children
  def IsChildOf(self, item):
    for CHILD in item.Children:
      if CHILD == self:
        return True

    return False

  ## @todo Doxygen
  def IsDir(self):
    return os.path.isdir(self.Path)

  ## @todo Doxygen
  def IsFile(self):
    return os.path.isfile(self.Path)

  ## @todo Doxygen
  def RemoveChildren(self):
    self.Children = []

    return not self.Children

  ## @todo Doxygen
  def SetChildren(self, items):
    self.Children = items

    return self.Children == items

  ## @todo Doxygen
  def SetItem(self, item, path):
    self.Item = item
    self.Item.Path = paths.normalize(path, strict=True)


## @todo Doxygen
class DirectoryTree(wx.GenericDirCtrl):
  def __init__(self, parent, id=wx.ID_ANY, path=paths.getUserHome()):
    super().__init__(parent, id, path, style=wx.DIRCTRL_DEFAULT_STYLE|wx.DIRCTRL_MULTIPLE)

    self.callbacks = {}
    # FIXME: not platform independent
    self.cmd_trash = paths.getExecutable("gio")
    self.ctx_menu = wx.Menu()

    mitm_add = wx.MenuItem(self.ctx_menu, wx.ID_ADD, GT("Add to project"))
    self.mitm_expand = wx.MenuItem(self.ctx_menu, menuid.EXPAND, GT("Expand"))
    self.mitm_collapse = wx.MenuItem(self.ctx_menu, menuid.COLLAPSE, GT("Collapse"))
    mitm_rename = wx.MenuItem(self.ctx_menu, menuid.RENAME, GT("Rename"))
    mitm_togglehidden = wx.MenuItem(self.ctx_menu, menuid.TOGGLEHIDDEN, GT("Show Hidden"),
        kind=wx.ITEM_CHECK)
    mitm_refresh = wx.MenuItem(self.ctx_menu, wx.ID_REFRESH, GT("Refresh"))

    self.ctx_menu.Append(mitm_add)
    self.ctx_menu.Append(mitm_rename)
    if self.cmd_trash:
      self.ctx_menu.Append(wx.MenuItem(self.ctx_menu, wx.ID_DELETE, GT("Trash")))
    self.ctx_menu.AppendSeparator()
    self.ctx_menu.Append(mitm_togglehidden)
    self.ctx_menu.Append(mitm_refresh)

    self.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
    self.Bind(wx.EVT_MENU, self.onExpand, id=menuid.EXPAND)
    self.Bind(wx.EVT_MENU, self.onExpand, id=menuid.COLLAPSE)
    self.Bind(wx.EVT_MENU, self.onRename, id=menuid.RENAME)
    self.Bind(wx.EVT_MENU, self.onToggleHidden, id=menuid.TOGGLEHIDDEN)
    self.Bind(wx.EVT_MENU, self.onRefresh, id=wx.ID_REFRESH)
    if self.cmd_trash:
      self.Bind(wx.EVT_MENU, self.onTrash, id=wx.ID_DELETE)

    tree = self.GetTreeCtrl()

    # add items via context menu
    self.Bind(wx.EVT_MENU, self.onAddSelection, id=wx.ID_ADD)
    # double-click files to add to project
    tree.Bind(wx.EVT_LEFT_DCLICK, self.onAddSelection)
    # add items via drag-and-drop
    tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onDragStart)
    # ~ self.Bind(wx.EVT_TREE_END_DRAG, self.onDragEnd)
    # workaround because wx.EVT_TREE_END_DRAG doesn't work
    tree.Bind(wx.EVT_LEFT_UP, self.onDragEnd)
    self.dragging = False

    # drop target window
    self.drop_target = None

  ## Opens the context menu.
  def onContextMenu(self, evt):
    logger.debug("context menu activated")
    expanding = False
    tree = self.GetTreeCtrl()
    for sel in tree.GetSelections():
      if not tree.IsExpanded(sel):
        expanding = True
        break
    if expanding:
      self.ctx_menu.Insert(1, self.mitm_expand)
    else:
      self.ctx_menu.Insert(1, self.mitm_collapse)
    self.PopupMenu(self.ctx_menu)
    self.ctx_menu.Remove(self.ctx_menu.FindItemByPosition(1))

  ## Expands the selected nodes in the directory tree.
  def onExpand(self, evt):
    expanding = evt.GetId() != menuid.COLLAPSE
    tree = self.GetTreeCtrl()
    selections = tree.GetSelections()
    if selections:
      for sel in selections:
        tree.Expand(sel) if expanding else tree.Collapse(sel)

  ## Marks selected label for editing.
  def onRename(self, evt):
    tree = self.GetTreeCtrl()
    selections = tree.GetSelections()
    if len(selections) == 0:
      return
    tree.EditLabel(selections[0])

  ## Toggles visibility of hidden files.
  def onToggleHidden(self, evt):
    self.ShowHidden(self.ctx_menu.FindItemById(menuid.TOGGLEHIDDEN).IsChecked())

  ## Reloads directory tree.
  def onRefresh(self, evt):
    # remember selection
    paths = self.GetPaths()
    self.ReCreateTree()
    self.UnselectAll()
    if len(paths) > 0:
      self.ExpandPath(paths[0])

  ## Executes the "on_add" callback group.
  def onAddSelection(self, evt):
    if type(evt) == wx.MouseEvent:
      path = self.GetPath()
      if os.path.isdir(path) or not os.path.lexists(path):
        evt.Skip()
        return
      logger.debug("adding file via double-click: {}".format(path))
    if "on_add" in self.callbacks:
      for func in self.callbacks["on_add"]:
        func()

  ## Handles actions when an item is dragged.
  def onDragStart(self, evt):
    logger.debug("file drag start")
    evt.Allow()
    self.dragging = True
    # Show a 'dragging' cursor
    self.updateCursor()
    # Skipping drag event & using mouse release event for drop looks better
    evt.Skip()

  ## Handles actions when a dragged item is released.
  def onDragEnd(self, evt):
    if not self.dragging:
      evt.Skip()
      return
    logger.debug("file drag end")
    # Reset cursor to default
    self.updateCursor(True)
    self.dragging = False
    if not self.drop_target:
      return
    on_target = MouseInsideWindow(self.drop_target)
    logger.debug("Dropped inside file list: {}".format(on_target))
    if on_target:
      self.onAddSelection(None)

    # WARNING: Skipping event causes selection to change in directory tree
    #  	  if multiple items selected.
    #event.Skip()

  ## Adds a callback function to be triggered on special events.
  #
  #  @param group
  #    Callback group.
  #  @param func
  #    Function to execute with group.
  def addCallback(self, group, func):
    if group not in self.callbacks:
      self.callbacks[group] = []
    self.callbacks[group].append(func)

  ## Sets the visible cursor on the Files page dependent on drag-&-drop state
  #
  #  @param reset
  #    \b \e bool : Resets cursor back to default if True
  def updateCursor(self, reset=False):
    try:
      if reset:
        wx.SetCursor(wx.NullCursor)
        return

      new_cursor = "drag-file"
      for path in self.GetPaths():
        if os.path.isdir(path):
          new_cursor = "drag-folder"
          break

      wx.SetCursor(GetCursor(new_cursor, 24))

    except TypeError:
      err_l1 = GT("Failed to set cursor")
      err_l2 = GT("Details below:")
      logger.error("\n	{}\n	{}\n\n{}".format(err_l1, err_l2, traceback.format_exc()))

  ## Moves selected items to trash.
  def onTrash(self, evt):
    paths = self.GetPaths()
    logger.debug("trashing files: {}".format(paths))
    dia = ConfirmationDialog(self, text=GT("Move {} items to trash?").format(len(paths)))
    if dia.ShowModal() != wx.ID_OK:
      return
    if libdbr.bin.trash(paths) != 0:
      logger.error("failed to trash some files: {}".format(paths))
    self.onRefresh(None)


## A customized directory tree that is compatible with older wx versions
#
#  @todo
#    - Add method GetFilePaths
#    - Change icon when directory expanded/collapsed
#    - Set current path when item selected
#    - Add option for refreshing tree (ReCreateTree?)
class _DirectoryTree(wx.TreeCtrl):
  def __init__(self, parent, w_id=wx.ID_ANY, path=paths.getUserHome(), exclude_pattern=[".*",],
      pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE,
      validator=wx.DefaultValidator, name=wx.TreeCtrlNameStr):

    wx.TreeCtrl.__init__(self, parent, w_id, pos, size,
        style=style|wx.TR_HAS_BUTTONS|wx.TR_MULTIPLE|wx.BORDER_NONE,
        validator=validator, name=name)

    logger.deprecated(_DirectoryTree, alt=wx.GenericDirCtrl)

    self.AssignImageList()

    # FIXME: Use regular expressions
    #self.exclude_pattern = list(exclude_pattern)
    self.exclude_pattern = ["."]

    self.current_path = paths.normalize(path, strict=True)

    # NOTE: Use individual items children???
    self.item_list = []

    self.root_item = self.AddRoot(GT("System"), ImageList.GetImageIndex("computer"))

    self.COLOR_default = self.GetItemBackgroundColour(self.root_item)

    # List of sub-root items that shouldn't be deleted if they exist on filesystem
    # FIXME: Should not need to use a root list now with GetDeviceMountPoints function
    self.mount_list = []

    self.ctx_menu = wx.Menu()

    mitm_add = wx.MenuItem(self.ctx_menu, wx.ID_ADD, GT("Add to project"))
    mitm_expand = wx.MenuItem(self.ctx_menu, menuid.EXPAND, GT("Expand"))
    mitm_rename = wx.MenuItem(self.ctx_menu, menuid.RENAME, GT("Rename"))
    mitm_togglehidden = wx.MenuItem(self.ctx_menu, menuid.TOGGLEHIDDEN, GT("Show Hidden"),
        kind=wx.ITEM_CHECK)
    mitm_refresh = wx.MenuItem(self.ctx_menu, wx.ID_REFRESH, GT("Refresh"))

    self.ctx_menu.Append(mitm_add)
    self.ctx_menu.Append(mitm_expand)
    self.ctx_menu.Append(mitm_rename)
    self.ctx_menu.AppendSeparator()
    self.ctx_menu.Append(mitm_togglehidden)
    self.ctx_menu.Append(mitm_refresh)

    # FIXME: Hack
    self.trash = False

    if paths.getExecutable("gvfs-trash"):
      mitm_delete = wx.MenuItem(self.ctx_menu, wx.ID_DELETE, GT("Trash"))
      self.ctx_menu.InsertItem(2, mitm_delete)
      self.trash = True

    # Tells app if user is currently dragging an item from tree
    self.dragging = False

    # *** Event handlers *** #

    self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
    self.Bind(wx.EVT_KEY_DOWN, self.OnDoubleClick)
    self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

    self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpand)
    self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapse)

    self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelect)

    self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    self.Bind(wx.EVT_MENU, self.OnMenuSelect, id=menuid.EXPAND)
    self.Bind(wx.EVT_MENU, self.OnMenuSelect, id=menuid.RENAME)
    self.Bind(wx.EVT_MENU, self.OnMenuSelect, id=wx.ID_DELETE)
    self.Bind(wx.EVT_MENU, self.OnRefresh, id=menuid.TOGGLEHIDDEN)
    self.Bind(wx.EVT_MENU, self.OnRefresh, id=wx.ID_REFRESH)

    self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndLabelEdit)

    self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragBegin)
    self.Bind(wx.EVT_LEFT_UP, self.OnDragEnd)

    # *** Post-layout/event actions *** #

    self.InitMountItems()

    # Expand the user's home directory
    if self.GetHomeItem():
      self.InitDirectoryLayout()

  ## Override inherited method to return custom PathItem instances
  #
  #  @param label
  #    \b \e string : Text shown on item
  #  @param path
  #    \b \e string : Path stored with item
  #  @param image
  #    \b \e ???
  #  @param selImage
  #    \b \e ???
  #  @param data
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
      #    or other errors?
      self.SetItemHasChildren(tree_item)
    elif os.access(path, os.X_OK):
      self.SetItemTextColour(base_item, COLOR_executable)

    if os.path.islink(path):
      self.SetItemTextColour(base_item, COLOR_link)

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
  #  @todo Test if PathItem is actually removed from memory
  def Delete(self, item):
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

  ## Overrides inherited method to not delete everything but root item
  #
  #  FIXME: Need to make sure PathItem instances are removed from memory
  def DeleteAllItems(self):
    self.DeleteChildren(self.root_item)

    # ???: Redundant
    for I in reversed(self.item_list):
      del I

    for I in reversed(self.mount_list):
      del I

    # Reset item lists
    self.item_list = []
    self.mount_list = []

  ## Delete the listed items
  def DeleteItems(self, item_list):
    # Reversing the sorted list guarantees child objects will be deleted
    # before parents & prevents app crashing.
    item_list = sorted(item_list, key=PathItem.GetPath, reverse=True)
    for ITEM in item_list:
      self.Delete(ITEM)

  ## Override inherited method so children are filled out
  #
  #  NOTE: Only items representing directories should expand
  #
  #  @todo FIXME: Change icon when expanded/collapsed
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
              if FILTER == "." and self.IsHiddenShown():
                pass
              elif LABEL.startswith(FILTER):
                filtered = True
                break

            if not filtered:
              child_path = os.path.join(item_path, LABEL)

              if os.path.isdir(child_path) and os.access(child_path, os.R_OK):
                dirs.append((LABEL, child_path,))

              elif os.path.isfile(child_path) and os.access(child_path, os.R_OK):
                files.append((LABEL, child_path,))

          # Sort directories first
          for DIR, PATH in sorted(dirs):
            child = self.AppendItem(item, DIR, PATH)
            self.SetItemImage(child, ImageList.GetImageIndex("folder"), wx.TreeItemIcon_Normal)
            self.SetItemImage(child, ImageList.GetImageIndex("folder-open"), wx.TreeItemIcon_Expanded)

            item.AddChild(child)

          for FILE, PATH in sorted(files):
            child = self.AppendItem(item, FILE, PATH)
            self.SetItemImage(child, child.ImageIndex, wx.TreeItemIcon_Normal)

            item.AddChild(child)

        except OSError:
          logger.warn("No such file or directory: {}".format(item_path))

    # Recursively expand parent items
    parent = self.GetItemParent(item)
    if parent:
      self.Expand(parent)

    base_item = item
    if isinstance(item, PathItem):
      if not item.HasChildren():
        logger.warn("path '{}' does not have children".format(item.GetPath()))
        return True
      base_item = item.GetBaseItem()

    # FIXME: broken on Windows
    if not base_item.IsOk():
      logger.error("'PathItem' ({}) is corrupted".format(item.GetPath()))
      return False
    return wx.TreeCtrl.Expand(self, base_item)
    # ~ return True

  ## Expands a mounted item all the way down path
  #
  #  @param mount_item
  #    Mounted \b \e PathItem to be expanded
  #  @param path
  #    Path to follow
  def ExpandPath(self, mount_item, path):
    self.Expand(mount_item)

    children = self.GetItemChildren(mount_item)
    while children:
      in_path = False

      for CHILD in children:
        in_path = CHILD.Path in path
        if in_path:
          logger.debug("Expanding path: {}".format(CHILD.Path))

          self.Expand(CHILD)
          children = self.GetItemChildren(CHILD)
          break

      if not in_path:
        break

  ## @todo Doxygen
  def GetAllItems(self):
    return tuple(self.item_list)

  ## Retrieve the item that represents user's home directory
  #
  #  Should always be first item in root list
  def GetHomeItem(self):
    dir_home = paths.getUserHome()
    if self.mount_list:
      for ITEM in self.mount_list:
        if ITEM.Path == dir_home:
          return ITEM

    return None

  ## Retrieves all children for an item
  def GetItemChildren(self, item):
    if not isinstance(item, PathItem):
      return list()

    return item.Children

  ## Override to ensure return value of DirectoryImageList instance
  def GetImageList(self):
    #return wx.TreeCtrl.GetImageList(self)

    return ImageList

  ## @todo Doxygen
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

  ## @todo Doxygen
  def GetPath(self):
    return self.current_path

  ## Override inherited method to retrieve wxcustom root item with 'Path' attribute
  def GetRootItem(self):
    return self.root_item

  ## Retrieves the parent mount item for current selection
  def GetSelectedMountItem(self):
    mount_item = self.GetSelection()

    if isinstance(mount_item, PathItem) and mount_item in self.mount_list:
      return mount_item

    if mount_item:
      parent = self.GetItemParent(mount_item)

      # Root item should be only instance that is not PathItem
      while isinstance(parent, PathItem):
        if parent in self.mount_list:
          return parent
        parent = self.GetItemParent(parent)

    # FIXME: Should return home item if mount item is None???
    return None

  ## Retrieve paths of all selected tree items
  #
  #  @todo Define method
  def GetSelectedPaths(self):
    selected = self.GetSelections()
    s_paths = []
    for S in selected:
      # Ensure that all selected items are PathItem instances
      if isinstance(S, PathItem):
        s_paths.append(S.Path)
    return tuple(s_paths)

  ## Get selected item
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

  ## @todo Doxygen
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
    if self.mount_list:
      # Don't call self.Expand directly
      self.OnExpand(item=self.GetHomeItem())

  ## Creates all mount items for tree
  def InitMountItems(self):
    # Failsafe conditional in case of errors reading user home directory
    dir_home = paths.getUserHome()
    home_exists = os.path.isdir(dir_home)
    if home_exists:
      home_item = self.AppendItem(self.root_item, GT("Home directory"), dir_home,
          ImageList.GetImageIndex("folder-home"),
          expImage=ImageList.GetImageIndex("folder-home-open"))

      self.mount_list.append(home_item)

    # List storage devices currently mounted on system
    stdevs = GetMountedStorageDevices()

    for DEV in stdevs:
      # Do not re-add home directory in case it is mounted on its own partition
      if DEV.MountPoint == dir_home:
        continue

      add_item = os.path.ismount(DEV.MountPoint)
      if add_item:
        for PITEM in self.mount_list:
          if DEV.MountPoint == PITEM.Path:
            add_item = False
            break

      if add_item:
        logger.debug("Adding new mount PathItem instance: {}".format(DEV.Label))
        self.mount_list.append(self.AppendItem(self.root_item, DEV.Label, DEV.MountPoint,
            ImageList.GetImageIndex(DEV.Type)))
        continue
      else:
        logger.debug("PathItem instance for \"{}\" directory already exists".format(DEV.MountPoint))

  ## @todo Doxygen
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
    #  	Should return a boolean
    return item.HasChildren()

  ## @todo Doxygen
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
      for ITEM in selected:
        if ITEM.Type != "folder":
          removed_expand = self.ctx_menu.Remove(menuid.EXPAND)
          break
    elif isinstance(selected[0], PathItem) and selected[0].Type != "folder":
      removed_expand = self.ctx_menu.Remove(menuid.EXPAND)
    elif selected and isinstance(selected[0], wx.TreeItemId) and selected[0] == self.root_item:
      logger.debug("Root item selected")
      # Only allow expand/collapse & refresh for root item
      removed_menus = []
      menu_ids = [wx.ID_ADD, None, menuid.RENAME,]
      if self.trash:
        menu_ids.append(wx.ID_DELETE)

      for MENU_ID in menu_ids:
        # None inserted into removed menus instead of trying to remember menu indexes
        if not MENU_ID:
          removed_menus.append(None)
        else:
          removed_menus.append(self.ctx_menu.Remove(MENU_ID))

      expand_label = GT("Collapse")
      if not self.IsExpanded(self.root_item):
        expand_label= GT("Expand")

      self.ctx_menu.SetLabel(menuid.EXPAND, expand_label)

      self.PopupMenu(self.ctx_menu)

      for INDEX in range(len(removed_menus)):
        menu = removed_menus[INDEX]
        if menu:
          self.ctx_menu.InsertItem(INDEX, menu)
      return

    if selected:
      # Should only have to worry about changing label if all selected
      # items are directories.
      if not removed_expand:
        # Set expand menu item label dependent on item state
        expand_label = GT("Collapse")
        for ITEM in selected:
          if not self.IsExpanded(ITEM):
            expand_label = GT("Expand")
            break

        self.ctx_menu.SetLabel(menuid.EXPAND, expand_label)

      for ITEM in self.mount_list:
        if ITEM in selected:
          allow_rename = False
          allow_trash = False
          break

      self.ctx_menu.Enable(menuid.RENAME, allow_rename)

      if self.trash:
        self.ctx_menu.Enable(wx.ID_DELETE, allow_trash)

      self.PopupMenu(self.ctx_menu)

      # Re-enable expand menu item
      if removed_expand:
        self.ctx_menu.InsertItem(1, removed_expand)
    else:
      logger.debug("No items were selected")

  ## @todo Doxygen
  def OnDoubleClick(self, event=None):
    mouse_event = False
    key_event = False

    if event:
      mouse_event = isinstance(event, wx.MouseEvent)
      key_event = isinstance(event, wx.KeyEvent)

    if key_event:
      # Allow double-click behavior for return & enter keys only
      if event.GetKeyCode() not in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER,):
        event.Skip()
        return

    selected = list(self.GetSelections())
    if selected:
      if len(selected) == 1 and (self.ItemHasChildren(selected[0]) or os.path.isdir(selected[0].Path)):
        selected = selected[0]
        # Use default behavior for double-click mouse event
        if mouse_event:
          event.Skip()
        else:
          if self.IsExpanded(selected):
            self.Collapse(selected)
          else:
            self.Expand(selected)
      else:
        # FIXME: Better method?
        self.GetParent().GetParent().OnImportFromTree()
        # Return focus to tree for keyboard control
        self.SetFocus()

  ## @todo Doxygen
  #  @todo FIXME: File list does not receive EVT_ENTER_WINDOW during drag
  def OnDragBegin(self, event=None):
    if event:
      event.Allow()
      self.dragging = True
      logger.debug("Dragging!!!")
      # Show a 'dragging' cursor
      self.UpdateCursor()
      # Skipping drag event & using mouse release event for drop looks better
      event.Skip()

  ## @todo Doxygen
  #  @todo
  #    FIXME: Should send event to Files page???
  def OnDragEnd(self, event=None):
    if event and self.dragging:
      self.dragging = False

      # Reset cursor to default
      self.UpdateCursor(True)

      target_window = self.GetParent().GetParent().GetListInstance()
      dropped = MouseInsideWindow(target_window)

      logger.debug("Dropped inside file list: {}".format(dropped))

      if dropped:
        self.GetParent().GetParent().OnImportFromTree()

      # WARNING: Skipping event causes selection to change in directory tree
      #  	  if multiple items selected.
      #event.Skip()

  ## @todo Doxygen
  #  @todo
  #    FIXME: Paths can use forward slashes if a directory exists to move item into. Tree does not
  #    update to show that the item has been moved.
  def OnEndLabelEdit(self, event=None):
    if event:
      if event.IsEditCancelled():
        logger.debug("Vetoing due to cancelled edit")
        event.Veto()
        return

      item = event.GetItem()
      for I in self.item_list:
        if I.GetBaseItem() == item:
          item = I
          break

      new_label = event.GetLabel()
      item_dir = os.path.dirname(item.Path)
      new_path = os.path.join(item_dir, new_label)

      try:
        if os.path.exists(new_path):
          msg_l1 = GT("Name already exists:")
          ShowErrorDialog("{}\n\n{}".format(msg_l1, new_path))
          event.Veto()
          return
        os.rename(item.Path, new_path)

        ## ???: Another way to test if rename was successful?
        if os.path.exists(new_path):
          # Items path must be updated
          I.Path = new_path
      except OSError:
        logger.debug("Item not renamed, traceback details below:\n\n{}".format(traceback.format_exc()))
        event.Veto()
      logger.debug("New item path: {}".format(item.Path))

  ## @todo Doxygen
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
      if event_id == menuid.EXPAND:
        expand = event.GetEventObject().GetLabel(menuid.EXPAND).lower() == "expand"
        selected = self.GetSelections()
        if expand:
          for ITEM in selected:
            self.Expand(ITEM)
        else:
          for ITEM in selected:
            self.Collapse(ITEM)
      elif event_id == menuid.RENAME:
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
  #  @todo
  #    FIXME: Behavior is different between wx 2.8 & 3.0. 2.8 behavior is preferred.
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

  ## Checks menu item state
  def IsHiddenShown(self):
    return self.ctx_menu.FindItemById(menuid.TOGGLEHIDDEN).IsChecked()

  ## Refreshes the tree's displayed layout
  def ReCreateTree(self):
    selected = self.GetSelection()
    mount_path = None

    if selected:
      # Get the current mount item's path for re-expanding
      mount_item = self.GetSelectedMountItem()
      if isinstance(mount_item, PathItem):
        mount_path = mount_item.Path

      if isinstance(selected, PathItem):
        selected_path = selected.Path
        expanded = self.IsExpanded(selected)
      else:
        selected_path = paths.getUserHome()
        expanded = True

      logger.debug("Selected path: {}".format(selected_path))

    self.DeleteAllItems()

    # Refresh list of connected storage devices
    self.InitMountItems()

    if selected and mount_path:
      mount_item = None

      for MOUNT in self.mount_list:
        if MOUNT.Path == mount_path:
          mount_item = MOUNT
          break

      if mount_item:
        if mount_item.Path == selected_path:
          if expanded:
            self.Expand(mount_item)
        elif expanded:
          self.ExpandPath(mount_item, selected_path)
        else:
          self.ExpandPath(mount_item, os.path.dirname(selected_path))

  ## Clears all selected items except latest selected
  def ResetSelected(self):
    selected = self.GetSelection()
    if selected:
      self.UnselectAll()
      if isinstance(selected, PathItem):
        selected = selected.GetBaseItem()
      self.SelectItem(selected)

  ## Send that selected item's path to trash
  #
  #  @todo
  #    FIXME: not platform independent
  def SendToTrash(self, item_list):
    path_list = []
    for I in item_list:
      if not os.access(I.Path, os.W_OK):
        ShowErrorDialog(GT("Cannot move \"{}\" to trash, no write access").format(I.Path),
            warn=True)
        return False
      path_list.append(I.Path)

    msg_l1 = GT("Move the following items to trash?")
    msg_l2 = "\n".join(path_list)
    if ConfirmationDialog(ui.app.getMainWindow(), GT("Delete"),
        "{}\n\n{}".format(msg_l1, msg_l2)).Confirmed():

      arg_list = list(path_list)
      # Use 'force' argument to avoid crash on non-existing paths
      arg_list.insert(0, "-f")
      libdbr.bin.execute(paths.getExecutable("gvfs-trash"), arg_list)

      logger.debug("Paths deleted")

      self.DeleteItems(item_list)

      logger.debug("Items deleted")

      # Confirm that paths were removed
      for P in path_list:
        if os.path.exists(P):
          logger.debug("Failed to remove \"{}\"".format(P))
          return False
      logger.debug("Items successfully moved to trash")
      return True
    return False

  ## Make sure image list cannot be changed
  #
  #  @param _faux
  #    Unused parameter in case called with an attempt to change image list.
  def SetImageList(self, _dummy=None):
    return wx.TreeCtrl.SetImageList(self, ImageList)

  ## @todo Doxygen
  def SetItemHasChildren(self, item, has_children=True):
    if isinstance(item, PathItem):
      item = item.GetBaseItem()

    return wx.TreeCtrl.SetItemHasChildren(self, item, has_children)

  ## Override inherited method to extract wx.TreeItemId instance
  #
  #  @param item
  #    \b \e PathItem or \b \e wx.TreeItemId instance
  #  @param image_index
  #    Image \b \e integer index to set for item
  #  @param state
  #    Item state for which to use image
  def SetItemImage(self, item, image_index, state):
    if isinstance(item, PathItem):
      item = item.GetBaseItem()

    return wx.TreeCtrl.SetItemImage(self, item, image_index, state)

  ## Sets the currently selected path
  #
  #  @param path
  #    \b \e string : New path to be set
  def SetPath(self, path):
    self.current_path = paths.normalize(path, strict=True)

  ## Sets the visible cursor on the Files page dependent on drag-&-drop state
  #
  #  @param reset
  #    \b \e bool : Resets cursor back to default if True
  def UpdateCursor(self, reset=False):
    try:
      if reset:
        wx.SetCursor(wx.NullCursor)
        return

      new_cursor = "drag-file"
      for I in self.GetSelections():
        if os.path.isdir(I.Path):
          new_cursor = "drag-folder"
          break

      wx.SetCursor(GetCursor(new_cursor, 24))

    except TypeError:
      err_l1 = GT("Failed to set cursor")
      err_l2 = GT("Details below:")
      logger.error("\n	{}\n	{}\n\n{}".format(err_l1, err_l2, traceback.format_exc()))

## Directory tree with a nicer border
class DirectoryTreePanel(BorderedPanel):
  def __init__(self, parent, w_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
      style=wx.TAB_TRAVERSAL, name="DirTreePnl"):
    BorderedPanel.__init__(self, parent, w_id, pos, size, style, name)

    # ~ self.DirTree = DirectoryTree(self)
    self.DirTree = None

    # Give easy access of instance to parent
    # ~ parent.DirTree = self.DirTree

    # *** Layout *** #

    # ~ layout = BoxSizer(wx.VERTICAL)

    # ~ lyt_main = BoxSizer(wx.VERTICAL)
    # ~ lyt_main.Add(self.DirTree, 1, wx.EXPAND)

    self.SetAutoLayout(True)
    self.SetSizer(BoxSizer(wx.VERTICAL))
    self.Layout()

  ## Retrieve DirectoryTree instance so methods can be called from within other objects
  def GetDirectoryTree(self):
    logger.deprecated(self.GetDirectoryTree, alt=self.getTree)# "DirectoryTreePanel.getTree")

    return self.getTree()

  ## Retrieves the directory tree.
  #
  #  @return
  #    `DirectoryTree` instance.
  def getTree(self):
    return self.DirTree

  ## Sets directory tree for this panel.
  #
  #  @param tree
  #    `DirectoryTree` instance to use.
  def setTree(self, tree):
    sizer = self.GetSizer()
    old_tree = self.getTree()
    if old_tree == None:
      sizer.Add(tree, 1, wx.EXPAND)
    else:
      sizer.Replace(old_tree, tree)
      old_tree.Destroy()
    self.DirTree = tree
    self.Layout()
