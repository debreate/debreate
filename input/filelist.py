
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module input.filelist

import os, wx

from wx.lib.mixins.listctrl import TextEditMixin

from dbr.colors       import COLOR_executable
from dbr.colors       import COLOR_link
from dbr.colors       import COLOR_warn
from dbr.language     import GT
from globals.fileitem import FileItem
from globals.strings  import IsString
from input.essential  import EssentialField
from input.list       import ListCtrl
from libdbr           import fileinfo
from libdbr.logger    import Logger


logger = Logger(__name__)

# ListCtrl report view style constants.
FL_HEADER = wx.LC_REPORT
FL_NO_HEADER = wx.LC_REPORT|wx.LC_NO_HEADER

## FileList columns.
class FileListColumns:
  Columns = range(4)
  FILENAME, SOURCE, TARGET, TYPE = Columns

  Labels = {
    FILENAME: "File",
    SOURCE: "Source Directory",
    TARGET: "Staged Target",
    TYPE: "File Type",
    }

  ## Retrieves all labels.
  #
  #  @return
  #    <b><i>String</i></b> list of column labels
  def GetAllLabels(self):
    labels = [] # sorted(self.Labels)
    # Converts to list of column indexes
    for COL in sorted(self.Labels):
      labels.append(self.Labels[COL])
    return labels

  ## Retrieves string label for column
  #
  #  @param col
  #    Column <b><i>integer</i></b> index
  #  @return
  #    <b><i>String</i></b> label of column
  def GetLabel(self, col):
    return self.Labels[col]

  ## Retrieves column index from string label.
  #
  #  @param label
  #    <b><i>String</i></b> label to search for
  #  @return
  #    <b><i>Integer</i></b> index of column, or <b><i>None</i></b>
  def GetColumnByLabel(self, label):
    for COL in self.Labels:
      if self.Labels[COL] == label:
        return COL


columns = FileListColumns()

## List control intended for managing files.
class BasicFileList(ListCtrl, TextEditMixin):
  ## Constructor
  #
  #  @param parent
  #    <b><i>wx.Window</i></b> parent instance
  #  @param winId
  #    <b><i>Integer</i></b> identifier
  #  @param hlExe
  #    If <b><i>True</i></b>, will highlight executable files with red text
  #  @param pos
  #    <b><i>wx.Window</i></b> position
  #  @param size
  #    <b><i>wx.Window</i></b> size
  #  @param style
  #    <b><i>wx.ListCtrl</i></b> style
  #  @param name
  #    <b><i>wx.Window</i></b> name attribute
  #  @param defaultValue
  #    \see fields.ifield.InputField.Default
  #  @param required
  #    \see fields.ifield.InputField.Required
  #  @param outLabel
  #    \see fields.ifield.InputField.OutputLabel
  def __init__(self, parent, winId=wx.ID_ANY, hlExe=False, pos=wx.DefaultPosition,
      size=wx.DefaultSize, style=FL_NO_HEADER, name=wx.ListCtrlNameStr,
      defaultValue=None, required=False, outLabel=None):

    ListCtrl.__init__(self, parent, winId, pos, size, style, name=name,
        defaultValue=defaultValue, required=required, outLabel=outLabel)
    TextEditMixin.__init__(self)

    # Highlights executables in red if 'True'
    self.HLExe = hlExe

    ## List of globals.fileitem.FileItem instances
    # FIXME: items in this list are out-of-order when items deleted from BaseFileList
    #        Check `BaseFileList.Delete`
    self.FileItems = []

  ## Adds new `globals.fileitem.FileItem` instance to end of list.
  #
  #  @param item
  #    Either the path to a file or a FileItem instance.
  #  @param target
  #    File's target installation directory (only if item is not FileItem instance).
  #  @return
  #    `True` if successfully added to list.
  def Add(self, item, target=None):
    return self.Insert(self.GetCount(), item, target)

  ## Appends new `globals.fileitem.FileItem` instance to end of list.
  #
  #  Alias of `input.list.BasicFileList.Add`.
  #
  #  @param item
  #    Either the path to a file or a FileItem instance.
  #  @param target
  #    File's target installation directory (only if item is not FileItem instance).
  #  @return
  #    `True` if successfully added to list.
  def Append(self, item, target=None):
    return self.Add(item, target)

  ## Deletes an item from the file list.
  #
  #  @param item
  #    Can be integer index, file path string, or FileItem instance.
  #  @return
  #    \b \e True if the file item was deleted from list.
  def Delete(self, item):
    item = self.GetIndex(item)
    filename = self.GetPath(item)
    if self.DeleteItem(item):
      self.FileItems.pop(item)
      logger.debug("Deleted item from BasicFileList: {}".format(filename))
      return True
    logger.warn("Failed to deleted item from BasicFilelist: {}".format(filename))
    return False

  ## Retrieves the basename of the file's path.
  #
  #  @param item
  #    Can be integer index, file path string, or FileItem instance.
  #  @return
  #    \b \e String representation of the filename.
  def GetBasename(self, item):
    return self.GetFileItem(item).GetBasename()

  ## Retrieves all file basenames in list.
  #
  #  @return
  #    \b \e Tuple list of string file basenames.
  def GetBasenames(self):
    basenames = []
    for FILE in self.FileItems:
      basenames.append(FILE.GetBasename())
    return tuple(basenames)

  ## Retrieves all executables.
  def GetExecutables(self, strings=True):
    exe_list = []
    for FILE in self.FileItems:
      if FILE.IsExecutable():
        if strings:
          exe_list.append(FILE.GetPath())
        else:
          exe_list.append(FILE)
    return exe_list

  ## Retrieves globals.fileitem.FileItem instance.
  #
  #  @param item
  #    Can be item index, string path, or FileItem instance.
  #  @return
  #    \b \e FileItem instance.
  def GetFileItem(self, item):
    if IsString(item):
      for FILE in self.FileItems:
        if FILE.GetPath() == item:
          item = FILE
          break
    elif isinstance(item, int):
      item = self.FileItems[item]
    if not isinstance(item, FileItem):
      logger.warn("Could not convert to FileItem: {}".format(item))
      return None
    return item

  ## Retrieves all file items
  #
  # @treturn list
  def GetFileItems(self):
    return self.FileItems

  ## Retrieves the index of given item.
  #
  #  @param item
  #    Can be \b \e FileItem instance or string representing file path
  #  @return
  #    \b \e Integer index of given item
  def GetIndex(self, item):
    item = self.GetFileItem(item)
    return self.FileItems.index(item)

  ## Retrieves full path of file.
  #
  #  @param item
  #    Can be \b \e Integer index, string path, or FileName instance.
  def GetPath(self, item):
    return self.GetFileItem(item).GetPath()

  ## Retrieves all file paths.
  def GetPaths(self):
    paths = []
    for FILE in self.FileItems:
      paths.append(FILE.GetPath())
    return tuple(paths)

  ## Retrieves target path of file.
  #
  #  @param item
  #    Can be \b \e Integer index, string path, or FileName instance.
  def GetTarget(self, item):
    return self.GetFileItem(item).GetTarget()

  ## Retrieves all target paths from files
  #
  #  @return
  #  \b \e Tuple list of all target paths
  def GetTargets(self):
    targets = []
    for FILE in self.FileItems:
      targets.append(FILE.GetTarget())
    return tuple(targets)

  ## Inserts new globals.fileitem.FileItem instance to list at given index.
  #
  #  @param index
  #    \b \e Integer index at which to insert item
  #  @param item
  #    Can be \b \e Integer index, string path, or FileName instance
  #  @param target
  #    File's target installation directory (only if item is not FileItem instance)
  #  @return
  #    \b \e True if successfully added to list
  #  @todo
  #    FIXME:
  #    - `target` not used
  #    - this is broken if `item` is not FileItem instance
  def Insert(self, index, item, target=None):
    item = self.GetFileItem(item)
    self.InsertStringItem(index, item.GetPath())
    self.FileItems.insert(index, item)
    if self.HLExe:
      self.SetItemTextColour(index, wx.RED)
    return item in self.FileItems

  ## Removes an item from the file list.
  #
  #  Alias of `input.list.BasicFileList.Delete`.
  def Remove(self, item):
    return self.Delete(item)

  ## Resets the list to default value (empty).
  def Reset(self):
    if ListCtrl.Reset(self):
      self.FileItems = []
      return True
    return False


## @todo Doxygen
class _FileDropTarget(wx.FileDropTarget):
  def __init__(self, window):
    wx.FileDropTarget.__init__(self)
    self.window = window

  ## @todo Doxygen
  def OnDropFiles(self, x, y, filename):
    self.window.OnDropFiles(filename)

## An editable list of files.
#
#  @todo
#    FIXME: use methods from BasicFileList
class FileList(BasicFileList):
  ## Constructor
  #
  #  @param parent
  #    <b><i>wx.Window</i></b> parent instance
  #  @param winId
  #    <b><i>Integer</i></b> identifier
  #  @param pos
  #    <b><i>wx.Window</i></b> position
  #  @param size
  #    <b><i>wx.Window</i></b> size
  #  @param name
  #    <b><i>wx.Window</i></b> name attribute
  #  @param defaultValue
  #    \see fields.ifield.InputField.Default
  #  @param required
  #    \see fields.ifield.InputField.Required
  #  @param outLabel
  #    \see fields.ifield.InputField.OutputLabel
  def __init__(self, parent, winId=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
      name=wx.ListCtrlNameStr, defaultValue=None, required=False, outLabel=None):

    BasicFileList.__init__(self, parent, winId, True, pos, size, style=FL_HEADER, name=name,
        defaultValue=defaultValue, required=required, outLabel=outLabel)

    dt = _FileDropTarget(parent)
    parent.SetDropTarget(dt)

    self.DEFAULT_BG_COLOR = self.GetBackgroundColour()
    self.DEFAULT_TEXT_COLOR = self.GetForegroundColour()
    self.FOLDER_TEXT_COLOR = wx.BLUE

    # FIXME: Way to do this dynamically?
    col_width = 150

    self.SetColumns(columns.GetAllLabels(), col_width)

    self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)

    # Resize bug hack
    if wx.MAJOR_VERSION == 3 and wx.MINOR_VERSION == 0:
      wx.EVT_SIZE(self, self.OnResize)

  ## @todo Doxygen
  #
  #  @param filename
  #    \b \e str : Basename of file.
  #  @param sourceDir
  #    \b \e str : Directory where file is located.
  #  @param targetDir
  #    \b \e str : Target directory where file will ultimately be installed.
  #  @param executable
  #    \b \e bool : Whether or not the file should be marked as executable.
  #  @return
  #    \b \e bool : True if file exists on the filesystem.
  def AddFile(self, filename, sourceDir, targetDir=None, executable=False):
    list_index = self.GetItemCount()

    # Method can be called with two arguments: absolute filename & target directory
    if targetDir == None:
      targetDir = sourceDir
      sourceDir = os.path.dirname(filename)
      filename = os.path.basename(filename)

    source_path = os.path.join(sourceDir, filename)
    mime_type = fileinfo.getMimeType(source_path)

    logger.debug("adding file: {} ({})".format(source_path, mime_type))

    self.InsertStringItem(list_index, filename)
    self.SetStringItem(list_index, columns.SOURCE, sourceDir)
    self.SetStringItem(list_index, columns.TARGET, targetDir)
    self.SetStringItem(list_index, columns.TYPE, mime_type)

    if os.path.islink(source_path):
      self.SetItemTextColour(list_index, COLOR_link)
    elif os.path.isdir(source_path):
      self.SetItemTextColour(list_index, self.FOLDER_TEXT_COLOR)
    else:
      # TODO: Use 'libdbr.fileinfo.getMimeType' module to determine file type
      if os.access(source_path, os.X_OK) or executable:
        self.SetFileExecutable(list_index)

      if not os.path.isfile(source_path):
        self.SetItemBackgroundColour(list_index, COLOR_warn)
        self.FileItems.insert(list_index, FileItem(source_path, targetDir))
        # File was added but does not exist on filesystem
        return False

    self.FileItems.insert(list_index, FileItem(source_path, targetDir))
    return True

  ## @todo Doxygen
  def DeleteAllItems(self):
    if ListCtrl.DeleteAllItems(self):
      self.FileItems = []
    else:
      logger.warn("Failed to delete all items from FileList")
    logger.debug("Visual item count: {}".format(self.GetItemCount()))
    logger.debug("Actual item count: {}".format(len(self.FileItems)))

  ## Retrieves the filename at given index.
  #
  #  @params index
  #    Integer row of the item.
  #  @param basename
  #    If `True`, only retrieves the file's basename.
  def GetFilename(self, index, basename=False):
    if isinstance(index, FileItem):
      index = self.GetIndex(index)
    filename = self.GetItemText(index)
    if basename:
      filename = os.path.basename(filename)
    return filename

  ## Retrieves an item's path
  def GetPath(self, index):
    file_dir = self.GetItemText(index, columns.SOURCE)
    file_name = self.GetItemText(index, columns.FILENAME)

    return os.path.join(file_dir, file_name)

  ## @todo Doxygen
  def GetRowData(self, row):
    filename = self.GetFilename(row)
    source_dir = self.GetSource(row)
    target_dir = self.GetTarget(row)
    executable = self.IsExecutable(row)
    return (filename, source_dir, target_dir, executable)

  ## @todo Doxygen
  def GetRowDefs(self, row):
    row_data = self.GetRowData(row)
    row_defs = {
      "filename": row_data[0],
      "source": row_data[1],
      "target": row_data[2],
      "executable": row_data[3],
    }
    return row_defs

  ## Retrieves the source path of a file.
  #
  #  @param row
  #    Row index of item.
  def GetSource(self, row):
    return self.GetItemText(row, columns.SOURCE)

  ## Retrieves target directory of a file.
  #
  #  @param row
  #    Row index of item.
  def GetTarget(self, row):
    if isinstance(row, FileItem):
      row = self.GetIndex(row)
    return self.GetItemText(row, columns.TARGET)

  ## Retrieves mime type of a file.
  #
  #  @param row
  #    Row index of item.
  def GetType(self, row):
    return self.GetItemText(row, columns.TYPE)

  ## Checks if an item is a directory.
  #
  #  @param row
  #    Row index of item.
  def IsDirectory(self, row):
    return os.path.isdir(self.GetPath(row))

  ## Checks if the file list is empty.
  def IsEmpty(self):
    return not self.GetItemCount()

  ## Checks if an item is executable.
  #
  #  @param row
  #    Row index of item.
  def IsExecutable(self, row):
    return self.GetItemTextColour(row) == wx.RED

  ## Checks if an item is a symbolic link.
  #
  #  @param row
  #    Row index of item.
  def IsSymlink(self, row):
    return "symlink" in self.GetType(row)

  ## @todo Doxygen
  def MissingFiles(self):
    return self.RefreshFileList()

  ## Defines actions to take when left-click or left-double-click event occurs.
  #
  #  The super method is overridden to ensure that 'event.Skip' is called.
  #  @todo
  #    Notify wxPython project of 'event.Skip' error.
  def OnLeftDown(self, event=None):
    TextEditMixin.OnLeftDown(self)
    if event:
      event.Skip()

  ## Works around resize bug in wx 3.0.
  #
  #  Uses parent width & its children to determine desired width.
  #
  #  @todo
  #    FIXME: Unknown if this bug persists in wx 3.1
  #  @todo
  #    FIXME: Do not override, should be inherited from ListCtrl
  def OnResize(self, event=None):
    if event:
      event.Skip(True)

    parent = self.GetParent()

    width = self.GetSize()
    height = width[1]
    width = width[0]

    # Use the parent window & its children to determine desired width
    target_width = parent.GetSize()[0] - parent.GetDirTreePanel().GetSize()[0] - 15

    if width > 0 and target_width > 0:
      if width != target_width:
        logger.debug(GT("File list failed to resize. Forcing manual resize to target width: {}").format(target_width))
        self.SetSize(wx.Size(target_width, height))

  ## Opens an editor for target.
  #
  #  The super method is overridden to only allow editing the "target" column.
  #
  #  @param col
  #    \b \e int : Column received from the event (replaced with "target" column).
  #  @param row
  #    \b \e int : Row index to be edited.
  def OpenEditor(self, col, row):
    TextEditMixin.OpenEditor(self, columns.TARGET, row)

  ## Refresh file list.
  #
  #  Missing files are marked with a distinct color.
  #
  #  @return
  #    \b \e bool : `True` if files are missing, `False` if all okay.
  #  @todo
  #    Update executable status.
  def RefreshFileList(self):
    dirty = False
    for row in range(self.GetItemCount()):
      item_color = self.DEFAULT_BG_COLOR
      text_color = self.DEFAULT_TEXT_COLOR
      row_defs = self.GetRowDefs(row)

      absolute_filename = "{}/{}".format(row_defs["source"], row_defs["filename"])

      if not os.path.exists(absolute_filename):
        item_color = COLOR_warn
        dirty = True

      elif os.path.isdir(absolute_filename):
        text_color = self.FOLDER_TEXT_COLOR

      elif self.IsSymlink(row):
        text_color = COLOR_link

      elif os.access(absolute_filename, os.X_OK):
        text_color = COLOR_executable

      self.SetItemTextColour(row, text_color)
      self.SetItemBackgroundColour(row, item_color)

    return dirty

  ## Removes selected files from list.
  def RemoveSelected(self):
    selected_total = self.GetSelectedItemCount()
    selected_count = selected_total

    while selected_count:
      current_selected = self.GetFirstSelected()
      if current_selected < 0:
        break

      logger.debug(GT("Removing selected item {} of {}".format(selected_total - selected_count + 1,
                                    selected_total
                                    )))

      deleted = self.DeleteItem(current_selected)
      selected_count = self.GetSelectedItemCount()

      if deleted:
        self.FileItems.pop(current_selected)
      else:
        logger.warn("Failed to delete item from Filelist: index: {}".format(current_selected))

      logger.debug("Visual item count: {}".format(self.GetItemCount()))
      logger.debug("Actual item count: {}".format(len(self.FileItems)))

  ## Selects all items in the list.
  def SelectAll(self):
    file_count = self.GetItemCount()
    for x in range(file_count):
      self.Select(x)

  ## Marks a file as executable.
  #
  #  @param row
  #    Row index of item.
  def SetFileExecutable(self, row, executable=True):
    if executable:
      self.SetItemTextColour(row, wx.RED)
      return
    self.SetItemTextColour(row, self.DEFAULT_TEXT_COLOR)

  ## Sorts listed items in target column alphabetically
  #
  #  @todo
  #    Sort listed items.
  def Sort(self):
    pass

  ## Toggles executable flag for selected list items.
  #
  #  @todo
  #    Define & execute with context menu.
  def ToggleExecutable(self):
    pass

## FileList that notifies main window to mark project dirty.
#
#  This is a dummy class to facilitate merging to & from unstable branch.
class FileListESS(FileList, EssentialField):
  ## Constructor
  #
  #  @param parent
  #    <b><i>wx.Window</i></b> parent instance
  #  @param winId
  #    <b><i>Integer</i></b> identifier
  #  @param pos
  #    <b><i>wx.Window</i></b> position
  #  @param size
  #    <b><i>wx.Window</i></b> size
  #  @param name
  #    <b><i>wx.Window</i></b> name attribute
  #  @param defaultValue
  #    \see fields.ifield.InputField.Default
  #  @param required
  #    \see fields.ifield.InputField.Required
  #  @param outLabel
  #    \see fields.ifield.InputField.OutputLabel
  def __init__(self, parent, winId=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
      name=wx.ListCtrlNameStr, defaultValue=None, required=False, outLabel=None):

    FileList.__init__(self, parent, winId, pos, size, name, defaultValue, required,
        outLabel)
    EssentialField.__init__(self)
