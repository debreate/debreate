# -*- coding: utf-8 -*-

## \package wiz_bin.scripts

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.buttons            import ButtonBuild
from dbr.buttons            import ButtonImport
from dbr.buttons            import ButtonQuestion64
from dbr.buttons            import ButtonRemove
from dbr.language           import GT
from dbr.listinput          import ListCtrlPanel
from dbr.log                import Logger
from dbr.markdown           import MarkdownDialog
from dbr.panel              import BorderedPanel
from dbr.pathctrl           import PATH_WARN
from dbr.pathctrl           import PathCtrl
from dbr.selectinput        import ComboBox
from dbr.textinput          import TextAreaPanel
from dbr.wizard             import WizardPage
from globals                import ident
from globals.errorcodes     import ERR_DIR_NOT_AVAILABLE
from globals.errorcodes     import ERR_FILE_WRITE
from globals.errorcodes     import dbrerrno
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.ident          import page_ids
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetTopWindow


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
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.SCRIPTS)
        
        self.preinst = DebianScript(self, ID_INST_PRE)
        self.postinst = DebianScript(self, ID_INST_POST)
        self.prerm = DebianScript(self, ID_RM_PRE)
        self.postrm = DebianScript(self, ID_RM_POST)
        
        # Radio buttons for displaying between pre- and post- install scripts
        # FIXME: Names settings for tooltips are confusing
        rb_preinst = wx.RadioButton(self, self.preinst.GetId(), self.preinst.GetName(),
                name=self.preinst.script_filename, style=wx.RB_GROUP)
        rb_postinst = wx.RadioButton(self, self.postinst.GetId(), self.postinst.GetName(),
                name=self.postinst.script_filename)
        rb_prerm = wx.RadioButton(self, self.prerm.GetId(), self.prerm.GetName(),
                name=self.prerm.script_filename)
        rb_postrm = wx.RadioButton(self, self.postrm.GetId(), self.postrm.GetName(),
                name=self.postrm.script_filename)
        
        self.script_objects = (
            (self.preinst, rb_preinst),
            (self.postinst, rb_postinst),
            (self.prerm, rb_prerm),
            (self.postrm, rb_postrm),
        )
        
        # *** Auto-Link *** #
        
        pnl_autolink = BorderedPanel(self)
        
        # Executable list - generate button will make scripts to link to files in this list
        self.lst_executables = []
        
        # Auto-Link path for new link
        txt_autolink = wx.StaticText(pnl_autolink, label=GT(u'Path'), name=u'target')
        self.ti_autolink = PathCtrl(pnl_autolink, value=u'/usr/bin', ctrl_type=PATH_WARN)
        self.ti_autolink.SetName(u'target')
        self.ti_autolink.default = self.ti_autolink.GetValue()
        
        # Auto-Link executables to be linked
        self.executables = ListCtrlPanel(pnl_autolink, size=(200,200), name=u'al list')
        self.executables.SetSingleStyle(wx.LC_SINGLE_SEL)
        #self.executables.InsertColumn(0, u'')
        
        # Auto-Link import, generate and remove buttons
        btn_al_import = ButtonImport(pnl_autolink)
        btn_al_remove = ButtonRemove(pnl_autolink)
        btn_al_generate = ButtonBuild(pnl_autolink)
        
        # Text explaining Auto-Link
        '''txt_autolink = wx.StaticText(self, -1, 'How to use Auto-Link: Press the "import" button to \
import any executables from the "files" tab.  Then press the "generate" button.  "postinst" and "prerm" \
scripts will be created that will place a symbolic link to your executables in the path displayed above.')
        txt_autolink.Wrap(210)'''
        
        # Auto-Link help
        btn_help = ButtonQuestion64(pnl_autolink)
        
        # Initialize script display
        self.ScriptSelect(None)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        for S, RB in self.script_objects:
            wx.EVT_RADIOBUTTON(RB, RB.GetId(), self.ScriptSelect)
        
        #wx.EVT_KEY_UP(self.ti_autolink, ChangeInput)
        
        wx.EVT_BUTTON(btn_al_import, ident.IMPORT, self.ImportExe)
        wx.EVT_BUTTON(btn_al_generate, -1, self.OnGenerate)
        btn_al_remove.Bind(wx.EVT_BUTTON, self.ImportExe)
        
        wx.EVT_BUTTON(btn_help, wx.ID_HELP, self.OnHelpButton)
        
        # *** Layout *** #
        
        # Organizing radio buttons
        lyt_sel_script = wx.BoxSizer(wx.HORIZONTAL)
        lyt_sel_script.AddMany((
            (rb_preinst),
            (rb_postinst),
            (rb_prerm),
            (rb_postrm),
            ))
        
        # Sizer for left half of scripts panel
        lyt_left = wx.BoxSizer(wx.VERTICAL)
        
        lyt_left.Add(lyt_sel_script, 0, wx.EXPAND|wx.BOTTOM, 5)
        
        for S, RB in self.script_objects:
            lyt_left.Add(S, 1, wx.EXPAND)
        
        # Auto-Link/Right side
        lyt_ti_autolink = wx.BoxSizer(wx.HORIZONTAL)
        lyt_ti_autolink.Add(txt_autolink, 0, wx.ALIGN_CENTER)
        lyt_ti_autolink.Add(self.ti_autolink, 1, wx.ALIGN_CENTER)
        
        lyt_btn_autolink = wx.BoxSizer(wx.HORIZONTAL)
        lyt_btn_autolink.Add(btn_al_import, 0)
        lyt_btn_autolink.Add(btn_al_remove, 0, wx.LEFT|wx.RIGHT, 5)
        lyt_btn_autolink.Add(btn_al_generate, 0)
        
        lyt_autolink = wx.BoxSizer(wx.VERTICAL)
        lyt_autolink.Add(lyt_ti_autolink, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, 5)
        lyt_autolink.Add(self.executables, 3, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
        lyt_autolink.Add(lyt_btn_autolink, 0, wx.ALIGN_CENTER_HORIZONTAL)
        lyt_autolink.Add(btn_help, 1, wx.ALIGN_CENTER)
        
        pnl_autolink.SetSizer(lyt_autolink)
        pnl_autolink.SetAutoLayout(True)
        pnl_autolink.Layout()
        
        # Sizer for right half of scripts panel
        lyt_right = wx.BoxSizer(wx.VERTICAL)
        # Line up panels to look even
        lyt_right.AddSpacer(39)
        lyt_right.Add(wx.StaticText(self, label=GT(u'Auto-Link Executables')),
                0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        lyt_right.Add(pnl_autolink, 0, wx.EXPAND)
        
        lyt_main = wx.BoxSizer(wx.HORIZONTAL)
        lyt_main.Add(lyt_left, 1, wx.EXPAND|wx.ALL, 5)
        lyt_main.Add(lyt_right, 0, wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def Export(self, out_dir):
        return_code = (0, None)
        
        for S, O in self.script_objects:
            if S.IsExportable():
                return_code = S.Export(out_dir, False)
                
                if return_code[0]:
                    return return_code
        
        return return_code
    
    
    ## TODO: Doxygen
    def ExportBuild(self, stage):
        stage = u'{}/DEBIAN'.format(stage).replace(u'//', u'/')
        
        if not os.path.isdir(stage):
            os.makedirs(stage)
        
        # FIXME: Should have error check
        for S, RB in self.script_objects:
            if S.IsExportable():
                S.Export(stage, build=True)
        
        return (dbrerrno.SUCCESS, None)
                
    
    ## Imports executables from files page for Auto-Link
    def ImportExe(self, event=None):
        event_id = event.GetId()
        if event_id == ident.IMPORT:
            # First clear the Auto-Link display and the executable list
            self.executables.DeleteAllItems()
            self.lst_executables = []
            
            # Get executables from "files" tab
            files = GetField(ident.FILES, ident.F_LIST)
            
            # Sets the max iterate value
            MAX = files.GetItemCount()
            i_index = 0
            while i_index < MAX:
                # Searches for executables (distinguished by executable flag)
                if files.FileIsExecutable(i_index):
                    # Get the filename from the source
                    filename = os.path.basename(files.GetItemText(i_index))
                    
                    # Where the file linked to will be installed
                    file_target = files.GetItem(i_index, 2)
                    
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
                            
                            exe_index = self.executables.GetItemCount()
                            
                            # Put "destination/filename" together in executable list
                            self.lst_executables.insert(exe_index, u'{}/{}'.format(dest_path, filename))
                            self.executables.InsertStringItem(exe_index, filename)
                            self.executables.SetItemTextColour(exe_index, wx.RED)
                        
                        else:
                            Logger.Warning(__name__, u'{}: The executables destination is not valid'.format(__name__))
                    
                    except IndexError:
                        Logger.Warning(__name__, u'{}: The executables destination is not available'.format(__name__))
                
                i_index += 1
        
        elif event_id in (wx.ID_REMOVE, wx.WXK_DELETE):
            # FIXME: Use ListCtrlPanel.DeleteAllItems()???
            exe = self.executables.GetFirstSelected()
            if exe != -1:
                self.executables.DeleteItem(exe)
                self.lst_executables.remove(self.lst_executables[exe])
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, filename):
        Logger.Debug(__name__, GT(u'Importing script: {}').format(filename))
        
        script_name = filename.split(u'-')[-1]
        script_object = None
        
        for S, O in self.script_objects:
            if script_name == S.GetFilename():
                script_object = S
                break
        
        # Loading the actual text
        # FIXME: Should be done in class method
        if script_object != None:
            script_data = ReadFile(filename, split=True)
            
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
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        for S, RB in self.script_objects:
            if S.IsExportable():
                return True
    
    
    ## Creates scripts that link the executables
    def OnGenerate(self, event=None):
        for S in self.postinst, self.prerm:
            if not TextIsEmpty(S.GetValue()):
                confirm = wx.MessageDialog(GetTopWindow(),
                        GT(u'The {} script is not empty').format(S.script_name), GT(u'Warning'),
                        style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
                confirm.SetYesNoLabels(u'Continue', u'Cancel')
                confirm.SetExtendedMessage(GT(u'Do you want to overwrite the contents of this script?'))
                if confirm.ShowModal() == wx.ID_NO:
                    Logger.Debug(__name__, GT(u'Cancelling'))
                    return
                
                Logger.Debug(__name__, GT(u'Continuing'))
    
        # Create the scripts to link the executables
        
        # Create a list of commands to put into the script
        postinst_list = []
        prerm_list = []
        
        link_path = self.ti_autolink.GetValue() # Get destination for link from Auto-Link input textctrl
        total = len(self.lst_executables)  # Get the amount of links to be created
        
        if total > 0:
            cont = True
            
            # If the link path does not exist on the system post a warning message
            if os.path.isdir(link_path) == False:
                cont = False
                msg_path = GT(u'Path "{}" does not exist. Continue?')
                link_error_dia = wx.MessageDialog(self, msg_path.format(link_path), GT(u'Path Warning'),
                    style=wx.YES_NO)
                if link_error_dia.ShowModal() == wx.ID_YES:
                    cont = True
            
            if cont:
                count = 0
                while count < total:
                    filename = os.path.split(self.lst_executables[count])[1]
                    if u'.' in filename:
                        linkname = u'.'.join(filename.split(u'.')[:-1])
                        link = u'{}/{}'.format(link_path, linkname)
                    else:
                        link = u'{}/{}'.format(link_path, filename)
                        #link = u'{}/{}'.format(link_path, os.path.split(self.lst_executables[count])[1])
                    postinst_list.append(u'ln -fs "{}" "{}"'.format(self.lst_executables[count], link))
                    prerm_list.append(u'rm "{}"'.format(link))
                    count += 1
                
                postinst = u'\n\n'.join(postinst_list)
                prerm = u'\n\n'.join(prerm_list)
                
                #self.te_postinst.SetValue(u'#! /bin/bash -e\n\n{}'.format(postinst))
                self.chk_postinst.SetValue(True)
                #self.te_prerm.SetValue(u'#! /bin/bash -e\n\n{}'.format(prerm))
                self.chk_prerm.SetValue(True)
                
                dia = wx.MessageDialog(self, GT(u'post-install and pre-remove scripts generated'), GT(u'Success'), wx.OK)
                dia.ShowModal()
                dia.Destroy()
    
    
    ## TODO: Doxygen
    def OnHelpButton(self, event=None):
        self.al_help = MarkdownDialog(self, title=GT(u'Auto-Link Help'))
        #self.al_help = wx.Dialog(self, -1, GT(u'Auto-Link Help'))
        description = GT(u'Debreate offers an Auto-Link Executables feature. What this does is finds any executables in the Files section and creates a postinst script that will create soft links to them in the specified path. This is useful if you are installing executables to a directory that is not found in the system PATH but want to access it from the PATH. For example, if you install an executable "bar" to the directory "/usr/share/foo" in order to execute "bar" from a terminal you would have to type /usr/share/foo/bar. Auto-Link can be used to place a link to "bar" somewhere on the system path like "/usr/bin". Then all that needs to be typed is bar to execute the program. Auto-Link also creates a prerm script that will delete the link upon removing the package.')
        instructions = GT(u'How to use Auto-Link: Press the IMPORT button to import any executables from the Files section. Then press the GENERATE button. Post-Install and Pre-Remove scripts will be created that will place symbolic links to your executables in the path displayed above.')
        
        self.al_help.SetText(u'{}\n\n{}'.format(description, instructions))
        
        # FIXME:
        #self.al_help.button_ok = ButtonConfirm(self.al_help)
        
        self.al_help.ShowModal()
        self.al_help.CenterOnParent(wx.BOTH)
        self.al_help.Close()
    
    
    ## Resets all fields on page to default values
    def ResetPage(self):
        for S, O in self.script_objects:
            S.Reset()
        
        self.ti_autolink.Reset()
        self.executables.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def ScriptSelect(self, event=None):
        for S, RB in self.script_objects:
            if RB.GetValue():
                S.Show()
            else:
                S.Hide()
        
        self.Layout()
    
    
    ## TODO: Doxygen
    def SetFieldDataLegacy(self, data):
        preinst = data.split(u'<<PREINST>>\n')[1].split(u'\n<</PREINST>>')[0]
        postinst = data.split(u'<<POSTINST>>\n')[1].split(u'\n<</POSTINST>>')[0]
        prerm = data.split(u'<<PRERM>>\n')[1].split(u'\n<</PRERM>>')[0]
        postrm = data.split(u'<<POSTRM>>\n')[1].split(u'\n<</POSTRM>>')[0]
        
        def format_script(script):
            return u'\n'.join(script.split(u'\n')[2:])  # Use '2' to remove first two lines
        
        if unicode(preinst[0]).isnumeric():
            if int(preinst[0]):
                self.preinst.SetValue(format_script(preinst))
        
        if unicode(postinst[0]).isnumeric():
            if int(postinst[0]):
                self.postinst.SetValue(format_script(postinst))
        
        if unicode(prerm[0]).isnumeric():
            if int(prerm[0]):
                self.prerm.SetValue(format_script(prerm))
        
        if unicode(postrm[0]).isnumeric():
            if int(postrm[0]):
                self.postrm.SetValue(format_script(postrm))



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
    def __init__(self, parent, script_id):
        wx.Panel.__init__(self, parent, script_id)
        
        self.parent = parent
        
        ## Filename used for exporting script
        self.script_filename = id_definitions[script_id].lower()
        
        ## String name used for display in the application
        self.script_name = None
        self.__set_script_name()
        
        shell_options = []
        shell_options.append(u'/bin/sh')  # Place /bin/sh as first item
        for P in u'/bin/', u'/usr/bin/', u'/usr/bin/env ':
            for S in sorted(shell_descriptions, key=unicode.lower):
                if S == u'sh':
                    pass
                
                else:
                    shell_options.append(P + S)
        
        self.shell = ComboBox(self, self.GetId(), choices=shell_options)
        self.shell.default = u'/bin/bash'
        self.shell.SetStringSelection(self.shell.default)
        
        self.script_body = TextAreaPanel(self, self.GetId())
        
        # *** Layout *** #
        
        lyt_shell = wx.BoxSizer(wx.HORIZONTAL)
        lyt_shell.Add(wx.StaticText(self, label=u'#!'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        lyt_shell.Add(self.shell, 1)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(lyt_shell, 0)
        lyt_main.Add(self.script_body, 1, wx.EXPAND|wx.TOP, 5)
        
        self.SetSizer(lyt_main)
        self.SetAutoLayout(True)
        self.Layout()
        
        # Scripts are hidden by default
        self.Hide()
    
    
    ## Sets the name of the script to be displayed
    #  
    #  Sets the displayed script name to a value of either 'Pre Install',
    #    'Pre Uninstall', 'Post Install', or 'Post Uninstall'. 'self.script_filename'
    #    is used to determine the displayed name.
    #  TODO: Add strings to GetText translations
    def __set_script_name(self):
        prefix = None
        suffix = None
        
        if u'pre' in self.script_filename:
            prefix = u'Pre'
            suffix = self.script_filename.split(u'pre')[1]
        
        elif u'post' in self.script_filename:
            prefix = u'Post'
            suffix = self.script_filename.split(u'post')[1]
        
        if suffix.lower() == u'inst':
            suffix = u'Install'
        
        elif suffix.lower() == u'rm':
            suffix = u'Uninstall'
        
        if (prefix != None) and (suffix != None):
            self.script_name = GT(u'{}-{}'.format(prefix, suffix))
    
    
    ## Exports the script to a text file
    #  
    #  \param out_dir
    #        \b \e str : Target directory to output file
    #  \param executable
    #        \b \e bool : Make file executable
    #  \param build
    #        \b \e bool : Format output for final build
    def Export(self, out_dir, executable=True, build=False):
        if not os.path.isdir(out_dir):
            Logger.Error(__name__, GT(u'Directory not available: {}'.format(out_dir)))
            return (ERR_DIR_NOT_AVAILABLE, __name__)
        
        if build:
            absolute_filename = u'{}/{}'.format(out_dir, self.script_filename).replace(u'//', u'/')
        else:
            absolute_filename = u'{}/{}-{}'.format(out_dir, page_ids[self.parent.GetId()].upper(), self.script_filename)
        
        script_text = u'{}\n\n{}'.format(self.GetShebang(), self.script_body.GetValue())
        
        #add_newline = script_text.split(u'\n')[-1] != u''
        
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
    #        \b \e str : Script filename
    def GetFilename(self):
        return self.script_filename
    
    
    ## Retrieves the script's name for display
    #  
    #  \return
    #        \b \e str : String representation of script's name
    def GetName(self):
        return self.script_name
    
    
    ## Retrieves the description of a shell for display
    #  
    #  \return
    #        \b \e str : Description or None if using custom shell
    def GetSelectedShellDescription(self):
        selected_shell = self.shell.GetValue()
        
        if selected_shell in shell_descriptions:
            return shell_descriptions[selected_shell]
        
        return None
    
    
    ## TODO: Doxygen
    def GetShebang(self):
        shell = self.shell.GetValue()
        
        if shell.startswith(u'/usr/bin/env '):
            shell = u'#!{}\nset -e'.format(shell)
        else:
            shell = u'#!{} -e'.format(shell)
        
        return shell
    
    
    ## TODO: Doxygen
    def GetValue(self):
        return self.script_body.GetValue()
    
    
    ## Retrieves whether or not the script is used & should be exported
    #  
    #  The text area is checked &, if not empty, signifies that
    #    the user want to export the script.
    #  \return
    #        \b \e bool : 'True' if text area is not empty, 'False' otherwise
    def IsExportable(self):
        return (not TextIsEmpty(self.script_body.GetValue()))
    
    
    ## Resets all members to default values
    def Reset(self):
        self.shell.SetStringSelection(self.shell.default)
        self.script_body.Clear()
    
    
    ## TODO: Doxygen
    def SetScript(self, value):
        self.SetValue(value)
    
    
    ## TODO: Doxygen
    def SetShell(self, shell, forced=False):
        if forced:
            self.shell.SetValue(shell)
            return
        
        self.shell.SetStringSelection(shell)
    
    
    ## Fills the script
    #  
    #  \param value
    #        \b \e unicode|str : Text to be displayed
    def SetValue(self, value):
        self.script_body.SetValue(value)
