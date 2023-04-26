
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module wizbin.changelog

import wx

import ui.app
import ui.page

from dbr.language      import GT
from f_export.ftarget  import FileOTarget
from globals.bitmaps   import ICON_WARNING
from globals.changes   import FormatChangelog
from globals.system    import GetOSDistNames
from globals.tooltips  import SetPageToolTips
from input.pathctrl    import PathCtrlESS
from input.select      import Choice
from input.select      import ComboBox
from input.text        import TextArea
from input.text        import TextAreaPanel
from input.text        import TextAreaPanelESS
from input.toggle      import CheckBox
from input.toggle      import CheckBoxESS
from libdbr            import strings
from libdbr.logger     import Logger
from libdebreate.ident import btnid
from libdebreate.ident import chkid
from libdebreate.ident import inputid
from libdebreate.ident import pgid
from libdebreate.ident import selid
from ui.button         import CreateButton
from ui.dialog         import DetailedMessageDialog
from ui.helper         import ErrorTuple
from ui.helper         import GetFieldValue
from ui.layout         import BoxSizer
from ui.style          import layout as lyt


logger = Logger(__name__)

## Changelog page.
class Page(ui.page.Page):
  ## Constructor
  #
  #  @param parent
  #    Parent <b><i>wx.Window</i></b> instance
  def __init__(self, parent):
    super().__init__(parent, pgid.CHANGELOG)

    txt_package = wx.StaticText(self, label=GT("Package"), name="package")
    self.ti_package = TextArea(self, inputid.PACKAGE, name=txt_package.Name)

    txt_version = wx.StaticText(self, label=GT("Version"), name="version")
    self.ti_version = TextArea(self, inputid.VERSION, name=txt_version.Name)

    dist_names = GetOSDistNames()

    txt_dist = wx.StaticText(self, label=GT("Distribution"), name="dist")

    if dist_names:
      self.ti_dist = ComboBox(self, inputid.DIST, choices=dist_names, name=txt_dist.Name)

    # Use regular text input if could not retrieve distribution names list
    else:
      self.ti_dist = TextArea(self, inputid.DIST, name=txt_dist.Name)

    opts_urgency = (
      "low",
      "medium",
      "high",
      "emergency",
      )

    txt_urgency = wx.StaticText(self, label=GT("Urgency"), name="urgency")
    self.sel_urgency = Choice(self, selid.URGENCY, choices=opts_urgency, name=txt_urgency.Name)

    txt_maintainer = wx.StaticText(self, label=GT("Maintainer"), name="maintainer")
    self.ti_maintainer = TextArea(self, inputid.MAINTAINER, name=txt_maintainer.Name)

    txt_email = wx.StaticText(self, label=GT("Email"), name="email")
    self.ti_email = TextArea(self, inputid.EMAIL, name=txt_email.Name)

    btn_import = CreateButton(self, btnid.IMPORT, GT("Import"), "import", name="btn import")
    txt_import = wx.StaticText(self, label=GT("Import information from Control page"))

    # Changes input
    self.ti_changes = TextAreaPanel(self, size=(20,150), name="changes")

    # *** Target installation directory

    # FIXME: Should this be set by config or project file???
    self.pnl_target = FileOTarget(self, "/usr/share/doc/<package>", name="target default",
        defaultType=CheckBoxESS, customType=PathCtrlESS, pathIds=(chkid.TARGET, inputid.TARGET,))

    self.btn_add = CreateButton(self, btnid.ADD, GT("Add"), "add", name="btn add")
    txt_add = wx.StaticText(self, label=GT("Insert new changelog entry"))

    self.chk_indentation = CheckBox(self, label=GT("Preserve indentation"), name="indent")

    self.dsp_changes = TextAreaPanelESS(self, inputid.CHANGES, monospace=True, name="log")
    self.dsp_changes.EnableDropTarget()

    SetPageToolTips(self)

    # *** Event Handling *** #

    btn_import.Bind(wx.EVT_BUTTON, self.OnImportFromControl)
    self.btn_add.Bind(wx.EVT_BUTTON, self.AddInfo)

    # *** Layout *** #

    LEFT_BOTTOM = lyt.ALGN_LB
    LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
    RIGHT_CENTER = wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL

    lyt_info = wx.FlexGridSizer(2, 6, 0, 0)

    lyt_info.AddGrowableCol(1)
    lyt_info.AddGrowableCol(3)
    lyt_info.AddGrowableCol(5)
    lyt_info.AddMany((
      (txt_package, 0, RIGHT_CENTER|wx.RIGHT, 5),
      (self.ti_package, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 5),
      (txt_version, 0, RIGHT_CENTER|wx.RIGHT, 5),
      (self.ti_version, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 5),
      (txt_dist, 0, RIGHT_CENTER|wx.RIGHT, 5),
      (self.ti_dist, 1, wx.EXPAND|wx.BOTTOM, 5),
      (txt_urgency, 0, RIGHT_CENTER|wx.RIGHT, 5),
      (self.sel_urgency, 1, wx.RIGHT, 5),
      (txt_maintainer, 0, RIGHT_CENTER|wx.RIGHT, 5),
      (self.ti_maintainer, 1, wx.EXPAND|wx.RIGHT, 5),
      (txt_email, 0, RIGHT_CENTER|wx.RIGHT, 5),
      (self.ti_email, 1, wx.EXPAND)
      ))

    lyt_details = wx.GridBagSizer()
    lyt_details.SetCols(3)
    lyt_details.AddGrowableRow(2)
    lyt_details.AddGrowableCol(1)

    lyt_details.Add(btn_import, (0, 0))
    lyt_details.Add(txt_import, (0, 1), flag=LEFT_CENTER)
    lyt_details.Add(wx.StaticText(self, label=GT("Changes")), (1, 0),
        flag=LEFT_BOTTOM|wx.TOP, border=5)
    lyt_details.Add(wx.StaticText(self, label=GT("Target")), (1, 2),
        flag=LEFT_BOTTOM)
    lyt_details.Add(self.ti_changes, (2, 0), (1, 2), wx.EXPAND|wx.RIGHT, 5)
    lyt_details.Add(self.pnl_target, (2, 2))
    lyt_details.Add(self.btn_add, (3, 0), (2, 1), wx.TOP, 5)
    lyt_details.Add(txt_add, (3, 1), flag=LEFT_BOTTOM|wx.TOP, border=5)
    lyt_details.Add(self.chk_indentation, (4, 1), flag=LEFT_BOTTOM)

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.AddSpacer(10)
    lyt_main.Add(lyt_info, 0, wx.EXPAND|lyt.PAD_LR, 5)
    lyt_main.AddSpacer(10)
    lyt_main.Add(lyt_details, 1, wx.EXPAND|lyt.PAD_LR, 5)
    lyt_main.Add(wx.StaticText(self, label="Changelog Output"),
        0, lyt.ALGN_L|lyt.PAD_LT, 5)
    lyt_main.Add(self.dsp_changes, 1, wx.EXPAND|lyt.PAD_LR|wx.BOTTOM, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

  ## @override ui.page.Page.init
  def init(self):
    return True

  ## Formats input text from 'changes' field for new entry in changelog
  def AddInfo(self, event=None):
    new_changes = self.ti_changes.GetValue()

    if strings.isEmpty(new_changes):
      DetailedMessageDialog(ui.app.getMainWindow(), GT("Warning"), ICON_WARNING,
          GT("\"Changes\" section is empty")).ShowModal()

      self.ti_changes.SetInsertionPointEnd()
      self.ti_changes.SetFocus()

      return

    package = self.ti_package.GetValue()
    version = self.ti_version.GetValue()
    dist = self.ti_dist.GetValue()
    urgency = self.sel_urgency.GetStringSelection()
    maintainer = self.ti_maintainer.GetValue()
    email = self.ti_email.GetValue()

    new_changes = FormatChangelog(new_changes, package, version, dist, urgency,
        maintainer, email, self.chk_indentation.GetValue())

    # Clean up leading & trailing whitespace in old changes
    old_changes = self.dsp_changes.GetValue().strip(" \t\n\r")

    # Only append newlines if log isn't already empty
    if not strings.isEmpty(old_changes):
      new_changes = "{}\n\n\n{}".format(new_changes, old_changes)

    # Add empty line to end of log
    if not new_changes.endswith("\n"):
      new_changes = "{}\n".format(new_changes)

    self.dsp_changes.SetValue(new_changes)

    # Clear "Changes" text
    self.ti_changes.Clear()
    self.ti_changes.SetFocus()

  ## Retrieves changelog text
  #
  #  The output is a text file that uses sections defined by braces ([, ])
  #
  #  @return
  #    <b><i>tuple(str, str)</i></b>: Filename & formatted string of changelog target & body
  def Get(self):
    target = self.pnl_target.GetPath()
    if target == self.pnl_target.GetDefaultPath():
      target = "STANDARD"

    return (target, self.GetChangelog())

  ## Retrieves plain text of the changelog field
  #
  #  @return
  #    Formatted changelog text
  def GetChangelog(self):
    return self.dsp_changes.GetValue()

  ## @todo Doxygen
  def GetSaveData(self):
    target = self.pnl_target.GetPath()
    if target == self.pnl_target.GetDefaultPath():
      target = "<<DEST>>DEFAULT<</DEST>>"
    else:
      target = "<<DEST>>{}<</DEST>>".format(target)
    return "\n".join(("<<CHANGELOG>>", target, self.dsp_changes.GetValue(), "<</CHANGELOG>>"))

  ## @override ui.page.Page.toString
  def toString(self):
    return self.GetSaveData()

  ## Checks the page's fields for exporting
  #
  #  @return
  #    <b><i>False</i></b> if page cannot be exported
  def IsOkay(self):
    return not strings.isEmpty(self.dsp_changes.GetValue())

  ## Imports select field values from the 'Control' page
  def OnImportFromControl(self, event=None):
    fields = (
      (self.ti_package, inputid.PACKAGE),
      (self.ti_version, inputid.VERSION),
      (self.ti_maintainer, inputid.MAINTAINER),
      (self.ti_email, inputid.EMAIL),
      )

    for F, FID in fields:
      field_value = GetFieldValue(pgid.CONTROL, FID)
      if isinstance(field_value, ErrorTuple):
        err_msg1 = GT("Got error when attempting to retrieve field value")
        err_msg2 = "\tError code: {}\n\tError message: {}".format(field_value.GetCode(), field_value.GetString())
        logger.error("{}:\n{}".format(err_msg1, err_msg2))
        continue
      if not strings.isEmpty(field_value):
        F.SetValue(field_value)

  ## Sets values of page's fields with given input
  #
  #  @param data
  #    Text to parse for values
  def Set(self, data):
    changelog = data.split("\n")
    target = changelog[0].split("<<DEST>>")[1].split("<</DEST>>")[0]
    if target == "DEFAULT":
      if not self.pnl_target.UsingDefault():
        self.pnl_target.Reset()
    else:
      self.pnl_target.SetPath(target)
    self.dsp_changes.SetValue("\n".join(changelog[1:]))

  ## Iterates child elements & resets each.
  #
  #  @override ui.page.Page.reset
  #  @todo
  #    Handle in `ui.page.Page` super class.
  def reset(self):
    logger.debug("resetting changelog page")
    for child_el in self.GetChildren():
      self.resetElement(child_el)

  ## Resets an element & its children.
  #
  #  @param el
  #    Element to be reset.
  def resetElement(self, el):
    if hasattr(el, "GetChildren"):
      for child_el in el.GetChildren():
        self.resetElement(child_el)
    if hasattr(el, "Reset"):
      el.Reset()

  ## Updates list of available distribution names.
  #
  #  @return
  #    `True` if interface supports drop down list.
  def reloadDistNames(self):
    if isinstance(self.ti_dist, ComboBox):
      self.ti_dist.Set(GetOSDistNames())
      return True
    return False
