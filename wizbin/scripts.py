
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module wizbin.scripts

import os

import wx

import ui.app
import ui.page

from dbr.language      import GT
from globals           import tooltips
from globals.fileitem  import FileItem
from input.filelist    import BasicFileList
from input.markdown    import MarkdownDialog
from input.pathctrl    import PathCtrl
from input.text        import TextAreaPanelESS
from input.toggle      import CheckBox
from libdbr            import strings
from libdbr.fileio     import readFile
from libdbr.logger     import Logger
from libdebreate.ident import btnid
from libdebreate.ident import inputid
from libdebreate.ident import pgid
from ui.button         import CreateButton
from ui.dialog         import ConfirmationDialog
from ui.dialog         import DetailedMessageDialog
from ui.dialog         import ShowDialog
from ui.helper         import FieldEnabled
from ui.helper         import GetField
from ui.layout         import BoxSizer
from ui.panel          import BorderedPanel
from ui.style          import layout as lyt


logger = Logger(__name__)

ID_INST_PRE = wx.NewId()
ID_INST_POST = wx.NewId()
ID_RM_PRE = wx.NewId()
ID_RM_POST = wx.NewId()

id_definitions = {
  ID_INST_PRE: "preinst",
  ID_INST_POST: "postinst",
  ID_RM_PRE: "prerm",
  ID_RM_POST: "postrm",
}

## Scripts page
class Page(ui.page.Page):
  ## Constructor
  #
  #  @param parent
  #    Parent <b><i>wx.Window</i></b> instance
  def __init__(self, parent):
    super().__init__(parent, pgid.SCRIPTS)

    preinst = DebianScript(self, ID_INST_PRE)
    postinst = DebianScript(self, ID_INST_POST)
    prerm = DebianScript(self, ID_RM_PRE)
    postrm = DebianScript(self, ID_RM_POST)

    # Check boxes for choosing scripts
    chk_preinst = CheckBox(self, ID_INST_PRE, GT("Make this script"), name=GT("Pre-Install"))
    preinst.SetCheckBox(chk_preinst)
    chk_postinst = CheckBox(self, ID_INST_POST, GT("Make this script"), name=GT("Post-Install"))
    postinst.SetCheckBox(chk_postinst)
    chk_prerm = CheckBox(self, ID_RM_PRE, GT("Make this script"), name=GT("Pre-Remove"))
    prerm.SetCheckBox(chk_prerm)
    chk_postrm = CheckBox(self, ID_RM_POST, GT("Make this script"), name=GT("Post-Remove"))
    postrm.SetCheckBox(chk_postrm)

    for S in chk_preinst, chk_postinst, chk_prerm, chk_postrm:
      tooltips.register(S, "{} {}".format(S.GetName(),
          GT("script will be created from text below")))
      S.Bind(wx.EVT_CHECKBOX, self.OnToggleScripts)

    # Radio buttons for displaying between pre- and post- install scripts
    # FIXME: Names settings for tooltips are confusing
    rb_preinst = wx.RadioButton(self, preinst.GetId(), GT("Pre-Install"),
        name=preinst.FileName, style=wx.RB_GROUP)
    rb_postinst = wx.RadioButton(self, postinst.GetId(), GT("Post-Install"),
        name=postinst.FileName)
    rb_prerm = wx.RadioButton(self, prerm.GetId(), GT("Pre-Remove"),
        name=prerm.FileName)
    rb_postrm = wx.RadioButton(self, postrm.GetId(), GT("Post-Remove"),
        name=postrm.FileName)

    # TODO: Remove check boxes from lists (no longer needed)
    self.script_objects = (
      (preinst, chk_preinst, rb_preinst,),
      (postinst, chk_postinst, rb_postinst,),
      (prerm, chk_prerm, rb_prerm,),
      (postrm, chk_postrm, rb_postrm,),
      )

    for DS, CHK, RB in self.script_objects:
      CHK.Hide()

    # Set script text areas to default enabled/disabled setting
    self.OnToggleScripts()

    # *** Auto-Link *** #

    pnl_autolink = BorderedPanel(self)

    # Auto-Link path for new link
    txt_autolink = wx.StaticText(pnl_autolink, label=GT("Path"), name="target")
    self.ti_autolink = PathCtrl(pnl_autolink, value="/usr/bin", defaultValue="/usr/bin", warn=True)
    self.ti_autolink.SetName("target")
    self.ti_autolink.Default = self.ti_autolink.GetValue()

    # Auto-Link executables to be linked
    self.Executables = BasicFileList(pnl_autolink, size=(200, 200), hlExe=True,
        name="al list")
    if self.Executables.GetColumnCount() == 0:
      self.Executables.AppendColumn("")

    # Auto-Link import, generate and remove buttons
    btn_al_import = CreateButton(pnl_autolink, btnid.IMPORT)
    btn_al_remove = CreateButton(pnl_autolink, btnid.REMOVE)
    btn_al_generate = CreateButton(pnl_autolink, image="build")

    # Auto-Link help
    btn_help = CreateButton(pnl_autolink, btnid.HELP, size=64)

    # Initialize script display
    self.ScriptSelect(None)

    tooltips.SetPageToolTips(self)

    # *** Event Handling *** #

    for DS, CHK, RB in self.script_objects:
      RB.Bind(wx.EVT_RADIOBUTTON, self.ScriptSelect)

    btn_al_import.Bind(wx.EVT_BUTTON, self.ImportExes, id=btnid.IMPORT)
    btn_al_generate.Bind(wx.EVT_BUTTON, self.OnGenerate, id=wx.ID_ANY)
    btn_al_remove.Bind(wx.EVT_BUTTON, self.ImportExes, id=btnid.REMOVE)
    btn_help.Bind(wx.EVT_BUTTON, self.OnHelpButton, id=btnid.HELP)

    # *** Layout *** #

    # Organizing radio buttons
    lyt_sel_script = BoxSizer(wx.HORIZONTAL)
    lyt_sel_script.AddMany((
      (chk_preinst),
      (chk_postinst),
      (chk_prerm),
      (chk_postrm),
      ))

    lyt_sel_script.AddStretchSpacer(1)

    lyt_sel_script.AddMany((
      (rb_preinst),
      (rb_postinst),
      (rb_prerm),
      (rb_postrm),
      ))

    # Sizer for left half of scripts panel
    lyt_left = BoxSizer(wx.VERTICAL)
    lyt_left.Add(lyt_sel_script, 0, wx.EXPAND|wx.BOTTOM, 5)

    for DS, CHK, RB, in self.script_objects:
      lyt_left.Add(DS, 1, wx.EXPAND)

    # Auto-Link/Right side
    lyt_ti_autolink = BoxSizer(wx.HORIZONTAL)
    lyt_ti_autolink.Add(txt_autolink, 0, lyt.ALGN_C)
    lyt_ti_autolink.Add(self.ti_autolink, 1, lyt.ALGN_C)

    lyt_btn_autolink = BoxSizer(wx.HORIZONTAL)
    lyt_btn_autolink.Add(btn_al_import, 0)
    lyt_btn_autolink.Add(btn_al_remove, 0, lyt.PAD_LR, 5)
    lyt_btn_autolink.Add(btn_al_generate, 0)

    lyt_autolink = BoxSizer(wx.VERTICAL)
    lyt_autolink.Add(lyt_ti_autolink, 0, wx.EXPAND|lyt.PAD_LRT, 5)
    lyt_autolink.Add(self.Executables, 3, wx.EXPAND|lyt.PAD_LRT, 5)
    lyt_autolink.Add(lyt_btn_autolink, 0, lyt.ALGN_CH|wx.TOP, 5)
    lyt_autolink.Add(btn_help, 1, lyt.ALGN_C|wx.TOP|wx.BOTTOM, 5)

    pnl_autolink.SetSizer(lyt_autolink)
    pnl_autolink.SetAutoLayout(True)
    pnl_autolink.Layout()

    # Sizer for right half of scripts panel
    lyt_right = BoxSizer(wx.VERTICAL)
    # Line up panels to look even
    lyt_right.AddSpacer(32)
    lyt_right.Add(wx.StaticText(self,
        label=GT("Auto-Link Executables")), 0)
    lyt_right.Add(pnl_autolink, 0, wx.EXPAND)

    lyt_main = BoxSizer(wx.HORIZONTAL)
    lyt_main.Add(lyt_left, 1, wx.EXPAND|wx.ALL, 5)
    lyt_main.Add(lyt_right, 0, lyt.PAD_RB, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

  ## @override ui.page.Page.init
  def init(self):
    return True

  ## @todo Doxygen
  def ChangeBG(self, exists):
    if exists == False:
      self.ti_autolink.SetBackgroundColour((255, 0, 0, 255))

    else:
      self.ti_autolink.SetBackgroundColour((255, 255, 255, 255))

  ## Retrieves page data from fields
  def Get(self):
    scripts = {}

    for DS, CHK, RB in self.script_objects:
      if DS.IsChecked():
        scripts[DS.GetFilename()] = DS.GetValue()

    return scripts

  ## @todo Doxygen
  def GetSaveData(self):
    # Custom dictionary of scripts
    script_list = (
      (self.script_objects[0][0], self.script_objects[0][2], "PREINST"),
      (self.script_objects[1][0], self.script_objects[1][2], "POSTINST"),
      (self.script_objects[2][0], self.script_objects[2][2], "PRERM"),
      (self.script_objects[3][0], self.script_objects[3][2], "POSTRM")
    )

    # Create a list to return the data
    data = []
    for group in script_list:
      if group[0].IsChecked():
        data.append("<<{}>>\n1\n{}\n<</{}>>".format(group[2], group[0].GetValue(), group[2]))
      else:
        data.append("<<{}>>\n0\n<</{}>>".format(group[2], group[2]))

    return "<<SCRIPTS>>\n{}\n<</SCRIPTS>>".format("\n".join(data))

  ## @override ui.page.Page.toString
  def toString(self):
    return self.GetSaveData()

  ## Imports executables from files page for Auto-Link
  def ImportExes(self, event=None):
    event_id = event.GetId()
    if event_id == btnid.IMPORT:
      # First clear the Auto-Link display and the executable list
      self.Executables.Reset()

      file_list = GetField(pgid.FILES, inputid.LIST)
      exe_list = file_list.GetExecutables(False)

      for EXE in exe_list:
        INDEX = file_list.GetIndex(EXE)

        # Get the filename from the source
        file_name = file_list.GetFilename(INDEX)
        #file_name = EXE.GetBasename()
        # Where the file linked to will be installed
        # FIXME: FileItem.GetTarget() is not accurate
        file_target = file_list.GetTarget(EXE)

        self.Executables.Add(FileItem(file_name, os.path.join(file_target, file_name), ignore_timestamp=True))

      # retrieve nested executables
      # FIXME: symlinks may cause problems here
      for FITEM in file_list.GetFileItems():
        if FITEM.IsDirectory():
          # recurse into subdirectories
          toplevel = FITEM.GetPath()
          for ROOT, DIRS, FILES in os.walk(toplevel):
            for FILE in FILES:
              fullpath = os.path.join(ROOT, FILE)
              DIR = os.path.dirname(fullpath[len(toplevel):]).strip(os.sep)
              relpath = os.path.join(FITEM.GetBasename(), DIR, FILE).strip(os.sep)

              if os.path.isfile(fullpath) and os.access(fullpath, os.X_OK):
                fulltarget = os.path.join(FITEM.GetTarget(), relpath)

                # check if item is already added to list
                duplicate = False
                for EXE in exe_list:
                  existingtarget = os.path.join(EXE.GetTarget(), file_list.GetFilename(EXE))
                  if fulltarget == existingtarget:
                    duplicate = True
                    break

                if duplicate:
                  logger.warn("Not adding executable with duplicate target: {}".format(fulltarget))
                  continue

                logger.debug("Adding nested executable: {}".format(relpath))
                self.Executables.Add(
                    FileItem(relpath, os.path.join(FITEM.GetTarget(), relpath),
                        ignore_timestamp=True))

    elif event_id in (btnid.REMOVE, wx.WXK_DELETE):
      self.Executables.RemoveSelected()

  ## Reads & parses page data from a formatted text file
  #
  #  @param filename
  #    File path to open
  #  @todo
  #    FIXME: Should be done in DebianScript class method???
  def ImportFromFile(self, filename):
    logger.debug(GT("Importing script: {}").format(filename))

    script_name = filename.split("-")[-1]
    script_object = None

    for DS, CHK, RB in self.script_objects:
      if script_name == DS.GetFilename():
        script_object = DS

        break

    # Loading the actual text
    # FIXME: Should be done in class method
    if script_object != None:
      script_object.SetValue(readFile(filename))

  ## Checks if one or more scripts can be exported
  #
  #  @return
  #    <b><i>True</i></b> if page is ready for export
  def IsOkay(self):
    for DS, CHK, RB in self.script_objects:
      if DS.IsChecked():
        return True

    return False

  ## Creates scripts that link the executables
  def OnGenerate(self, event=None):
    main_window = ui.app.getMainWindow()

    # Get the amount of links to be created
    total = self.Executables.GetCount()

    if total > 0:
      non_empty_scripts = []

      for DS in self.script_objects[1][0], self.script_objects[2][0]:
        if not strings.isEmpty(DS.GetValue()):
          non_empty_scripts.append(DS.GetName())

      # Warn about overwriting previous post-install & pre-remove scripts
      if non_empty_scripts:
        warn_msg = GT("The following scripts will be overwritten if you continue: {}")
        warn_msg = "{}\n\n{}".format(warn_msg.format(", ".join(non_empty_scripts)), GT("Continue?"))

        overwrite = ConfirmationDialog(main_window, text=warn_msg)

        if not overwrite.Confirmed():
          return

        overwrite.Destroy()
        del warn_msg, overwrite

      # Get destination for link from Auto-Link input textctrl
      link_path = self.ti_autolink.GetValue()

      # Warn about linking in a directory that does not exist on the current filesystem
      if not os.path.isdir(link_path):
        warn_msg = GT("Path \"{}\" does not exist.")
        warn_msg = "{}\n\n{}".format(warn_msg, GT("Continue?"))

        overwrite = ConfirmationDialog(main_window, text=warn_msg.format(link_path))

        if not overwrite.Confirmed():
          return

        overwrite.Destroy()
        del warn_msg, overwrite

      #for CHK in self.script_objects[1][1], self.script_objects[2][1]:
      #  CHK.SetValue(True)
      for DS in self.script_objects[1][1], self.script_objects[2][1]:
        DS.SetChecked(True)

      # Update scripts' text area enabled status
      self.OnToggleScripts()

      # Create a list of commands to put into the script
      postinst_list = []
      prerm_list = []

      for INDEX in range(total):
        source_path = self.Executables.GetTarget(INDEX)
        filename = self.Executables.GetBasename(INDEX)

        if "." in filename:
          linkname = ".".join(filename.split(".")[:-1])
          link = "{}/{}".format(link_path, linkname)

        else:
          link = "{}/{}".format(link_path, filename)

        postinst_list.append("ln -fs \"{}\" \"{}\"".format(source_path, link))
        prerm_list.append("rm -f \"{}\"".format(link))

      postinst = "\n\n".join(postinst_list)
      prerm = "\n\n".join(prerm_list)

      self.script_objects[1][0].SetValue("#!/bin/bash -e\n\n{}".format(postinst))
      self.script_objects[2][0].SetValue("#!/bin/bash -e\n\n{}".format(prerm))

      DetailedMessageDialog(main_window, GT("Success"),
          text=GT("Post-Install and Pre-Remove scripts generated")).ShowModal()

  ## Displays an information dialog about Auto-Link when help button is pressed
  def OnHelpButton(self, event=None):
    al_help = MarkdownDialog(self, title=GT("Auto-Link Help"), readonly=True)
    description = GT("Debreate offers an Auto-Link Executables feature. What this does is finds any executables in the Files section and creates a postinst script that will create soft links to them in the specified path. This is useful if you are installing executables to a directory that is not found in the system PATH but want to access it from the PATH. For example, if you install an executable \"bar\" to the directory \"/usr/share/foo\" in order to execute \"bar\" from a terminal you would have to type /usr/share/foo/bar. Auto-Link can be used to place a link to \"bar\" somewhere on the system path like \"/usr/bin\". Then all that needs to be typed is bar to execute the program. Auto-Link also creates a prerm script that will delete the link upon removing the package.")
    instructions = GT("How to use Auto-Link: Press the IMPORT button to import any executables from the Files section. Then press the GENERATE button. Post-Install and Pre-Remove scripts will be created that will place symbolic links to your executables in the path displayed above.")

    al_help.SetText("{}\n\n{}".format(description, instructions))

    ShowDialog(al_help)

  ## @todo Doxygen
  def OnToggleScripts(self, event=None):
    logger.debug("Toggling scripts")

    for DS, CHK, RB in self.script_objects:
      DS.Enable(DS.IsChecked())

  ## Resets all fields on page to default values
  def Reset(self):
    for DS, CHK, RB in self.script_objects:
      DS.Reset()

    self.OnToggleScripts()

    self.script_objects[0][2].SetValue(True)
    self.ScriptSelect(None)

    self.ti_autolink.Reset()
    self.Executables.Reset()

  ## @override ui.page.Page.reset
  def reset(self):
    self.Reset()

  ## Changes current displayed script
  def ScriptSelect(self, event=None):
    for DS, CHK, RB in self.script_objects:
      if RB.GetValue():
        DS.Show()

      else:
        DS.Hide()

    self.Layout()

  ## Sets the page's fields
  #
  #  @param data
  #    Text to parse for field values
  def Set(self, data):
    chk_preinst = self.script_objects[0][1]
    chk_postinst = self.script_objects[1][1]
    chk_prerm = self.script_objects[2][1]
    chk_postrm = self.script_objects[3][1]

    preinst = (
      data.split("<<PREINST>>\n")[1].split("\n<</PREINST>>")[0].split("\n"),
      chk_preinst,
      )
    postinst = (
      data.split("<<POSTINST>>\n")[1].split("\n<</POSTINST>>")[0].split("\n"),
      chk_postinst,
      )
    prerm = (
      data.split("<<PRERM>>\n")[1].split("\n<</PRERM>>")[0].split("\n"),
      chk_prerm,
      )
    postrm = (
      data.split("<<POSTRM>>\n")[1].split("\n<</POSTRM>>")[0].split("\n"),
      chk_postrm,
      )

    for S, CHK in (preinst, postinst, prerm, postrm):
      if S[0].isnumeric() and int(S[0]) > 0:
        CHK.SetValue(True) # pylint: disable=no-member (false-positive on some systems)
        # Remove unneeded integer
        S.pop(0) # pylint: disable=no-member (false-positive on some systems)

    # Enable/Disable scripts text areas
    self.OnToggleScripts()

    if chk_preinst.GetValue():
      self.script_objects[0][0].SetValue("\n".join(preinst[0]))
    if chk_postinst.GetValue():
      self.script_objects[1][0].SetValue("\n".join(postinst[0]))
    if chk_prerm.GetValue():
      self.script_objects[2][0].SetValue("\n".join(prerm[0]))
    if chk_postrm.GetValue():
      self.script_objects[3][0].SetValue("\n".join(postrm[0]))

## Class defining a Debian package script
#
#  A script's filename is one of 'preinst', 'prerm',
#  'postinst', or 'postrm'. Scripts are stored in the
#  (FIXME: Don't remember section name) section of the
#  package & are executed in the order dictated by the
#  naming convention:
#    'Pre Install', 'Pre Remove/Uninstall',
#    'Post Install', & 'Post Remove/Uninstall'.
class DebianScript(wx.Panel):
  ## Constructor
  #
  #  @param parent
  #    The <b><i>wx.Window</i></b> parent instance
  #  @param scriptId
  #    Unique <b><i>integer</i></b> identifier for script
  def __init__(self, parent, scriptId):
    wx.Panel.__init__(self, parent, scriptId)

    ## Filename used for exporting script
    self.FileName = id_definitions[scriptId].lower()

    ## String name used for display in the application
    self.ScriptName = None
    self.SetScriptName()

    self.ScriptBody = TextAreaPanelESS(self, self.GetId(), monospace=True)
    self.ScriptBody.EnableDropTarget()

    self.Check = None

    # *** Layout *** #

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.Add(self.ScriptBody, 1, wx.EXPAND|wx.TOP, 5)

    self.SetSizer(lyt_main)
    self.SetAutoLayout(True)
    self.Layout()

    # Scripts are hidden by default
    self.Hide()

  ## @todo Doxygen
  def Disable(self):
    return self.Enable(False)

  ## @todo Doxygen
  def Enable(self, enable=True):
    return self.ScriptBody.Enable(enable)

  ## Retrieves the filename to use for exporting
  #
  #  @return
  #    Script filename
  def GetFilename(self):
    return self.FileName

  ## Retrieves the script's name for display
  #
  #  @return
  #    <b><i>String</i></b> representation of script's name
  def GetName(self):
    return self.ScriptName

  ## Retrieves the text body of the script
  def GetValue(self):
    return self.ScriptBody.GetValue()

  ## @todo Doxygen
  def Hide(self):
    if self.Check:
      self.Check.Hide()

    return wx.Panel.Hide(self)

  ## @todo Doxygen
  def IsChecked(self):
    # FIXME: Should check if field is wx.CheckBox
    if self.Check:
      return self.Check.IsChecked()

    return False

  ## @todo Doxygen
  def IsEnabled(self):
    return FieldEnabled(self.ScriptBody)

  ## Checks if the script is used & can be exporteds.
  #
  #  The text area is checked &, if not empty, signifies that the user want to export the script.
  #
  #  @return
  #    `True` if text area is not empty, `False` otherwise.
  def IsOkay(self):
    return not strings.isEmpty(self.ScriptBody.GetValue())

  ## Resets all members to default values
  def Reset(self):
    self.ScriptBody.Clear()
    if self.Check:
      self.Check.Reset()

  ## @todo Doxygen
  def SetCheckBox(self, check_box):
    self.Check = check_box

  ## @todo Doxygen
  def SetChecked(self, value=True):
    self.Check.SetValue(value)

  ## Sets the name of the script to be displayed
  #
  #  Sets the displayed script name to a value of either 'Pre Install',
  #  'Pre Uninstall', 'Post Install', or 'Post Uninstall'. 'self.FileName'
  #  is used to determine the displayed name.
  #
  #  @todo
  #    Add strings to GetText translations
  def SetScriptName(self):
    prefix = None
    suffix = None

    if "pre" in self.FileName:
      prefix = "Pre"
      suffix = self.FileName.split("pre")[1]
    elif "post" in self.FileName:
      prefix = "Post"
      suffix = self.FileName.split("post")[1]

    if suffix.lower() == "inst":
      suffix = "Install"
    elif suffix.lower() == "rm":
      suffix = "Uninstall"

    if (prefix != None) and (suffix != None):
      self.ScriptName = GT("{}-{}".format(prefix, suffix))

  ## Fills the script
  #
  #  @param value
  #    Text to be entered into the script body
  def SetValue(self, value):
    self.ScriptBody.SetValue(value)

  ## @todo Doxygen
  def Show(self):
    if self.Check:
      self.Check.Show()
    return wx.Panel.Show(self)
