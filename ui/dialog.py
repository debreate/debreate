
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.dialog

import os

import wx

import ui.app

from dbr.language         import GT
from dbr.workingdir       import ChangeWorkingDirectory
from globals.bitmaps      import ICON_ERROR
from globals.bitmaps      import ICON_EXCLAMATION
from globals.bitmaps      import ICON_INFORMATION
from globals.bitmaps      import ICON_QUESTION
from globals.project      import project_wildcards
from globals.project      import supported_suffixes
from input.select         import ComboBox
from input.text           import TextAreaPanel
from libdbr               import strings
from libdbr.logger        import Logger
from ui.button            import AddCustomButtons
from ui.button            import ButtonSizer
from ui.button            import GetButtonSizer
from ui.hyperlink         import Hyperlink
from ui.layout            import BoxSizer
from ui.style             import layout as lyt


logger = Logger(__name__)

## An abstract class defining method to manipulate button labels
class ButtonDialog:
  ## Changes the label of buttons of a given ID
  #
  #  @param btnId
  #  \b \e Integer ID of buttons to change labels
  #  @param newLabel
  #  New \b \e string label for button
  #  @return
  #  Value of ui.button.ButtonSizer.SetLabel or \b \e False
  def SetButtonLabel(self, btnId, newLabel):
    btn_sizer = GetButtonSizer(self)
    if isinstance(btn_sizer, ButtonSizer):
      return btn_sizer.SetLabel(btnId, newLabel)
    return False


## A base dialog class
#
#  Differences from wx.Dialog:
#  * Border is always resizable.
#  * Centers on parent when ShowModal is called.
class BaseDialog(wx.Dialog):
  def __init__(self, parent=None, ID=wx.ID_ANY, title=GT("Title"), pos=wx.DefaultPosition,
        size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr):
    if parent == None:
      parent = ui.app.getMainWindow()

    wx.Dialog.__init__(self, parent, ID, title, pos, size, style|wx.RESIZE_BORDER, name)

  ## Centers on parent then shows dialog in modal form
  def ShowModal(self):
    if self.GetParent():
      self.CenterOnParent()
    return wx.Dialog.ShowModal(self)

## @todo Doxygen
class StandardDirDialog(wx.DirDialog):
  def __init__(self, parent, title, style=wx.DD_DEFAULT_STYLE):

    # Setting os.getcwd() causes dialog to always be opened in working directory
    wx.DirDialog.__init__(self, parent, title, os.getcwd(),
        style=style|wx.DD_DIR_MUST_EXIST|wx.DD_NEW_DIR_BUTTON|wx.DD_CHANGE_DIR)

    # FIXME: Find inherited bound event
    self.Bind(wx.EVT_BUTTON, self.OnAccept)

    self.CenterOnParent()

  ## @todo Doxygen
  def OnAccept(self, event=None):
    path = self.GetPath()
    if os.path.isdir(path):
      self.EndModal(wx.ID_OK)
      return
    logger.debug("Path is not a directory: {}".format(path))

## A standard system file dialog modified for advanced use
class StandardFileDialog(wx.FileDialog):
  def __init__(self, parent, title="Choose a file", defaultDir=None, defaultFile="",
      defaultExt=None, wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE,
      pos=wx.DefaultPosition, size=wx.DefaultSize, name="filedlg"):

    if not defaultDir:
      defaultDir = os.getcwd()

    # Setting os.getcwd() causes dialog to always be opened in working directory
    wx.FileDialog.__init__(self, parent, title, defaultDir, defaultFile, wildcard, style, pos)

    self.SetSize(size)
    self.SetName(name)
    self.Extension = defaultExt

    if self.WindowStyleFlag & wx.FD_SAVE:
      self.Bind(wx.EVT_BUTTON, self.OnAccept, id=self.AffirmativeId)

      if self.WindowStyleFlag & wx.FD_CHANGE_DIR:
        logger.warn("Found FD_CHANGE_DIR style, could conflict with OnAccept method")

    self.CenterOnParent()

  ## @todo Doxygen
  def GetExtension(self):
    return self.Extension

  ## @todo Doxygen
  def HasExtension(self, path):
    if "." in path:
      if path.split(".")[-1] != "":
        return True
    return False

  ## Checks if dialog is using FD_SAVE style
  def IsSaveDialog(self):
    return self.WindowStyleFlag & wx.FD_SAVE

  ## @todo Doxygen
  def OnAccept(self, event=None):
    if self.IsSaveDialog():
      if self.Extension:
        if not self.GetFilename().endswith(self.Extension):
          # Adds extensions if not specified
          self.SetFilename(self.Filename)

      if self.Path:
        if os.path.isfile(self.Path):
          overwrite = OverwriteDialog(self, self.Path)
          confirmed = overwrite.Confirmed()
          # ensure dialog does not persist
          overwrite.Destroy()
          if not confirmed:
            return

          try:
            os.remove(self.Path)
          except OSError:
            # File was removed before confirmation
            logger.debug("Item was removed before confirmation: {}".format(self.Path))

    # Because we are not using default FileDialog methods, we must set
    # directory manually.
    self.SetDirectory(os.path.dirname(self.Path))

    # File & directory dialogs should call this function
    ChangeWorkingDirectory(self.GetDirectory())

    self.EndModal(self.AffirmativeId)

  ## Updates the Filename & Path attributes
  #
  #  Differences from inherited method:
  #  - If the filename does not already have an extension, the default
  #  extension will be appended.
  #
  #  @param filename
  #    New \b \e string filename
  def SetFilename(self, filename):
    if filename:
      if filename.endswith("."):
        # Strip trailing periods
        filename = filename.rstrip(".")

      # Allow users to manually set filename extension
      if not "." in filename:
        if self.Extension:
          ext = self.Extension
          if not ext.startswith("."):
            ext = ".{}".format(ext)

          if not filename.endswith(ext):
            filename = "{}{}".format(filename, ext)

    return wx.FileDialog.SetFilename(self, filename)

## Displays a dialog with message & details
#
#  @todo FIXME: Crashes if icon is wx.NullBitmap
#  @param parent
#    \b \e wx.Window : The parent window
#  @param title
#    \b \e str : Text to display in title bar
#  @param icon
#    \b \e wx.Bitmap|str : Image to display
class DetailedMessageDialog(BaseDialog, ButtonDialog):
  def __init__(self, parent, title=GT("Message"), icon=ICON_INFORMATION, text=wx.EmptyString,
      details=wx.EmptyString, style=wx.DEFAULT_DIALOG_STYLE, buttons=(wx.ID_OK,),
      linewrap=0):

    BaseDialog.__init__(self, parent, wx.ID_ANY, title, style=style)

    # Allow using strings for 'icon' argument
    if isinstance(icon, str):
      icon = wx.Bitmap(icon)

    icon = wx.StaticBitmap(self, wx.ID_ANY, icon)

    txt_message = wx.StaticText(self, label=text)
    if linewrap:
      txt_message.Wrap(linewrap)

    # self.details needs to be empty for constructor
    self.details = wx.EmptyString
    details = details

    # *** Layout *** #

    self.lyt_urls = BoxSizer(wx.VERTICAL)

    # Only set if buttons are added to dialog
    self.lyt_buttons = None

    lyt_main = wx.GridBagSizer(5, 5)
    lyt_main.SetCols(3)
    lyt_main.AddGrowableRow(3)
    lyt_main.AddGrowableCol(2)
    lyt_main.Add(icon, (0, 0), (5, 1), wx.ALIGN_TOP|lyt.PAD_LR|wx.BOTTOM, 20)
    lyt_main.Add(txt_message, (0, 1), (1, 2), lyt.PAD_RT, 20)
    lyt_main.Add(self.lyt_urls, (1, 1), (1, 2), wx.RIGHT, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)

    self.AddButtons(buttons)

    if not strings.isEmpty(details):
      # self.details will be set here
      self.CreateDetailedView(details)

    else:
      self.Layout()

      self.Fit()
      self.SetMinSize(self.GetSize())

    self.CenterOnParent()

  ## Add custom buttons to dialog
  #
  #  NOTE: Do not call before self.SetSizer
  #
  #  @todo
  #    - FIXME: Rename to SetButtons???
  #    - FIXME: Should delete any previous buttons
  def AddButtons(self, button_ids):
    self.lyt_buttons = AddCustomButtons(self, button_ids)

    self.GetSizer().Add(self.lyt_buttons, (4, 2),
        flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|lyt.PAD_RTB, border=5)

  ## Adds a clickable link to the dialog
  def AddURL(self, url):
    if not isinstance(url, Hyperlink):
      url = Hyperlink(self, wx.ID_ANY, label=url, url=url)

    self.lyt_urls.Add(url, 0, wx.ALIGN_CENTER_VERTICAL)

    self.Layout()
    self.Fit()
    self.SetMinSize(self.GetSize())
    self.CenterOnParent()

  ## Shows dialog modal & returns 'confirmed' value
  #
  #  @return
  #    \b \e bool : True if ShowModal return value one of wx.ID_OK, wx.OK, wx.ID_YES, wx.YES
  def Confirmed(self):
    return self.ShowModal() in (wx.ID_OK, wx.OK, wx.ID_YES, wx.YES)

  ## Adds buttons & details text to dialog
  #
  #  @param details
  #    \b \e str : Detailed text to show in dialog
  def CreateDetailedView(self, details):
    # Controls have not been constructed yet
    if strings.isEmpty(self.details):
      self.btn_details = wx.ToggleButton(self, label=GT("Details"))
      #btn_copy = wx.Button(self, label=GT("Copy details"))

      self.dsp_details = TextAreaPanel(self, value=details,
          style=wx.TE_READONLY)

      # *** Event handlers *** #

      self.btn_details.Bind(wx.EVT_TOGGLEBUTTON, self.ToggleDetails)
      #btn_copy.Bind(wx.EVT_BUTTON, self.OnCopyDetails)

      layout = self.GetSizer()
      layout.Add(self.btn_details, (2, 1))
      #layout.Add(btn_copy, (2, 2), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
      layout.Add(self.dsp_details, (3, 1), (1, 2), wx.EXPAND|wx.RIGHT, 5)

      self.ToggleDetails()

    if not strings.isEmpty(details):
      for C in self.GetChildren():
        if isinstance(C, TextAreaPanel):
          self.details = details
          C.SetValue(self.details)
          return True
    return False

  ## Attempts to retrieve button instance matching btn_id
  #
  #  @todo
  #    - FIXME: This will fail if there are standard buttons in the dialog
  #    - FIXME: Retrieving by label doesn't work
  #  @param btn_id
  #    ID of the button instance to retrieve
  #  @return
  #    \b \e wx.Button instance or None
  def GetButton(self, btn_id):
    # Allow search by label
    use_label = not isinstance(btn_id, int)

    if self.lyt_buttons:
      for sizer in self.lyt_buttons.GetChildren():
        sizer = sizer.GetSizer()

        btn_layout = sizer.GetChildren()

        if btn_layout:
          BTN = btn_layout[0].GetWindow()
          LBL = None

          if len(btn_layout) < 2 and isinstance(BTN, wx.Button):
            LBL = BTN.GetLabel()

          else:
            LBL = btn_layout[1]
            if isinstance(LBL, wx.StaticText):
              LBL = LBL.GetLabel()

          if not use_label:
            if BTN.GetId() == btn_id:
              return BTN

          else:
            if LBL == btn_id:
              return BTN

  ## @todo Doxygen
  #  @todo FIXME: Layout initially wrong
  #  @todo Allow copying details to clipboard
  def OnCopyDetails(self, event=None):
    print("DEBUG: Copying details to clipboard ...")

    DetailedMessageDialog(self, "FIXME", ICON_EXCLAMATION,
        "Copying details to clipboard not functional").ShowModal()
    return

    cb_set = False

    clipboard = wx.Clipboard()
    if clipboard.Open():
      print("DEBUG: Clipboard opened")

      details = wx.TextDataObject(self.dsp_details.GetValue())
      print("DEBUG: Details set to:\n{}".format(details.GetText()))

      clipboard.Clear()
      print("DEBUG: Clipboard cleared")

      cb_set = clipboard.SetData(details)
      print("DEBUG: Clipboard data set")

      clipboard.Flush()
      print("DEBUG: Clipboard flushed")

      clipboard.Close()
      print("DEBUG: Clipboard cloased")

    del clipboard
    print("DEBUG: Clipboard object deleted")

    wx.MessageBox("FIXME: Details not copied to clipboard", GT("Debug"))

  ## Override inherited method to center on parent window first
  def ShowModal(self, *args, **kwargs):
    if self.Parent:
      self.CenterOnParent()
    return wx.Dialog.ShowModal(self, *args, **kwargs)

  ## @todo Doxygen
  def SetDetails(self, details):
    return self.CreateDetailedView(details)

  ## @todo Doxygen
  def ToggleDetails(self, event=None):
    try:
      if self.btn_details.GetValue():
        self.dsp_details.Show()
      else:
        self.dsp_details.Hide()
      self.Layout()
      self.Fit()
      self.SetMinSize(self.GetSize())
      return True
    except AttributeError:
      # Disable toggling details
      self.btn_details.Hide()
      self.Layout()
      self.Fit()
      self.SetMinSize(self.GetSize())
      return False


## Dialog that gives the option to confirm or cancel
class ConfirmationDialog(DetailedMessageDialog):
  def __init__(self, parent, title=GT("Warning"), text=wx.EmptyString,
      style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, buttons=(wx.ID_OK, wx.ID_CANCEL,)):

    DetailedMessageDialog.__init__(self, parent, title, icon=ICON_QUESTION,
        text=text, style=style, buttons=buttons)


## Dialog for the main window when a modified project is being closed
class ConfirmSaveDialog(DetailedMessageDialog):
  def __init__(self, parent, title=GT("Warning"), text=wx.EmptyString,
      style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
      buttons=(wx.ID_OK, wx.ID_CANCEL, wx.ID_SAVE,)):

    DetailedMessageDialog.__init__(self, parent, title, icon=ICON_QUESTION,
        text=text, style=style, buttons=buttons)

    btn_save = self.GetButton(wx.ID_SAVE)

    # *** Event Handling *** #

    if btn_save:
      btn_save.Bind(wx.EVT_BUTTON, self.OnButtonSave)

  ## @todo Doxygen
  def OnButtonSave(self, event=None):
    self.EndModal(wx.ID_SAVE)

## @todo Doxygen
class OverwriteDialog(ConfirmationDialog):
  def __init__(self, parent, filename):
    text = "{}\n\n{}".format(GT("Overwrite file?"), filename)

    ConfirmationDialog.__init__(self, parent, GT("File Exists"), text)


## Message dialog that shows an error & details
class ErrorDialog(DetailedMessageDialog):
  def __init__(self, parent, title=GT("Error"), text=GT("An error has occurred"),
      details=wx.EmptyString, linewrap=0):
    DetailedMessageDialog.__init__(self, parent, title, ICON_ERROR, text, details,
        linewrap=linewrap)


## @todo Doxygen
class SuperUserDialog(wx.Dialog):
  def __init__(self, ID=wx.ID_ANY):
    wx.Dialog.__init__(self, ui.app.getMainWindow(), ID)
    # User selector
    self.users = ComboBox(self)


## @todo Doxygen
def GetDialogWildcards(ID):
  proj_def = project_wildcards[ID][0]
  wildcards = list(project_wildcards[ID][1])

  for X in range(len(wildcards)):
    wildcards[X] = ".{}".format(wildcards[X])

  # Don't show list of suffixes in dialog's description
  if project_wildcards[ID][1] != supported_suffixes:
    proj_def = "{} ({})".format(proj_def, ", ".join(wildcards))

  for X in range(len(wildcards)):
    wildcards[X] = "*{}".format(wildcards[X])

  return (proj_def, ";".join(wildcards))

## @todo Doxygen
def GetDirDialog(parent, title):
  if parent == None:
    parent = ui.app.getMainWindow()
  dir_open = StandardDirDialog(parent, title)
  return dir_open

## Formats a wildcard list into a string
def _format_wildcard(wildcard):
  if isinstance(wildcard, (list, tuple)):
    wildcard = "|".join(wildcard)
  return wildcard

## Retrieves an 'open file' dialog for display
#
#  @param parent
#    \b \e wx.Window instance that should be dialog's parent
#  @param title
#    Text to be shown in the dialogs's title bar
#  @param wildcard
#    Wildcard to filter filenames
#  @param extension
#    The default filename extension to use when opening a file
#  @return
#    \b \e StandardFileDialog instance
def GetFileOpenDialog(parent, title, wildcard=wx.FileSelectorDefaultWildcardStr, extension=None,
      directory=None):

  if parent == None:
    parent = ui.app.getMainWindow()

  wildcard = _format_wildcard(wildcard)

  file_open = StandardFileDialog(parent, title, defaultDir=directory, defaultExt=extension,
      wildcard=wildcard, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_CHANGE_DIR)

  return file_open

## Retrieves a 'save file' dialog for display
#
#  @param parent
#    \b \e wx.Window instance that should be dialog's parent
#  @param title
#    Text to be shown in the dialogs's title bar
#  @param wildcard
#    Wildcard to filter filenames
#  @param extension
#    The default filename extension to use when saving a file
#  @return
#    \b \e StandardFileDialog instance
def GetFileSaveDialog(parent, title, wildcard=wx.FileSelectorDefaultWildcardStr, extension=None):
  if parent == None:
    parent = ui.app.getMainWindow()

  wildcard = _format_wildcard(wildcard)

  file_save = StandardFileDialog(parent, title, defaultExt=extension,
      wildcard=wildcard, style=wx.FD_SAVE)

  return file_save

## Used to display a dialog window
#
#  For custom dialogs, the method 'DisplayModal()' is used
#  to display the dialog. For stock dialogs, 'ShowModal()'
#  is used. The dialog that will be shown is determined
#  from 'GetFileSaveDialog'.
#
#  @todo FIXME: Perhaps should be moved to ui.output
#  @param dialog
#    The dialog window to be shown
#  @param center
#    Positioning relative to parent window
#  @return
#    'True' if the dialog's return value is 'wx..ID_OK', 'False'
#    otherwise
#
#  \b Alias: \e dbr.ShowDialog
def ShowDialog(dialog, center=wx.BOTH):
  dialog.CenterOnParent(center)

  return dialog.ShowModal() in (wx.ID_OK, wx.YES, wx.ID_YES, wx.ID_OPEN)

## Displays an instance of ErrorDialog class
#
#  Dialog is orphaned if parent is None so it can be displayed
#  without main window in cases of initialization errors.
#
#  @param text
#    \b \e str: Explanation of error
#  @param details
#    \b \e str: Extended details of error
#  @param parent
#    \b \e Parent window of new dialog
#    If False, parent is set to main window
#    If None, dialog is orphaned
#  @param module
#    \b \e str: Module where error was caught (used for Logger output)
#  @param warn
#    \b \e bool: Show log message as warning instead of error
def ShowErrorDialog(text, details=None, parent=False, warn=False, title=GT("Error"),
      linewrap=0):
  # Instantiate Logger message type so it can be optionally changed
  PrintLogMessage = logger.error
  if warn:
    PrintLogMessage = logger.warn

  logger_text = text

  if isinstance(text, (tuple, list)):
    logger_text = "; ".join(text)
    text = "\n".join(text)

  if details:
    logger_text = "{}:\n{}".format(logger_text, details)

  if parent == False:
    parent = ui.app.getMainWindow()

  if not parent:
    module_name = __name__

  else:
    module_name = parent.GetName()

  PrintLogMessage(logger_text)

  error_dialog = ErrorDialog(parent, title, text, linewrap=linewrap)
  if details:
    error_dialog.SetDetails(details)

  error_dialog.ShowModal()

## A function that displays a modal message dialog on the main window
#
#  @deprecated
#    `module` parameter is deprecated.
def ShowMessageDialog(text, title=GT("Message"), details=None, module=None, parent=None,
      linewrap=0):
  if not parent:
    parent = ui.app.getMainWindow()

  logger_text = text
  if isinstance(text, (tuple, list)):
    logger_text = "; ".join(text)
    text = "\n".join(text)

  if details:
    logger_text = "{}:\n{}".format(logger_text, details)

  message_dialog = DetailedMessageDialog(parent, title, ICON_INFORMATION, text, linewrap=linewrap)
  if details:
    message_dialog.SetDetails(details)

  # ~ Logger.Debug(module, logger_text)
  logger.debug(logger_text)

  message_dialog.ShowModal()
