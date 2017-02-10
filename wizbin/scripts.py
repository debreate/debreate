# -*- coding: utf-8 -*-

## \package wizbin.scripts

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.language       import GT
from dbr.log            import Logger
from globals.errorcodes import ERR_DIR_NOT_AVAILABLE
from globals.errorcodes import ERR_FILE_WRITE
from globals.errorcodes import dbrerrno
from globals.fileio     import FileItem
from globals.fileio     import GetFiles
from globals.fileio     import ReadFile
from globals.fileio     import WriteFile
from globals.ident      import genid
from globals.ident      import inputid
from globals.ident      import page_ids
from globals.ident      import pgid
from globals.paths      import ConcatPaths
from globals.strings    import GS
from globals.strings    import TextIsEmpty
from globals.tooltips   import SetPageToolTips
from input.list         import BasicFileList
from input.markdown     import MarkdownDialog
from input.pathctrl     import PathCtrl
from input.select       import ComboBoxESS
from input.text         import TextAreaPanelESS
from ui.button          import ButtonBuild
from ui.button          import ButtonHelp64
from ui.button          import ButtonImport
from ui.button          import ButtonRemove
from ui.dialog          import ConfirmationDialog
from ui.dialog          import DetailedMessageDialog
from ui.dialog          import ShowDialog
from ui.layout          import BoxSizer
from ui.panel           import BorderedPanel
from ui.style           import layout as lyt
from wiz.helper         import GetField
from wiz.helper         import GetMainWindow
from wiz.wizard         import WizardPage


ID_INST_PRE = wx.NewId()
ID_INST_POST = wx.NewId()
ID_RM_PRE = wx.NewId()
ID_RM_POST = wx.NewId()

id_definitions = {
    ID_INST_PRE: u'preinst',
    ID_INST_POST: u'postinst',
    ID_RM_PRE: u'prerm',
    ID_RM_POST: u'postrm',
}


## Scripts page
class Page(WizardPage):
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.SCRIPTS)
        
        preinst = DebianScript(self, ID_INST_PRE)
        postinst = DebianScript(self, ID_INST_POST)
        prerm = DebianScript(self, ID_RM_PRE)
        postrm = DebianScript(self, ID_RM_POST)
        
        # Radio buttons for displaying between pre- and post- install scripts
        # FIXME: Names settings for tooltips are confusing
        rb_preinst = wx.RadioButton(self, preinst.GetId(), preinst.GetName(),
                name=preinst.FileName, style=wx.RB_GROUP)
        rb_postinst = wx.RadioButton(self, postinst.GetId(), postinst.GetName(),
                name=postinst.FileName)
        rb_prerm = wx.RadioButton(self, prerm.GetId(), prerm.GetName(),
                name=prerm.FileName)
        rb_postrm = wx.RadioButton(self, postrm.GetId(), postrm.GetName(),
                name=postrm.FileName)
        
        self.script_objects = (
            (preinst, rb_preinst,),
            (postinst, rb_postinst,),
            (prerm, rb_prerm,),
            (postrm, rb_postrm,),
            )
        
        # *** Auto-Link *** #
        
        pnl_autolink = BorderedPanel(self)
        
        # Auto-Link path for new link
        txt_autolink = wx.StaticText(pnl_autolink, label=GT(u'Path'), name=u'target')
        self.ti_autolink = PathCtrl(pnl_autolink, value=u'/usr/bin', warn=True)
        self.ti_autolink.SetName(u'target')
        self.ti_autolink.Default = self.ti_autolink.GetValue()
        
        # Auto-Link executables to be linked
        self.Executables = BasicFileList(pnl_autolink, size=(200, 200), hlExes=True,
                name=u'al list')
        
        # Auto-Link import, generate and remove buttons
        btn_al_import = ButtonImport(pnl_autolink)
        btn_al_remove = ButtonRemove(pnl_autolink)
        btn_al_generate = ButtonBuild(pnl_autolink)
        
        # Auto-Link help
        btn_help = ButtonHelp64(pnl_autolink)
        
        # Initialize script display
        self.ScriptSelect(None)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        for DS, RB in self.script_objects:
            wx.EVT_RADIOBUTTON(RB, RB.GetId(), self.ScriptSelect)
        
        wx.EVT_BUTTON(btn_al_import, genid.IMPORT, self.ImportExes)
        wx.EVT_BUTTON(btn_al_generate, wx.ID_ANY, self.OnGenerate)
        wx.EVT_BUTTON(btn_al_remove, wx.ID_REMOVE, self.ImportExes)
        wx.EVT_BUTTON(btn_help, wx.ID_HELP, self.OnHelpButton)
        
        # *** Layout *** #
        
        # Organizing radio buttons
        lyt_sel_script = BoxSizer(wx.HORIZONTAL)
        lyt_sel_script.AddMany((
            (rb_preinst),
            (rb_postinst),
            (rb_prerm),
            (rb_postrm),
            ))
        
        # Sizer for left half of scripts panel
        lyt_left = BoxSizer(wx.VERTICAL)
        lyt_left.Add(lyt_sel_script, 0, wx.EXPAND|wx.BOTTOM, 5)
        
        for DS, RB in self.script_objects:
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
        lyt_autolink.Add(lyt_btn_autolink, 0, lyt.ALGN_CH)
        lyt_autolink.Add(btn_help, 1, lyt.ALGN_C)
        
        pnl_autolink.SetSizer(lyt_autolink)
        pnl_autolink.SetAutoLayout(True)
        pnl_autolink.Layout()
        
        # Sizer for right half of scripts panel
        lyt_right = BoxSizer(wx.VERTICAL)
        # Line up panels to look even
        lyt_right.AddSpacer(44)
        lyt_right.Add(wx.StaticText(self, label=GT(u'Auto-Link Executables')),
                0, lyt.ALGN_LB)
        lyt_right.Add(pnl_autolink, 0, wx.EXPAND)
        
        lyt_main = BoxSizer(wx.HORIZONTAL)
        lyt_main.Add(lyt_left, 1, wx.EXPAND|wx.ALL, 5)
        lyt_main.Add(lyt_right, 0, wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Collects page's data & exports it to file
    #
    #  \param target
    #    Absolute filename path for output
    #  \see wiz.wizard.WizardPage.Export
    def Export(self, out_dir):
        return_code = (0, None)
        
        for DS, RB in self.script_objects:
            if DS.IsOkay():
                return_code = DS.Export(out_dir, False)
                
                if return_code[0]:
                    return return_code
        
        return return_code
    
    
    ## Exports data for the build process
    #
    #  \param target
    #    Filename path to be exported
    def ExportBuild(self, stage):
        stage = u'{}/DEBIAN'.format(stage).replace(u'//', u'/')
        
        if not os.path.isdir(stage):
            os.makedirs(stage)
        
        # FIXME: Should have error check
        for DS, RB in self.script_objects:
            if DS.IsOkay():
                DS.Export(stage, build=True)
        
        return (dbrerrno.SUCCESS, None)
    
    
    ## Retrieves page data from fields
    def Get(self):
        scripts = {}
        
        for DS, RB in self.script_objects:
            if not TextIsEmpty(DS.GetValue()):
                scripts[DS.GetFilename()] = DS.GetValue()
        
        return scripts
    
    
    ## Imports executables from files page for Auto-Link
    def ImportExes(self, event=None):
        event_id = event.GetId()
        if event_id == genid.IMPORT:
            # First clear the Auto-Link display and the executable list
            self.Executables.Reset()
            
            # Get executables from "files" tab
            file_list = GetField(pgid.FILES, inputid.LIST)
            
            for INDEX in range(file_list.GetItemCount()):
                # Get the filename from the source
                file_name = file_list.GetFilename(INDEX, basename=True)
                file_path = file_list.GetPath(INDEX)
                # Where the file linked to will be installed
                file_target = file_list.GetItem(INDEX, 1)
                
                # Walk directory to find executables
                if file_list.IsDirectory(INDEX):
                    for EXE in GetFiles(file_path, os.X_OK):
                        self.Executables.Append(FileItem(EXE, file_target))
                
                # Search for executables (distinguished by red text)
                elif file_list.IsExecutable(INDEX):
                    try:
                        # If destination doesn't start with "/" do not include executable
                        if file_target.GetText()[0] == u'/':
                            if file_target.GetText()[-1] == u'/' or file_target.GetText()[-1] == u' ':
                                # In case the full path of the destination is "/" keep going
                                if len(file_target.GetText()) == 1:
                                    dest_path = u''
                                
                                else:
                                    search = True
                                    # Set the number of spaces to remove from dest path in case of multiple "/"
                                    slashes = 1
                                    while search:
                                        # Find the number of slashes/spaces at the end of the filename
                                        endline = slashes - 1
                                        if file_target.GetText()[-slashes] == u'/' or file_target.GetText()[-slashes] == u' ':
                                            slashes += 1
                                        
                                        else:
                                            dest_path = file_target.GetText()[:-endline]
                                            search = False
                            
                            else:
                                dest_path = file_target.GetText()
                            
                            self.Executables.Append(file_name, dest_path)
                        
                        else:
                            Logger.Warn(__name__, u'{}: The executables destination is not valid'.format(__name__))
                    
                    except IndexError:
                        Logger.Warn(__name__, u'{}: The executables destination is not available'.format(__name__))
        
        elif event_id in (wx.ID_REMOVE, wx.WXK_DELETE):
            self.Executables.RemoveSelected()
    
    
    ## Reads & parses page data from a formatted text file
    #
    #  FIXME: Should be done in DebianScript class method???
    #
    #  \param filename
    #    File path to open
    def ImportFromFile(self, filename):
        Logger.Debug(__name__, GT(u'Importing script: {}').format(filename))
        
        script_name = filename.split(u'-')[-1]
        script_object = None
        
        for DS, RB in self.script_objects:
            if script_name == DS.GetFilename():
                script_object = DS
                
                break
        
        # Loading the actual text
        # FIXME: Should be done in class method
        if script_object != None:
            script_data = ReadFile(filename, split=True, convert=list)
            
            # FIXME: this should be global variable
            shebang = u'/bin/bash'
            
            remove_indexes = 0
            
            if u'#!' == script_data[0][:2]:
                shebang = script_data[0][2:]
                script_data.remove(script_data[0])
            
            # Remove empty lines from beginning of script
            for L in script_data:
                if not TextIsEmpty(L):
                    break
                
                remove_indexes += 1
            
            for I in reversed(range(remove_indexes)):
                script_data.remove(script_data[I])
            
            script_data = u'\n'.join(script_data)
            
            script_object.SetShell(shebang, True)
            script_object.SetValue(script_data)
    
    
    ## Checks if one or more scripts can be exported
    #
    #  \return
    #    <b><i>True</i></b> if page is ready for export
    def IsOkay(self):
        for DS, RB in self.script_objects:
            if DS.IsOkay():
                return True
    
    
    ## Creates scripts that link the executables
    def OnGenerate(self, event=None):
        main_window = GetMainWindow()
        
        # Get the amount of links to be created
        total = self.Executables.GetCount()
        
        if total > 0:
            non_empty_scripts = []
            
            for DS in self.script_objects[1][0], self.script_objects[2][0]:
                if not TextIsEmpty(DS.GetValue()):
                    non_empty_scripts.append(DS.GetName())
            
            # Warn about overwriting previous post-install & pre-remove scripts
            if non_empty_scripts:
                warn_msg = GT(u'The following scripts will be overwritten if you continue: {}')
                warn_msg = u'{}\n\n{}'.format(warn_msg.format(u', '.join(non_empty_scripts)), GT(u'Continue?'))
                
                overwrite = ConfirmationDialog(main_window, text=warn_msg)
                
                if not overwrite.Confirmed():
                    return
                
                overwrite.Destroy()
                del warn_msg, overwrite
            
            # Get destination for link from Auto-Link input textctrl
            link_path = self.ti_autolink.GetValue()
            
            # Warn about linking in a directory that does not exist on the current filesystem
            if not os.path.isdir(link_path):
                warn_msg = GT(u'Path "{}" does not exist.')
                warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))
                
                overwrite = ConfirmationDialog(main_window, text=warn_msg.format(link_path))
                
                if not overwrite.Confirmed():
                    return
                
                overwrite.Destroy()
                del warn_msg, overwrite
            
            # Create a list of commands to put into the script
            postinst_list = []
            prerm_list = []
            
            for INDEX in range(total):
                source_path = self.Executables.GetPath(INDEX)
                filename = self.Executables.GetBasename(INDEX)
                
                if u'.' in filename:
                    linkname = u'.'.join(filename.split(u'.')[:-1])
                    link = u'{}/{}'.format(link_path, linkname)
                
                else:
                    link = u'{}/{}'.format(link_path, filename)
                
                postinst_list.append(u'ln -fs "{}" "{}"'.format(source_path, link))
                prerm_list.append(u'rm -f "{}"'.format(link))
            
            postinst = u'\n\n'.join(postinst_list)
            prerm = u'\n\n'.join(prerm_list)
            
            self.script_objects[1][0].SetValue(postinst)
            self.script_objects[2][0].SetValue(prerm)
            
            DetailedMessageDialog(main_window, GT(u'Success'),
                    text=GT(u'Post-Install and Pre-Remove scripts generated')).ShowModal()
    
    
    ## Displays an information dialog about Auto-Link when help button is pressed
    def OnHelpButton(self, event=None):
        al_help = MarkdownDialog(self, title=GT(u'Auto-Link Help'))
        description = GT(u'Debreate offers an Auto-Link Executables feature. What this does is finds any executables in the Files section and creates a postinst script that will create soft links to them in the specified path. This is useful if you are installing executables to a directory that is not found in the system PATH but want to access it from the PATH. For example, if you install an executable "bar" to the directory "/usr/share/foo" in order to execute "bar" from a terminal you would have to type /usr/share/foo/bar. Auto-Link can be used to place a link to "bar" somewhere on the system path like "/usr/bin". Then all that needs to be typed is bar to execute the program. Auto-Link also creates a prerm script that will delete the link upon removing the package.')
        instructions = GT(u'How to use Auto-Link: Press the IMPORT button to import any executables from the Files section. Then press the GENERATE button. Post-Install and Pre-Remove scripts will be created that will place symbolic links to your executables in the path displayed above.')
        
        al_help.SetText(u'{}\n\n{}'.format(description, instructions))
        
        ShowDialog(al_help)
    
    
    ## Resets all fields on page to default values
    def Reset(self):
        for DS, RB in self.script_objects:
            DS.Reset()
        
        self.ti_autolink.Reset()
        self.Executables.Reset()
    
    
    ## Changes current displayed script
    def ScriptSelect(self, event=None):
        for DS, RB in self.script_objects:
            if RB.GetValue():
                DS.Show()
            
            else:
                DS.Hide()
        
        self.Layout()
    
    
    ## Sets the page's fields
    #
    #  \param data
    #    Text to parse for field values
    def Set(self, data):
        preinst = data.split(u'<<PREINST>>\n')[1].split(u'\n<</PREINST>>')[0]
        postinst = data.split(u'<<POSTINST>>\n')[1].split(u'\n<</POSTINST>>')[0]
        prerm = data.split(u'<<PRERM>>\n')[1].split(u'\n<</PRERM>>')[0]
        postrm = data.split(u'<<POSTRM>>\n')[1].split(u'\n<</POSTRM>>')[0]
        
        def format_script(script):
            return u'\n'.join(script.split(u'\n')[2:])  # Use '2' to remove first two lines
        
        if GS(preinst[0]).isnumeric():
            if int(preinst[0]):
                self.script_objects[0][0].SetValue(format_script(preinst))
        
        if GS(postinst[0]).isnumeric():
            if int(postinst[0]):
                self.script_objects[1][0].SetValue(format_script(postinst))
        
        if GS(prerm[0]).isnumeric():
            if int(prerm[0]):
                self.script_objects[2][0].SetValue(format_script(prerm))
        
        if GS(postrm[0]).isnumeric():
            if int(postrm[0]):
                self.script_objects[3][0].SetValue(format_script(postrm))



## Descriptions for each available pre-defined shell
#  
#  TODO: Add strings to GetText translations
shell_descriptions = {
    u'sh': GT(u'UNIX Bourne shell'),
    u'bash': GT(u'GNU Bourne Again shell'),
    u'ksh' or u'pdksh': GT(u'Korn shell'),
    u'csh': GT(u'C shell'),
    u'tcsh': GT(u'Tenex C shell (Advanced C shell)'),
    u'zsh': GT(u'Z shell'),
}


## Class defining a Debian package script
#  
#  A script's filename is one of 'preinst', 'prerm',
#    'postinst', or 'postrm'. Scripts are stored in the
#    (FIXME: Don't remember section name) section of the package & are executed in the
#    order dictated by the naming convention:
#    'Pre Install', 'Pre Remove/Uninstall',
#    'Post Install', & 'Post Remove/Uninstall'.
class DebianScript(wx.Panel):
    ## Constructor
    #
    #  \param parent
    #    The <b><i>wx.Window</i></b> parent instance
    #  \param scriptId
    #    Unique <b><i>integer</i></b> identifier for script
    def __init__(self, parent, scriptId):
        wx.Panel.__init__(self, parent, scriptId)
        
        ## Filename used for exporting script
        self.FileName = id_definitions[scriptId].lower()
        
        ## String name used for display in the application
        self.ScriptName = None
        self.SetScriptName()
        
        shell_options = []
        shell_options.append(u'/bin/sh')  # Place /bin/sh as first item
        for P in u'/bin/', u'/usr/bin/', u'/usr/bin/env ':
            for S in sorted(shell_descriptions, key=GS.lower):
                if S == u'sh':
                    pass
                
                else:
                    shell_options.append(P + S)
        
        self.Shell = ComboBoxESS(self, self.GetId(), choices=shell_options, monospace=True,
                defaultValue=u'/bin/bash')
        
        self.ScriptBody = TextAreaPanelESS(self, self.GetId(), monospace=True)
        self.ScriptBody.EnableDropTarget()
        
        # *** Layout *** #
        
        lyt_shell = BoxSizer(wx.HORIZONTAL)
        lyt_shell.Add(wx.StaticText(self, label=u'#!'), 0, lyt.ALGN_CV|wx.RIGHT, 5)
        lyt_shell.Add(self.Shell, 1)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(lyt_shell, 0)
        lyt_main.Add(self.ScriptBody, 1, wx.EXPAND|wx.TOP, 5)
        
        self.SetSizer(lyt_main)
        self.SetAutoLayout(True)
        self.Layout()
        
        # Scripts are hidden by default
        self.Hide()
    
    
    ## Exports the script to a text file
    #
    #  \param out_dir
    #    Target directory of output file
    #  \param executable
    #    If <b><i>True</i></b>, sets the files executable bit
    #  \param build
    #    If <b><i>True</i></b>, format output for final build
    def Export(self, out_dir, executable=True, build=False):
        if not os.path.isdir(out_dir):
            Logger.Error(__name__, GT(u'Directory not available: {}'.format(out_dir)))
            
            return (ERR_DIR_NOT_AVAILABLE, __name__)
        
        if build:
            absolute_filename = ConcatPaths((out_dir, self.FileName))
        
        else:
            filename = u'{}-{}'.format(page_ids[self.Parent.GetId()].upper(), self.FileName)
            absolute_filename = ConcatPaths((out_dir, filename))
        
        script_text = u'{}\n\n{}'.format(self.GetShebang(), self.ScriptBody.GetValue())
        
        WriteFile(absolute_filename, script_text)
        
        if not os.path.isfile(absolute_filename):
            Logger.Error(__name__, GT(u'Could not write to file: {}'.format(absolute_filename)))
            
            return (ERR_FILE_WRITE, __name__)
        
        if executable:
            os.chmod(absolute_filename, 0755)
        
        return (0, None)
    
    
    ## Retrieves the filename to use for exporting
    #
    #  \return
    #    Script filename
    def GetFilename(self):
        return self.FileName
    
    
    ## Retrieves the script's name for display
    #
    #  \return
    #    <b><i>String</i></b> representation of script's name
    def GetName(self):
        return self.ScriptName
    
    
    ## Retrieves the description of a shell for display
    #
    #  \return
    #    Description or <b><i>None</i></b> if using custom shell
    def GetSelectedShellDescription(self):
        selected_shell = self.Shell.GetValue()
        
        if selected_shell in shell_descriptions:
            return shell_descriptions[selected_shell]
        
        return None
    
    
    ## Retrieves the shebang/shell line
    def GetShebang(self):
        shell = self.Shell.GetValue()
        
        if shell.startswith(u'/usr/bin/env '):
            shell = u'#!{}\nset -e'.format(shell)
        
        else:
            shell = u'#!{} -e'.format(shell)
        
        return shell
    
    
    ## Retrieves the text body of the script
    def GetValue(self):
        return self.ScriptBody.GetValue()
    
    
    ## Checks if the script is used & can be exported
    #
    #  The text area is checked &, if not empty, signifies that
    #  the user want to export the script.
    #
    #  \return
    #    <b><i>True</i></b> if text area is not empty, <b><i>False</i></b> otherwise
    def IsOkay(self):
        return not TextIsEmpty(self.ScriptBody.GetValue())
    
    
    ## Resets all members to default values
    def Reset(self):
        self.Shell.SetStringSelection(self.Shell.GetDefaultValue())
        self.ScriptBody.Clear()
    
    
    ## Sets the name of the script to be displayed
    #
    #  Sets the displayed script name to a value of either 'Pre Install',
    #  'Pre Uninstall', 'Post Install', or 'Post Uninstall'. 'self.FileName'
    #  is used to determine the displayed name.
    #  TODO: Add strings to GetText translations
    def SetScriptName(self):
        prefix = None
        suffix = None
        
        if u'pre' in self.FileName:
            prefix = u'Pre'
            suffix = self.FileName.split(u'pre')[1]
        
        elif u'post' in self.FileName:
            prefix = u'Post'
            suffix = self.FileName.split(u'post')[1]
        
        if suffix.lower() == u'inst':
            suffix = u'Install'
        
        elif suffix.lower() == u'rm':
            suffix = u'Uninstall'
        
        if (prefix != None) and (suffix != None):
            self.ScriptName = GT(u'{}-{}'.format(prefix, suffix))
    
    
    ## Sets the shell/shebang line to use for script
    #
    #  \param shell
    #    Path to desired shell
    #  \param forced
    #    ???
    def SetShell(self, shell, forced=False):
        if forced:
            self.Shell.SetValue(shell)
            return
        
        self.Shell.SetStringSelection(shell)
    
    
    ## Fills the script
    #
    #  \param value
    #    Text to be entered into the script body
    def SetValue(self, value):
        self.ScriptBody.SetValue(value)
