
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module wizbin.control

import os

import wx

from wx.adv import OwnerDrawnComboBox

import ui.app
import ui.page

from dbr.language       import GT
from globals.errorcodes import dbrerrno
from globals.tooltips   import SetPageToolTips
from input.select       import ChoiceESS
from input.select       import ComboBoxESS
from input.text         import TextAreaESS
from input.text         import TextAreaPanelESS
from input.toggle       import CheckBoxESS
from libdbr             import strings
from libdbr.fileio      import readFile
from libdbr.fileio      import writeFile
from libdbr.logger      import Logger
from libdebreate.ident  import btnid
from libdebreate.ident  import inputid
from libdebreate.ident  import pgid
from ui.button          import CreateButton
from ui.dialog          import GetFileOpenDialog
from ui.dialog          import GetFileSaveDialog
from ui.dialog          import ShowDialog
from ui.dialog          import ShowErrorDialog
from ui.helper          import FieldEnabled
from ui.helper          import GetField
from ui.layout          import BoxSizer
from ui.panel           import BorderedPanel
from ui.style           import layout as lyt
from ui.textpreview     import TextPreview


logger = Logger(__name__)

## This panel displays the field input of the control file.
class Page(ui.page.Page):
  ## Constructor
  #
  #  @param parent
  #    Parent <b><i>wx.Window</i></b> instance
  def __init__(self, parent):
    super().__init__(parent, pgid.CONTROL)

    pnl_bg = wx.Panel(self)

    # Buttons to open, save, & preview control file
    btn_open = CreateButton(pnl_bg, btnid.BROWSE, GT("Browse"), "browse", name="btn browse")
    btn_save = CreateButton(pnl_bg, btnid.SAVE, GT("Save"), "save", name="btn save")
    btn_preview = CreateButton(pnl_bg, btnid.PREVIEW, GT("Preview"), "preview", name="btn preview")

    # *** Required fields *** #

    pnl_require = BorderedPanel(pnl_bg)

    txt_package = wx.StaticText(pnl_require, label=GT("Package"), name="package")
    txt_package.req = True
    ti_package = TextAreaESS(pnl_require, inputid.PACKAGE, name=txt_package.Name)
    ti_package.req = True

    txt_version = wx.StaticText(pnl_require, label=GT("Version"), name="version")
    txt_version.req = True
    ti_version = TextAreaESS(pnl_require, inputid.VERSION, name=txt_version.Name)
    ti_version.req = True

    txt_maintainer = wx.StaticText(pnl_require, label=GT("Maintainer"), name="maintainer")
    txt_maintainer.req = True
    ti_maintainer = TextAreaESS(pnl_require, inputid.MAINTAINER, name=txt_maintainer.Name)
    ti_maintainer.req = True

    txt_email = wx.StaticText(pnl_require, label=GT("Email"), name="email")
    txt_email.req = True
    ti_email = TextAreaESS(pnl_require, inputid.EMAIL, name=txt_email.Name)
    ti_email.req = True

    opts_arch = (
      "all", "alpha", "amd64", "arm", "arm64", "armeb", "armel",
      "armhf", "avr32", "hppa", "i386", "ia64", "lpia", "m32r",
      "m68k", "mips", "mipsel", "powerpc", "powerpcspe", "ppc64",
      "s390", "s390x", "sh3", "sh3eb", "sh4", "sh4eb", "sparc",
      "sparc64",
      )

    txt_arch = wx.StaticText(pnl_require, label=GT("Architecture"), name="architecture")
    sel_arch = ChoiceESS(pnl_require, inputid.ARCH, choices=opts_arch, name=txt_arch.Name)
    sel_arch.Default = 0
    sel_arch.SetSelection(sel_arch.Default)

    # *** Recommended fields *** #

    pnl_recommend = BorderedPanel(pnl_bg)

    opts_section = (
      "admin", "cli-mono", "comm", "database", "devel", "debug",
      "doc", "editors", "electronics", "embedded", "fonts", "games",
      "gnome", "graphics", "gnu-r", "gnustep", "hamradio", "haskell",
      "httpd", "interpreters", "java", "kde", "kernel", "libs",
      "libdevel", "lisp", "localization", "mail", "math",
      "metapackages", "misc", "net", "news", "ocaml", "oldlibs",
      "otherosfs", "perl", "php", "python", "ruby", "science",
      "shells", "sound", "tex", "text", "utils", "vcs", "video",
      "web", "x11", "xfce", "zope",
      )

    txt_section = wx.StaticText(pnl_recommend, label=GT("Section"), name="section")
    ti_section = ComboBoxESS(pnl_recommend, choices=opts_section, name=txt_section.Name)

    opts_priority = (
      "optional",
      "standard",
      "important",
      "required",
      "extra",
      )

    txt_priority = wx.StaticText(pnl_recommend, label=GT("Priority"), name="priority")
    sel_priority = ChoiceESS(pnl_recommend, choices=opts_priority, name=txt_priority.Name)
    sel_priority.Default = 0
    sel_priority.SetSelection(sel_priority.Default)

    txt_synopsis = wx.StaticText(pnl_recommend, label=GT("Short Description"), name="synopsis")
    ti_synopsis = TextAreaESS(pnl_recommend, name=txt_synopsis.Name)

    txt_description = wx.StaticText(pnl_recommend, label=GT("Long Description"), name="description")
    self.ti_description = TextAreaPanelESS(pnl_recommend, name=txt_description.Name)

    # *** Optional fields *** #

    pnl_option = BorderedPanel(pnl_bg)

    txt_source = wx.StaticText(pnl_option, label=GT("Source"), name="source")
    ti_source = TextAreaESS(pnl_option, name=txt_source.Name)

    txt_homepage = wx.StaticText(pnl_option, label=GT("Homepage"), name="homepage")
    ti_homepage = TextAreaESS(pnl_option, name=txt_homepage.Name)

    txt_essential = wx.StaticText(pnl_option, label=GT("Essential"), name="essential")
    self.chk_essential = CheckBoxESS(pnl_option, name="essential")
    self.chk_essential.Default = False

    self.grp_input = (
      ti_package,
      ti_version,
      ti_maintainer,  # Maintainer must be listed before email
      ti_email,
      ti_section,
      ti_source,
      ti_homepage,
      ti_synopsis,
      self.ti_description,
      )

    self.grp_select = (
      sel_arch,
      sel_priority,
      )

    SetPageToolTips(self)

    # *** Event Handling *** #

    btn_open.Bind(wx.EVT_BUTTON, self.OnBrowse)
    btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
    btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewControl)

    # *** Layout *** #

    LEFT_BOTTOM = lyt.ALGN_LB
    RIGHT_CENTER = wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT

    # Buttons
    lyt_buttons = BoxSizer(wx.HORIZONTAL)
    lyt_buttons.Add(btn_open, 0)
    lyt_buttons.Add(btn_save, 0, wx.LEFT, 5)
    lyt_buttons.Add(btn_preview, 0, wx.LEFT, 5)

    # Required fields
    lyt_require = wx.FlexGridSizer(0, 4, 5, 5)
    lyt_require.AddGrowableCol(1)
    lyt_require.AddGrowableCol(3)

    lyt_require.AddMany((
      (txt_package, 0, RIGHT_CENTER|lyt.PAD_LT, 5),
      (ti_package, 0, wx.EXPAND|wx.TOP, 5),
      (txt_version, 0, RIGHT_CENTER|wx.TOP, 5),
      (ti_version, 0, wx.EXPAND|wx.TOP|wx.RIGHT, 5),
      (txt_maintainer, 0, RIGHT_CENTER|wx.LEFT, 5),
      (ti_maintainer, 0, wx.EXPAND),
      (txt_email, 0, RIGHT_CENTER, 5),
      (ti_email, 0, wx.EXPAND|wx.RIGHT, 5),
      (txt_arch, 0, RIGHT_CENTER|lyt.PAD_LB, 5),
      (sel_arch, 0, wx.BOTTOM, 5),
      ))

    pnl_require.SetSizer(lyt_require)
    pnl_require.SetAutoLayout(True)
    pnl_require.Layout()

    # Recommended fields
    lyt_recommend = wx.GridBagSizer()
    lyt_recommend.SetCols(4)
    lyt_recommend.AddGrowableCol(1)
    lyt_recommend.AddGrowableRow(3)

    lyt_recommend.Add(txt_section, (0, 2), flag=RIGHT_CENTER|lyt.PAD_TB, border=5)
    lyt_recommend.Add(ti_section, (0, 3),
        flag=wx.EXPAND|lyt.PAD_RTB, border=5)
    lyt_recommend.Add(txt_synopsis, (0, 0), (1, 2), LEFT_BOTTOM|wx.LEFT, 5)
    lyt_recommend.Add(ti_synopsis, (1, 0), (1, 2), wx.EXPAND|lyt.PAD_LR, 5)
    lyt_recommend.Add(txt_priority, (1, 2), flag=RIGHT_CENTER, border=5)
    lyt_recommend.Add(sel_priority, (1, 3), flag=wx.EXPAND|wx.RIGHT, border=5)
    lyt_recommend.Add(txt_description, (2, 0), (1, 2), LEFT_BOTTOM|lyt.PAD_LT, 5)
    lyt_recommend.Add(self.ti_description, (3, 0), (1, 4),
        wx.EXPAND|lyt.PAD_LR|wx.BOTTOM, 5)

    pnl_recommend.SetSizer(lyt_recommend)
    pnl_recommend.SetAutoLayout(True)
    pnl_recommend.Layout()

    # Optional fields
    lyt_option = wx.FlexGridSizer(0, 4, 5, 5)

    lyt_option.AddGrowableCol(1)
    lyt_option.AddGrowableCol(3)
    lyt_option.AddSpacer(5)
    lyt_option.AddSpacer(5)
    lyt_option.AddSpacer(5)
    lyt_option.AddSpacer(5)
    lyt_option.AddMany((
      (txt_source, 0, RIGHT_CENTER|wx.LEFT, 5),
      (ti_source, 0, wx.EXPAND),
      (txt_homepage, 0, RIGHT_CENTER, 5),
      (ti_homepage, 0, wx.EXPAND|wx.RIGHT, 5),
      (txt_essential, 0, RIGHT_CENTER|lyt.PAD_LB, 5),
      (self.chk_essential, 0, wx.BOTTOM, 5),
      ))

    pnl_option.SetSizer(lyt_option)
    pnl_option.SetAutoLayout(True)
    pnl_option.Layout()

    # Main background panel sizer
    # FIXME: Is background panel (pnl_bg) necessary
    lyt_bg = BoxSizer(wx.VERTICAL)
    lyt_bg.Add(lyt_buttons, 0, wx.ALIGN_RIGHT|wx.BOTTOM, 5)
    lyt_bg.Add(wx.StaticText(pnl_bg, label=GT("Required")), 0)
    lyt_bg.Add(pnl_require, 0, wx.EXPAND)
    lyt_bg.Add(wx.StaticText(pnl_bg, label=GT("Recommended")), 0, wx.TOP, 5)
    lyt_bg.Add(pnl_recommend, 1, wx.EXPAND)
    lyt_bg.Add(wx.StaticText(pnl_bg, label=GT("Optional")), 0, wx.TOP, 5)
    lyt_bg.Add(pnl_option, 0, wx.EXPAND)

    pnl_bg.SetAutoLayout(True)
    pnl_bg.SetSizer(lyt_bg)
    pnl_bg.Layout()

    # Page's main sizer
    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.AddSpacer(5)
    lyt_main.Add(pnl_bg, 1, wx.EXPAND|lyt.PAD_LR|wx.BOTTOM, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

  ## @override ui.page.Page.init
  def init(self):
    return True

  ## Retrieves information for control file export
  #
  #  @return
  #    A <b><i>tuple</i></b> containing the filename & a string representation of control file
  #    formatted for text output
  def Get(self):
    return self.GetCtrlInfo()

  ## Retrieves field values & formats into plain text for output to file
  #
  #  @return
  #      Control file text
  def GetCtrlInfo(self):
    pg_depends = ui.app.getPage(pgid.DEPENDS)

    ctrl_list = []
    synopsis = None
    description = None
    # Email will be set if maintainer changed to True
    maintainer = False

    # Text input fields
    for field in self.grp_input:
      field_name = field.GetName().title()
      field_value = field.GetValue()

      if FieldEnabled(field) and not strings.isEmpty(field_value):
        logger.debug(GT("Exporting {} field").format(field_name))

        # Strip leading & trailing spaces, tabs, & newlines
        field_value = field_value.strip(" \t\n")

        if field_name == "Synopsis":
          synopsis = "{}: {}".format("Description", field_value)
          continue

        if field_name == "Description":
          description = field_value.split("\n")
          for line_index in range(len(description)):
            # Remove trailing whitespace
            description[line_index] = description[line_index].rstrip()

            if strings.isEmpty(description[line_index]):
              # Empty lines are formatted with one space indentation & a period
              description[line_index] = " ."

            else:
              # All other lines are formatted with one space indentation
              description[line_index] = " {}".format(description[line_index])

          description = "\n".join(description)
          continue

        if field_name in ("Package", "Version"):
          # Don't allow whitespace in package name & version
          ctrl_list.append("{}: {}".format(field_name, "-".join(field_value.split(" "))))
          continue

        if field_name == "Email":
          if maintainer and ctrl_list:
            # Append email to end of maintainer string
            for ctrl_index in range(len(ctrl_list)):
              if ctrl_list[ctrl_index].startswith("Maintainer: "):
                logger.debug("Found maintainer")
                ctrl_list[ctrl_index] = "{} <{}>".format(ctrl_list[ctrl_index], field_value)
                break

          continue

        # Don't use 'continue' on this statement
        if field_name == "Maintainer":
          maintainer = True

        # The rest of the fields
        ctrl_list.append("{}: {}".format(field_name, field_value))

    # Selection box fields
    for field in self.grp_select:
      field_name = field.GetName().title()
      field_value = field.GetStringSelection()

      if FieldEnabled(field) and not strings.isEmpty(field_value):
        logger.debug(GT("Exporting {} field").format(field_name))

        # Strip leading & trailing spaces, tabs, & newlines
        field_value = field_value.strip(" \t\n")

        ctrl_list.append("{}: {}".format(field_name, field_value))

    if self.chk_essential.GetValue():
      ctrl_list.append("Essential: yes")

    # Dependencies & conflicts
    dep_list = [] # Depends
    pre_list = [] # Pre-Depends
    rec_list = [] # Recommends
    sug_list = [] # Suggests
    enh_list = [] # Enhances
    con_list = [] # Conflicts
    rep_list = [] # Replaces
    pvd_list = [] # Provides
    brk_list = [] # Breaks

    all_deps = {
      "Depends": dep_list,
      "Pre-Depends": pre_list,
      "Recommends": rec_list,
      "Suggests": sug_list,
      "Enhances": enh_list,
      "Conflicts": con_list,
      "Replaces": rep_list,
      "Provides": pvd_list,
      "Breaks": brk_list,
      }

    # Get amount of items to add
    dep_area = GetField(pg_depends, inputid.LIST)
    dep_count = dep_area.GetItemCount()
    count = 0
    while count < dep_count:
      # Get each item from dependencies page
      dep_type = dep_area.GetItem(count, 0).GetText()
      dep_val = dep_area.GetItem(count, 1).GetText()
      for item in all_deps:
        if dep_type == item:
          all_deps[item].append(dep_val)

      count += 1

    for item in all_deps:
      if len(all_deps[item]) != 0:
        ctrl_list.append("{}: {}".format(item, ", ".join(all_deps[item])))

    if synopsis:
      ctrl_list.append(synopsis)

      # Long description is only added if synopsis is not empty
      if description:
        ctrl_list.append(description)

    # dpkg requires empty newline at end of file
    return "\n".join(ctrl_list).strip("\n") + "\n"

  ## Saving project
  def GetSaveData(self):
    data = self.GetCtrlInfo()
    return "<<CTRL>>\n{}<</CTRL>>".format(data)

  ## @override ui.page.Page.toString
  def toString(self):
    return self.GetSaveData()

  ## Reads & parses page data from a formatted text file
  #
  #  @param filename
  #      File path to open
  #  @todo
  #    Use 'Set'/'SetPage' method
  def ImportFromFile(self, filename):
    logger.debug(GT("Importing file: {}".format(filename)))

    if not os.path.isfile(filename):
      ShowErrorDialog(GT("File does not exist: {}".format(filename)), linewrap=600)
      return dbrerrno.ENOENT

    file_text = readFile(filename)

    page_depends = ui.app.getPage(pgid.DEPENDS)

    # Reset fields to default before opening
    self.Reset()
    page_depends.Reset()

    depends_data = self.Set(file_text)
    page_depends.Set(depends_data)

  ## Displays a file open dialog for selecting a text file to read
  def OnBrowse(self, event=None):
    browse_dialog = GetFileOpenDialog(ui.app.getMainWindow(), GT("Open File"))
    if ShowDialog(browse_dialog):
      self.ImportFromFile(browse_dialog.GetPath())

  ## Creates a formatted preview of the control file text
  def OnPreviewControl(self, event=None):
    ctrl_info = self.GetCtrlInfo()

    preview = TextPreview(title=GT("Control File Preview"),
        text=ctrl_info, size=(600,400))

    ShowDialog(preview)

  ## Opens a file save dialog to export control file data
  def OnSave(self, event=None):
    # Get data to write to control file
    control = self.GetCtrlInfo()

    save_dialog = GetFileSaveDialog(ui.app.getMainWindow(), GT("Save Control Information"))
    save_dialog.SetFilename("control")

    if ShowDialog(save_dialog):
      # Be sure not to strip trailing newline (dpkg is picky)
      writeFile(save_dialog.GetPath(), control)

  ## @todo Doxygen
  #
  #  FIXME: Unfinished???
  def ReLayout(self):
    # Organize all widgets correctly
    lc_width = self.coauth.GetSize()[0]
    self.coauth.SetColumnWidth(0, lc_width/2)

  ## Resets all fields on page to default values
  def Reset(self):
    for I in self.grp_input:
      # Calling 'Clear' on ComboBox removes all options
      if isinstance(I, (wx.ComboBox, OwnerDrawnComboBox,)):
        I.SetValue(wx.EmptyString)

      else:
        I.Clear()

    for S in self.grp_select:
      S.SetSelection(S.Default)

    self.chk_essential.SetValue(self.chk_essential.Default)

  ## @override ui.page.Page.reset
  def reset(self):
    self.Reset()

  ## Fills page's fields with input data
  #
  #  @param data
  #    Text to be parsed for values
  #  @return
  #    Leftover text to fill out 'Dependecies' page fields
  def Set(self, data):
    # Decode to unicode string if input is byte string
    if isinstance(data, bytes):
      data = data.decode("utf-8")

    # Strip leading & trailing spaces, tabs, & newlines
    data = data.strip(" \t\n")
    control_data = data.split("\n")

    # Store Dependencies
    depends_containers = (
      ["Depends"],
      ["Pre-Depends"],
      ["Recommends"],
      ["Suggests"],
      ["Enhances"],
      ["Conflicts"],
      ["Replaces"],
      ["Provides"],
      ["Breaks"],
      )

    # Anything left over is dumped into this list then into the description field
    description = []

    for line in control_data:
      if ": " in line:
        key = line.split(": ")
        value = ": ".join(key[1:]) # For dependency fields that have ": " in description
        key = key[0]

        logger.debug("Found key: {}".format(key))

        if key == self.chk_essential.GetName().title() and value.lower() in ("yes", "true"):
          self.chk_essential.SetValue(True)

        # Catch Maintainer
        if key == "Maintainer":
          maintainer = value
          email = None

          if "<" in maintainer and maintainer.endswith(">"):
            maintainer = maintainer.split("<")
            email = maintainer[1].strip(" <>\t")
            maintainer = maintainer[0].strip(" \t")

          for I in self.grp_input:
            input_name = I.GetName().title()
            if input_name == "Maintainer":
              I.SetValue(maintainer)
              continue
            if input_name == "Email":
              I.SetValue(email)
              # NOTE: Maintainer should be listed before email in input list
              break
          continue

        # Set the rest of the input fields
        for I in self.grp_input:
          input_name = I.GetName().title()
          if input_name == "Synopsis":
            input_name = "Description"

          if key == input_name:
            I.SetValue(value)

        # Set the wx.Choice fields
        for S in self.grp_select:
          if key == S.GetName().title():
            S.SetStringSelection(value)

        # Set dependencies
        for container in depends_containers:
          if container and key == container[0]:
            for dep in value.split(", "):
              container.append(dep)
      else:
        # Description
        if line.startswith(" ."):
          # Add a blank line for lines beginning with a period
          description.append(wx.EmptyString)
          continue

        if not strings.isEmpty(line) and line.startswith(" "):
          # Remove the first space generated in the description
          description.append(line[1:])
          continue

        if not strings.isEmpty(line):
          description.append(line)

    # Put leftovers in long description
    self.ti_description.SetValue("\n".join(description))

    # Return depends data to parent to be sent to page_depends
    return depends_containers
