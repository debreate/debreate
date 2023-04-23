
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Support functions for accessing wizard pages & attributes.
#
#  @module ui.helper

import wx

import ui.app

from dbr.language      import GT
from libdbr.logger     import Logger
from libdebreate.ident import pgid


_logger = Logger(__name__)

## @todo Doxygen
class ErrorTuple:
  def __init__(self, error_code=None, error_string=None):
    # FIXME: Should throw exception for wrong instance types???
    self.error_code = error_code
    self.error_string = error_string

  ## Same as dbr.functions.ErrorTuple.GetTuple
  def Get(self):
    return self.GetTuple()

  ## @todo Doxygen
  def GetCode(self):
    return self.error_code

  ## @todo Doxygen
  def GetMessage(self):
    return self.GetString()

  ## @todo Doxygen
  def GetString(self):
    return self.error_string

  ## @todo Doxygen
  def GetTuple(self):
    return (self.error_code, self.error_string,)

  ## @todo Doxygen
  def Set(self, error_code, error_string):
    # FIXME: Should throw exception for wrong instance types???
    self.error_code = error_code
    self.error_string = error_string

  ## @todo Doxygen
  def SetCode(self, error_code):
    # FIXME: Should throw exception for wrong instance type???
    if not isinstance(error_code, int):
      return 1
    self.error_code = error_code
    return 0


  ## @todo Doxygen
  def SetString(self, error_string):
    # FIXME: Should throw exception for wrong instance type???
    if not isinstance(error_string, str):
      return 1
    self.error_string = error_string
    return 0


## Checks if a field (or widget) is enabled
#
#  This is used for compatibility between wx. 2.8 & 3.0.
#  3.0 uses the method 'IsThisEnabled()' rather than
#  'IsEnabled()' to get the 'intrinsic' status of the
#  widget.
#  @param field
#   The widget (wx.Window) to be checked
def FieldEnabled(field):
  # wx. 3.0 must use 'IsThisEnabled' to get 'intrinsic' status in case parent is disabled
  if wx.MAJOR_VERSION > 2:
    return field.IsThisEnabled()

  else:
    return field.IsEnabled()


## Finds the ui.page.Page instance where an object is located
#
#  @param field
#    \b \e wx.Window instance to find parents of
def FindPageOf(field):
  parent = field.GetParent()
  if not parent:
    return None
  win_id = parent.GetId()
  if win_id in pgid.IdList:
    return ui.app.getPage(win_id)
  return FindPageOf(parent)


## Retrieves all instances of a window type from a parent window
def GetAllTypeFields(page, fieldType):
  # Objects that are not `ui.page.Page` instances must be passed as 'page' argument
  if not isinstance(page, wx.Window):
    page = ui.app.getPage(page)

  field_list = []

  # Recursively check children
  children = page.GetChildren()
  if children:
    for C in children:
      if isinstance(C, fieldType):
        field_list.append(C)

      field_list = field_list + GetAllTypeFields(C, fieldType)

  return field_list


## Retrieves a field/control from a page
#
#  @param page
#    \b \e ui.page.Page : The page to search
#  @param field_id
#    \b \e int : ID of desired field/control
#  @param field_type
#    \b \b wx.Window : The class type that field/control should be
#  @return
#    \b \e wx.Window : Field control matching field_id or None
#  @todo
#    FIXME: field_type is currently unused
def GetField(page, field_id, field_type=wx.Window):
  if not isinstance(page, wx.Window):
    page = ui.app.getPage(page)

  if isinstance(page, field_type) and page.GetId() == field_id:
    return page

  # Recursively check children
  children = page.GetChildren()
  if children:
    for C in children:
      field = GetField(C, field_id)

      if field and isinstance(field, field_type) and \
          field.GetId() == field_id:
        return field

  return ErrorTuple(1, GT("Field ID does not exist or match any fields: {}").format(field_id))


## Retrieves the input value of a field/control
#
#  @param page
#    \b \e Integer ID of desired page or page object
#  @param field_id
#    \b \e Integer ID of desired field/control
#  @param field_type
#    \b \b wx.Window : The class type that field/control should be
#  @return
#    The retrieved value of the field/control or an error tuple
#  @todo
#    FIXME: field_type is currently unused
def GetFieldValue(page, field_id, field_type=wx.Window):
  if isinstance(page, int):
    page = ui.app.getPage(page)

  if not isinstance(page, wx.Window):
    # FIXME: Should have error id
    err_msg = GT("Page retrieved was not instance of a window/widget: Page name: {}").format(page.GetName())
    return ErrorTuple(1, err_msg)

  field = GetField(page, field_id)

  if isinstance(field, ErrorTuple):
    return field

  if isinstance(field, wx.TextCtrl):
    return field.GetValue()

  if isinstance(field, wx.Choice):
    return field.GetStringSelection()

  # FIXME: Should have error id
  err_msg = GT("Unrecognized field type: {} (ID: {})").format(type(field), field_id)
  return ErrorTuple(1, err_msg)


## Finds the MainWindow instance.
#
#  @deprecated
#    Use `ui.app.getMainWindow`.
def GetMainWindow():
  _logger.deprecated(GetMainWindow, alt=ui.app.getMainWindow)

  return ui.app.getMainWindow()


## Retrieves a menu from the main window's menu bar by ID.
#
#  @param menuId
#    \b \e Integer ID of desired menu.
#  @return
#    The \b \e wx.Menu instance.
#  @deprecated
#    Use `ui.main.MainWindow.getMenu`.
def GetMenu(menuId):
  _logger.deprecated(GetMenu, alt="ui.main.MainWindow.getMenu")

  return ui.app.getMainWindow().getMenu(menuId)


## Retrieves the ui.menu.MenuBar instance in use by the main window.
#
#  @deprecated
#    Use `ui.main.MainWindow.getMenuBar`.
def GetMenuBar():
  _logger.deprecated(GetMenuBar, alt="ui.main.MainWindow.getMenuBar")

  return ui.app.getMainWindow().getMenuBar()


## Retrieves the `ui.page.Page` instance that matched pageId.
#
#  @deprecated
#    Use `ui.wizard.Wizard.GetPage`.
def GetPage(pageId):
  _logger.deprecated(GetPage, alt="ui.wizard.Wizard.getPage")

  page = ui.app.getWizard().getPage(pageId)
  return page


## Retrieves the full list of page IDs from the wizard.
#
#  @return
#    \b e\ tuple : List of all active wizard page IDs.
#  @deprecated
#    Use `ui.wizard.Wizard.getPagesIdList`.
def GetPagesIdList():
  _logger.deprecated(GetPagesIdList, alt="ui.wizard.Wizard.getPagesIdList")

  return ui.app.getWizard().getPagesIdList()


## Retrieves the ui.wizard.Wizard instance.
#
#  @deprecated
#    Use `ui.app.getWizard`.
def GetWizard():
  _logger.deprecated(GetWizard, alt=ui.app.getWizard)

  return ui.app.getWizard()
