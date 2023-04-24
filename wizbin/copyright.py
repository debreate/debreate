
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module wizbin.copyright

import os

import wx

import ui.app
import ui.page

from dbr.functions      import GetLongestLine
from dbr.language       import GT
from dbr.templates      import GetCustomLicenses
from dbr.templates      import GetLicenseTemplateFile
from dbr.templates      import GetLocalLicenses
from dbr.templates      import GetSysLicenses
from dbr.templates      import sys_licenses_path
from globals            import tooltips
from globals.dateinfo   import GetYear
from globals.errorcodes import dbrerrno
from input.select       import Choice
from input.text         import TextAreaPanelESS
from libdbr             import fileio
from libdbr             import paths
from libdbr             import strings
from libdbr.logger      import Logger
from libdebreate.ident  import btnid
from libdebreate.ident  import pgid
from libdebreate.ident  import selid
from ui.button          import CreateButton
from ui.dialog          import ConfirmationDialog
from ui.dialog          import ShowErrorDialog
from ui.helper          import GetField
from ui.layout          import BoxSizer
from ui.style           import layout as lyt


_logger = Logger(__name__)

# Globals
copyright_header = GT("Copyright © {} <copyright holder(s)> [<email>]")

## Copyright page.
#
#  @param parent
#    Parent `wx.Window` instance.
class Page(ui.page.Page):
  def __init__(self, parent):
    super().__init__(parent, pgid.COPYRIGHT)

    self.custom_licenses = []

    ## A list of available license templates
    self.sel_templates = Choice(self, selid.LICENSE, name="list»")

    # Initialize the template list
    self.OnRefreshList()

    btn_template = CreateButton(self, label=GT("Full Template"), image="full", name="full»")
    self.btn_template_simple = CreateButton(self, label=GT("Short Template"), image="short",
        name="short»")
    btn_refresh = CreateButton(self, btnid.REFRESH, GT("Refresh Template List"), "refresh",
        name="btn refresh")
    btn_open = CreateButton(self, btnid.BROWSE, GT("Open Template Directory"), "browse",
        name="btn opendir", commands="xdg-open")

    if not self.sel_templates.GetCount():
      self.sel_templates.Enable(False)
      btn_template.Enable(False)
      self.btn_template_simple.Enable(False)

    ## Area where license text is displayed
    self.dsp_copyright = TextAreaPanelESS(self, monospace=True, name="license")
    self.dsp_copyright.EnableDropTarget()

    tooltips.SetPageToolTips(self)

    # Initiate tooltip for drop-down selector
    if self.sel_templates.IsEnabled():
      self.OnSelectLicense(self.sel_templates)

    # *** Event Handling *** #

    self.sel_templates.Bind(wx.EVT_CHOICE, self.OnSelectLicense)

    btn_open.Bind(wx.EVT_BUTTON, self.OnOpenPath)
    btn_refresh.Bind(wx.EVT_BUTTON, self.OnRefreshList)
    btn_template.Bind(wx.EVT_BUTTON, self.OnTemplateFull)
    self.btn_template_simple.Bind(wx.EVT_BUTTON, self.OnTemplateShort)

    # *** Layout *** #

    lyt_top = BoxSizer(wx.HORIZONTAL)
    lyt_top.Add(wx.StaticText(self, label=GT("Available Templates")), 0,
        lyt.ALGN_CV)
    lyt_top.Add(self.sel_templates, 0, lyt.ALGN_CV|wx.LEFT, 5)
    lyt_top.Add(btn_template, 0, wx.LEFT, 5)
    lyt_top.Add(self.btn_template_simple, 0, wx.LEFT, 5)
    lyt_top.Add(btn_refresh, 0, wx.LEFT, 5)
    lyt_top.Add(btn_open, 0, wx.LEFT, 5)

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.AddSpacer(10)
    lyt_main.Add(lyt_top, 0, lyt.PAD_LR|wx.BOTTOM, 5)
    lyt_main.Add(self.dsp_copyright, 1, wx.EXPAND|lyt.PAD_LRB, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

  ## @override ui.page.Page.init
  def init(self):
    return True

  ## Displays a confirmation dialog to clear the text area if it is not empty.
  #
  #  @return
  #    `True`, if user confirmed.
  def DestroyLicenseText(self):
    if not strings.isEmpty(self.dsp_copyright.GetValue()):
      warn_msg = GT("This will destroy all license text.")
      warn_msg = "{}\n\n{}".format(warn_msg, GT("Continue?"))

      if ConfirmationDialog(ui.app.getMainWindow(), text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
        return False

    return True

  ## Retrieves copyright/license text.
  #
  #  @return
  #    `tuple(str, str)`: Filename & copyright/license text.
  def Get(self, getModule=False):
    page = self.dsp_copyright.GetValue()

    if strings.isEmpty(page):
      page = None

    if getModule:
      page = (__name__, page,)

    return page

  ## Retrieves license path.
  #
  #  @param licName
  #    License file basename to search for. If `None`, uses currently selected license.
  #  @return
  #    Full path to license file if found.
  def GetLicensePath(self, licName=None):
    # Default to currently selected template
    if not licName:
      licName = self.GetSelectedName()

    return GetLicenseTemplateFile(licName)

  ## @todo Doxygen
  def GetSaveData(self):
    data = self.Get()
    return "<<COPYRIGHT>>\n{}\n<</COPYRIGHT>>".format(data)

  ## @override ui.page.Page.toString
  def toString(self):
    return self.GetSaveData()

  ## Retrieves template name.
  #
  #  @return
  #    Currently selected template.
  def GetSelectedName(self):
    return GetField(self, selid.LICENSE).GetStringSelection()

  ## Sets page's fields from opened file.
  #
  #  @param filename
  #    File from which data is imported.
  def ImportFromFile(self, filename):
    if not os.path.isfile(filename):
      return dbrerrno.ENOENT

    copyright_data = fileio.readFile(filename).split("\n")

    # Remove preceding empty lines
    remove_index = 0
    for I in copyright_data:
      if not strings.isEmpty(I):
        break

      remove_index += 1

    for I in reversed(range(remove_index)):
      copyright_data.remove(copyright_data[I])

    copyright_data = "\n".join(copyright_data)

    self.dsp_copyright.SetValue(copyright_data)

    return 0

  ## Checks if page can be exported or or added to build.
  #
  #  @return
  #    `True` if export is possible.
  def IsOkay(self):
    return not strings.isEmpty(self.dsp_copyright.GetValue())

  ## Opens directory containing currently selected license.
  def OnOpenPath(self, event=None):
    path = self.GetLicensePath()
    if not path:
      ShowErrorDialog(GT("Error retrieving template path: {}").format(self.GetSelectedName()))
      return False
    path = os.path.dirname(path)
    if os.path.isdir(path):
      fileio.openFileManager(path)
      return True
    return False

  ## Repopulates template list.
  def OnRefreshList(self, event=None):
    # FIXME: Ignore symbolic links???
    self.custom_licenses = GetLocalLicenses()

    licenses = list(self.custom_licenses)

    # System licenses are not added to "custom" list
    for LIC in GetSysLicenses():
      if LIC not in licenses:
        licenses.append(LIC)

    for LIC in GetCustomLicenses():
      if LIC not in licenses:
        licenses.append(LIC)
        self.custom_licenses.append(LIC)

    self.custom_licenses.sort(key=str.lower)

    sel_templates = GetField(self, selid.LICENSE)

    selected = None
    if sel_templates.GetCount():
      selected = sel_templates.GetStringSelection()

    sel_templates.Set(sorted(licenses, key=str.lower))

    if selected:
      if not sel_templates.SetStringSelection(selected):
        # Selected template file was not found
        sel_templates.SetSelection(sel_templates.GetDefaultValue())

        # Update short template button enabled state
        self.OnSelectLicense()

    else:
      sel_templates.SetSelection(sel_templates.GetDefaultValue())

  ## Enables/Disables simple template button.
  #
  #  Simple template generation is only available for system  licenses.
  def OnSelectLicense(self, event=None):
    choice = GetField(self, selid.LICENSE)
    if choice:
      template = choice.GetString(choice.GetSelection())

      if template in self.custom_licenses:
        self.btn_template_simple.Disable()

      else:
        self.btn_template_simple.Enable()

      self.SetLicenseTooltip()

  ## Generates a full license template.
  def OnTemplateFull(self, event=None):
    selected_template = self.sel_templates.GetStringSelection()
    template_file = self.GetLicensePath(selected_template)

    if self.DestroyLicenseText():
      if not template_file or not os.path.isfile(template_file):
        ShowErrorDialog(GT("Could not locate license file: {}").format(self.GetSelectedName()))

        return

      _logger.debug("Copying license {}".format(template_file))

      license_text = fileio.readFile(template_file)

      # Number defines how many empty lines to add after the copyright header
      # Boolean/Integer defines whether copyright header should be centered/offset
      add_header = {
        "Artistic": (1, True),
        "BSD": (0, False),
      }

      template_name = os.path.basename(template_file)
      if template_name in add_header:
        license_text = license_text.split("\n")

        empty_lines = add_header[template_name][0]
        for L in range(empty_lines):
          license_text.insert(0, wx.EmptyString)

        header = copyright_header.format(GetYear())

        center_header = add_header[template_name][1]
        if center_header:
          _logger.debug("Centering header...")

          offset = 0

          # Don't use isinstance() here because boolean is an instance of integer
          if type(center_header) == int:
            offset = center_header

          else:
            # Use the longest line found in the text to center the header
            longest_line = GetLongestLine(license_text)

            _logger.debug("Longest line: {}".format(longest_line))

            header_length = len(header)
            if header_length < longest_line:
              offset = (longest_line - header_length) / 2

          if offset:
            _logger.debug("Offset: {}".format(offset))

            header = "{}{}".format(" " * offset, header)

        # Special changes for BSD license
        if template_name == "BSD":
          line_index = 0
          for LI in license_text:
            if "copyright (c)" in LI.lower():
              license_text[line_index] = header

              break

            line_index += 1

        else:
          license_text.insert(0, header)

        license_text = "\n".join(license_text)

      if not license_text:
        ShowErrorDialog(GT("License template is empty"))

        return

      self.dsp_copyright.SetValue(license_text)
      self.dsp_copyright.SetInsertionPoint(0)

    self.dsp_copyright.SetFocus()

  ## Generates a short reference template for a system license.
  def OnTemplateShort(self, event=None):
    if self.DestroyLicenseText():
      self.dsp_copyright.Clear()

      license_path = "{}/{}".format(sys_licenses_path, self.sel_templates.GetString(self.sel_templates.GetSelection()))

      self.dsp_copyright.WriteText("{}\n\n{}".format(copyright_header.format(GetYear()), license_path))
      self.dsp_copyright.SetInsertionPoint(0)

    self.dsp_copyright.SetFocus()

  ## Resets all page fields to default values.
  def Reset(self):
    self.dsp_copyright.Clear()

    if self.sel_templates.IsEnabled():
      self.sel_templates.Reset()
      self.OnSelectLicense(self.sel_templates)

  ## @override ui.page.Page.reset
  def reset(self):
    self.Reset()

  ## Sets the text of the displayed copyright.
  #
  #  @param data
  #    Text to parse for field values.
  def Set(self, data):
    self.dsp_copyright.SetValue(data)

  ## Changes the Choice instance's tooltip for the current license.
  def SetLicenseTooltip(self):
    license_name = self.sel_templates.GetString(self.sel_templates.GetSelection())
    license_path = self.GetLicensePath(license_name)
    if license_path:
      tooltips.register(self.sel_templates, license_path)
    else:
      tooltips.unregister(self.sel_templates)
