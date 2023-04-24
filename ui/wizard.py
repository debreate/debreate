
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## The wizard interface
#
#  @module ui.wizard

import traceback

import wx

import ui.app
import ui.page

from dbr.event         import ChangePageEvent
from dbr.language      import GT
from globals           import tooltips
from globals.system    import mimport
from globals.tooltips  import TT_wiz_next
from globals.tooltips  import TT_wiz_prev
from input.markdown    import MarkdownDialog
from libdbr.logger     import Logger
from libdebreate.ident import btnid
from libdebreate.ident import chkid
from libdebreate.ident import inputid
from libdebreate.ident import listid
from libdebreate.ident import menuid
from libdebreate.ident import page_ids
from libdebreate.ident import pgid
from libdebreate.ident import selid
from startup           import tests
from ui.button         import CreateButton
from ui.dialog         import ShowDialog
from ui.dialog         import ShowErrorDialog
from ui.helper         import FieldEnabled
from ui.helper         import GetField
from ui.layout         import BoxSizer
from ui.panel          import ScrolledPanel


_logger = Logger(__name__)

## Wizard class for Debreate.
class Wizard(wx.Panel):
  ## Constructor
  #
  #  @param parent
  #    Parent <b><i>wx.Window</i></b> instance
  #  @param pageList
  #    <b><i>List</i></b> of `ui.page.Page` instances to initialize wizard with.
  #  @todo
  #    FIXME: `pageList` param unused?
  def __init__(self, parent, pageList=None):
    # ~ wx.Panel.__init__(self, parent, wx.ID_ANY, pageList)
    wx.Panel.__init__(self, parent, wx.ID_ANY)

    testing = tests.isActive("alpha")

    # List of pages available in the wizard
    self.Pages = []

    self.PagesIds = {}

    # IDs for first & last pages
    self.ID_FIRST = None
    self.ID_LAST = None

    if testing:
      # Help button
      btn_help = CreateButton(self, btnid.HELP)
      tooltips.register(btn_help, GT("Page help"))

    # A Header for the wizard
    pnl_title = wx.Panel(self, style=wx.RAISED_BORDER)
    pnl_title.SetBackgroundColour((10, 47, 162))

    # Text displayed from objects "name" - object.GetName()
    self.txt_title = wx.StaticText(pnl_title, label=GT("Title"))
    self.txt_title.SetForegroundColour((255, 255, 255))

    # font to use in the header
    headerfont = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

    self.txt_title.SetFont(headerfont)

    # Previous and Next buttons
    self.btn_prev = CreateButton(self, btnid.PREV)
    tooltips.register(self.btn_prev, TT_wiz_prev)
    self.btn_next = CreateButton(self, btnid.NEXT)
    tooltips.register(self.btn_next, TT_wiz_next)

    # These widgets are put into a list so that they are not automatically hidden
    self.permanent_children = [
      pnl_title,
      self.btn_prev,
      self.btn_next,
      ]

    if testing:
      self.permanent_children.insert(0, btn_help)

    # *** Event Handling *** #

    if testing:
      btn_help.Bind(wx.EVT_BUTTON, self.OnHelpButton)

    self.btn_prev.Bind(wx.EVT_BUTTON, self.ChangePage)
    self.btn_next.Bind(wx.EVT_BUTTON, self.ChangePage)

    # *** Layout *** #

    # Position the text in the header
    lyt_title = wx.GridSizer(1, 1, 0, 0)
    lyt_title.Add(self.txt_title, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)

    pnl_title.SetSizer(lyt_title)

    # Button sizer includes header
    lyt_buttons = BoxSizer(wx.HORIZONTAL)

    if testing:
      lyt_buttons.Add(btn_help, 0, wx.LEFT, 5)

    lyt_buttons.AddSpacer(5)
    lyt_buttons.Add(pnl_title, 1, wx.EXPAND|wx.RIGHT, 5)
    lyt_buttons.Add(self.btn_prev)
    lyt_buttons.AddSpacer(5)
    lyt_buttons.Add(self.btn_next)
    lyt_buttons.AddSpacer(5)

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.Add(lyt_buttons, 0, wx.EXPAND)

    self.SetSizer(lyt_main)
    self.SetAutoLayout(True)
    self.Layout()

  ## Add a new page to the wizard
  #
  #  @param page
  #    Must either be a `ui.page.Page` instance or the string suffix of the page's module
  def AddPage(self, page):
    err_msg = None
    err_det = None

    if not isinstance(page, ui.page.Page):
      try:
        pagemod = "wizbin.{}".format(page)
        page = mimport(pagemod).Page(self)
      except ImportError:
        err_msg = "module does not exist"
        err_det = traceback.format_exc()

    lyt_main = self.GetSizer()

    # Must already be child
    if not isinstance(page, ui.page.Page):
      err_msg = "not 'ui.page.Page' instance"
    elif page not in self.GetChildren():
      err_msg = "not child of wizard"
    elif page in lyt_main.GetChildWindows():
      err_msg = "page is already added to wizard"

    if err_msg:
      err_msg = "Cannot add page, {}".format(err_msg)
      if err_det:
        ShowErrorDialog(err_msg, err_det)
      else:
        ShowErrorDialog(err_msg)
      return

    main_window = ui.app.getMainWindow()

    lyt_main.Add(page, 1, wx.EXPAND)
    self.Pages.append(page)

    # Add to page menu
    page_menu = main_window.getMenu(menuid.PAGE)
    page_menu.Append(wx.MenuItem(page_menu, page.GetId(), page.GetLabel(), kind=wx.ITEM_RADIO))

    # Bind menu event to ID
    main_window.Bind(wx.EVT_MENU, main_window.OnMenuChangePage, id=page.Id)

  ## Handles displaying a new page when commanded
  def ChangePage(self, event=None):
    event_id = event.GetEventObject().GetId()
    # Get index of currently shown page
    for page in self.Pages:
      if page.IsShown():
        index = self.Pages.index(page)
        break
    if event_id == btnid.PREV:
      if index != 0:
        index -= 1
    elif event_id == btnid.NEXT:
      if index != len(self.Pages) - 1:
        index += 1
    page_id = self.Pages[index].GetId()
    # Show the indexed page
    self.ShowPage(page_id)
    ui.app.getMainWindow().getMenu(menuid.PAGE).Check(page_id, True)

  ## Deletes all pages from the wizard
  def ClearPages(self):
    for page in self.Pages:
      self.GetSizer().Remove(page)

    self.Pages = []

    # Re-enable the buttons if they have been disabled
    self.EnableNext()
    self.EnablePrev()

  ## Disables the 'next' page button when displaying the last page
  def DisableNext(self):
    self.EnableNext(False)

  ## Disables 'previous' page button when displaying the first page.
  def DisablePrev(self):
    self.EnablePrev(False)

  ## Enables/Disables 'next' page button dependent on if the last page is displayed.
  #
  #  @param value
  #    Button is enabled <b><i>True</i></b>, disabled otherwise
  def EnableNext(self, value=True):
    if isinstance(value, (bool, int)):
      if value:
        self.btn_next.Enable()
      else:
        self.btn_next.Disable()
    else:
      # FIXME: Should not raise error here???
      raise TypeError("Must be bool or int value")

  ## Enables/Disables 'previous' page button dependent on if the last page is displayed.
  #
  #  @param value
  #    Button is enabled <b><i>True</i></b>, disabled otherwise
  def EnablePrev(self, value=True):
    if isinstance(value, (bool, int)):
      if value:
        self.btn_prev.Enable()
      else:
        self.btn_prev.Disable()
    else:
      # FIXME: Should not raise error here???
      raise TypeError("Must be bool or int value")

  ## Exports pages individually by calling `ui.page.Page.Export`.
  #
  #  Filename output is handled by classes inheriting `ui.page.Page`.
  #
  #  @param pageList
  #    List of `ui.page.Page` instances, or page IDs, to be exported.
  #  @param outDir
  #    Path to target directory.
  def ExportPages(self, pageList, outDir):
    for P in pageList:
      # Support using list of IDs instead of `ui.page.Page` instances
      if not isinstance(P, ui.page.Page):
        P = self.getPage(P)
      P.Export(outDir)

  ## Retrieves all current `ui.page.Page` instances.
  #
  #  @return
  #    <b><i>Tuple</i></b> list of currently available wizard pages.
  def GetAllPages(self):
    return tuple(self.Pages)

  ## Retrieves currently displayed page.
  #
  #  @return
  #    `ui.page.Page` instance.
  def GetCurrentPage(self):
    for page in self.Pages:
      if page.IsShown():
        return page

  ## Retrieve currently displayed page's ID.
  #
  #  @return
  #    <b><i>Integer</i></b> ID of page.
  def GetCurrentPageId(self):
    current_page = self.GetCurrentPage()
    if current_page:
      return current_page.GetId()

  ## Retrieves a page by ID.
  #
  #  @param pageId
  #    <b><i>Integer</i></b> ID of desired page.
  #  @return
  #    `ui.page.Page` instance or <b><i>None</i></b> if ID not found.
  def getPage(self, pageId):
    for P in self.Pages:
      if P.GetId() == pageId:
        return P
    _logger.warn("Page with ID {} has not been constructed".format(pageId))

  ## Alias of `ui.wizard.Wizard.getPage` for backward compatibility.
  #
  #  @deprecated
  #    Use `ui.wizard.Wizard.getPage`.
  def GetPage(self, pageId):
    _logger.deprecated(self.GetPage, alt=self.getPage)

    return self.getPage(pageId)

  ## Retrieves the full list of page IDs.
  #
  #  @return
  #    <b><i>Tuple</i></b> list of all current pages IDs.
  def getPagesIdList(self):
    page_ids = []
    for P in self.Pages:
      page_ids.append(P.GetId())
    return tuple(page_ids)

  ## Alias of `ui.wizard.Wizard.getPagesIdList` for backword compatibility.
  #
  #  @deprecated
  #    Use `ui.wizard.Wizard.getPagesIdList`.
  def GetPagesIdList(self):
    _logger.deprecated(self.GetPagesIdList, alt=self.getPagesIdList)

    return self.getPagesIdList()

  ## Initializes wizard by displaying an initial page.
  #
  #  @param showPage
  #    <b><i>Integer</i></b> index of page to be shown.
  def Initialize(self, showPage=0):
    if self.Pages:
      self.ID_FIRST = self.Pages[0].Id
      self.ID_LAST = self.Pages[-1].Id
    if not showPage:
      self.ShowPage(self.ID_FIRST)
    else:
      self.ShowPage(self.Pages[showPage].Id)
    for PAGE in self.Pages:
      PAGE.InitPage()
    self.Layout()

  ## Uses children `ui.page.Page` instances to set pages.
  #
  #  @return
  #    Value of `ui.wizard.Wizard.SetPages`.
  def InitPages(self):
    pages = []
    for C in self.GetChildren():
      if isinstance(C, ui.page.Page):
        pages.append(C)
    return self.SetPages(pages)

  ## Shows a help dialog for currently displayed page.
  def OnHelpButton(self, event=None):
    label = self.GetCurrentPage().GetLabel()
    page_help = MarkdownDialog(self, title=GT("Help"), readonly=True)
    page_help.SetText(GT("Help information for page \"{}\"".format(label)))
    ShowDialog(page_help)

  ## Removes a page from the wizard & memory.
  #
  #  @param pageId
  #    <b><i>Integer</i></b> ID of the page to be removed.
  def RemovePage(self, pageId):
    page = self.getPage(pageId)
    if page in self.Pages:
      self.Pages.pop(self.Pages.index(page))

    lyt_main = self.GetSizer()
    if page in lyt_main.GetChildWindows():
      lyt_main.Remove(page)
    self.Layout()

    # Remove from page menu
    ui.app.getMainWindow().getMenu(menuid.PAGE).Remove(pageId).Destroy()

  ## Resets all but greeting page.
  #
  #  @return
  #    Value of `ui.wizard.Wizard.Initialize`.
  def Reset(self):
    for PAGE in reversed(self.Pages):
      if PAGE.Id != pgid.GREETING:
        self.RemovePage(PAGE.Id)

    return self.Initialize()

  ## Resets each page's fields to default settings.
  #
  #  Calls `ui.page.Page.reset`.
  def ResetPagesInfo(self):
    for page in self.Pages:
      page.reset()

  ## Sets up the wizard for 'binary' mode.
  #
  #  @param startPage
  #    <b><i>Integer</i></b> index of page to be initially displayed.
  def SetModeBin(self, startPage=1):
    self.Reset()

    mods = [
      "control",
      "depends",
      "files",
      "scripts",
      "changelog",
      "copyright",
      "launchers",
      "build",
      ]

    for M in mods:
      self.AddPage(M)

    self.Initialize(startPage)

  ## Sets up the wizard for 'source' mode
  #
  #  @todo
  #    FIXME: WIP
  def SetModeSrc(self):
    self.Reset()

  ## Organizes `ui.page.Page` instances for displaying as pages in wizard.
  #
  #  @param pages
  #    List of pages owned by wizard to be used.
  #  @deprecated
  def SetPages(self, pages):
    self.ID_FIRST = pages[0].GetId()
    self.ID_LAST = pages[-1].GetId()

    main_window = ui.app.getMainWindow()

    # Make sure all pages are hidden
    children = self.GetChildren()
    for child in children:
      if child not in self.permanent_children:
        child.Hide()

    # Remove any current pages from the wizard
    self.ClearPages()

    if not isinstance(pages, (list, tuple)):
      # FIXME: Should not raise error here???
      raise TypeError("Argument 2 of Wizard.SetPages() must be List or Tuple")

    for PAGE in pages:
      self.Pages.append(PAGE)
      self.PagesIds[PAGE.GetId()] = PAGE.GetName().upper()
      self.GetSizer().Insert(1, PAGE, 1, wx.EXPAND)

      pg_id = PAGE.GetId()

      # Add pages to main menu
      main_window.menu_page.AppendItem(
        wx.MenuItem(main_window.menu_page, pg_id, PAGE.GetLabel(),
        kind=wx.ITEM_RADIO))

      # Bind menu event to ID
      wx.EVT_MENU(main_window, pg_id, main_window.OnMenuChangePage)

    # Initialize functions that can only be called after all pages are constructed
    for PAGE in pages:
      PAGE.InitPage()

    self.ShowPage(self.ID_FIRST)

    self.Layout()

  ## Sets the text displayed in the wizard title bar.
  #
  #  @param title
  #    Text to be displayed.
  def SetTitle(self, title):
    self.txt_title.SetLabel(title)
    self.Layout()

  ## Sets or changes the displayed page.
  #
  #  Posts a 'change page' event to notify the main window.
  #
  #  @param pageId
  #    `libdebreate.ident.pgid` of the page to be displayed.
  def ShowPage(self, pageId):
    for p in self.Pages:
      if p.GetId() != pageId:
        p.Hide()
      else:
        p.Show()
        self.txt_title.SetLabel(p.GetLabel())

    if pageId == self.ID_FIRST:
      self.btn_prev.Enable(False)
    elif not FieldEnabled(self.btn_prev):
      self.btn_prev.Enable(True)
    if pageId == self.ID_LAST:
      self.btn_next.Enable(False)
    elif not FieldEnabled(self.btn_next):
      self.btn_next.Enable(True)

    self.Layout()
    wx.PostEvent(ui.app.getMainWindow(), ChangePageEvent(0))

## Inherited class for wizard pages
# ~ class WizardPage(ScrolledPanel):
  # ~ ## Constructor
  # ~ #
  # ~ #  @param parent
  # ~ #    Parent <b><i>wx.Window</i></b> instance
  # ~ #  @param pageId
  # ~ #    Identifier to use for page
  # ~ def __init__(self, parent, pageId):
    # ~ ScrolledPanel.__init__(self, parent, pageId)

    # ~ _logger.deprecated(WizardPage, alt=ui.page.Page)

    # ~ # Pages should not be shown until wizard is initialized
    # ~ self.Hide()

    # ~ self.SetName(page_ids[self.GetId()])

    # ~ ## Label to show in title & menu
    # ~ # NOTE: Cannot use 'self.Label' in wx.Python 2.8
    # ~ self.PLabel = wx.EmptyString

    # ~ if not self.PLabel and self.Id in pgid.Labels:
      # ~ self.PLabel = pgid.Labels[self.Id]

    # ~ ## List of IDs that should not be reset
    # ~ self.IgnoreResetIds = []

    # ~ # Is added to prebuild check list
    # ~ self.prebuild_check = True

  # ~ ## Retrieves the page's field's data
  # ~ def Get(self):
    # ~ _logger.warn(GT("Page {} does not override inherited method Get").format(self.GetName()))

  # ~ ## Retrieves the page's label
  # ~ #
  # ~ #  if ui.wizard.WizardPage.Label is not set, returns the ui.wizard.WizardPage.Name attribute
  # ~ def GetLabel(self):
    # ~ if self.PLabel == None:
      # ~ return self.GetName()
    # ~ return self.PLabel

  # ~ ## Sets page's label
  # ~ def SetLabel(self, label):
    # ~ self.PLabel = label

  # ~ ## Retrieves all fields that cannot be left blank for build
  # ~ #
  # ~ #  @param children
  # ~ #    <b><i>List/Tuple</i></b> of the fields to be checked
  # ~ #  @return
  # ~ #    <b><i>Tuple</i></b> list of fields marked as required
  # ~ #  @todo
  # ~ #    FIXME: Should only require page ID
  # ~ def GetRequiredFields(self, children=None):
    # ~ required_fields = []
    # ~ if children == None:
      # ~ children = self.GetChildren()
    # ~ for C in children:
      # ~ for RF in self.GetRequiredFields(C.GetChildren()):
        # ~ required_fields.append(RF)
      # ~ # FIXME: Better way to mark fields as required???
      # ~ try:
        # ~ if C.req:
          # ~ required_fields.append(C)
      # ~ except AttributeError:
        # ~ pass
    # ~ return tuple(required_fields)

  # ~ ## Reads & parses page data from a formatted text file
  # ~ #
  # ~ #  @param filename
  # ~ #    File path to open
  # ~ def ImportFromFile(self, filename):
    # ~ _logger.warn(GT("Page {} does not override inherited method ImportFromFile").format(self.GetName()))

  # ~ ## This method can be used to access page members that are only available
  # ~ #  after the wizard has been completely initialized
  # ~ #
  # ~ #  @todo
  # ~ #    FIXME: Rename to 'OnWizardInit'???
  # ~ def InitPage(self):
    # ~ _logger.debug(GT("Page {} does not override inherited method InitPage").format(self.GetName()))
    # ~ return False

  # ~ ## Checks the page's fields for exporting
  # ~ #
  # ~ #  @return
  # ~ #    <b><i>False</i></b> if page cannot be exported
  # ~ def IsOkay(self):
    # ~ _logger.warn(GT("Page {} does not override inherited method IsOkay").format(self.GetName()))
    # ~ return False

  # ~ ## Resets page's fields to default settings
  # ~ #
  # ~ #  Set the ui.wizard.WizardPage.IgnoreResetIds attribute for any field
  # ~ #  that should not be reset
  # ~ def Reset(self):
    # ~ field_ids = (
      # ~ chkid,
      # ~ inputid,
      # ~ listid,
      # ~ selid,
      # ~ )

    # ~ for IDTYPE in field_ids:
      # ~ idlist = IDTYPE.IdList
      # ~ for ID in idlist:
        # ~ if ID not in self.IgnoreResetIds:
          # ~ field = GetField(self, ID)
          # ~ if isinstance(field, wx.Window):
            # ~ field.Reset()
