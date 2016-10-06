# -*- coding: utf-8 -*-

## \package wiz_bin.scripts


# System modules
import wx, os

# Local modules
import dbr
from dbr.constants import ID_SCRIPTS, ERR_DIR_NOT_AVAILABLE, ERR_FILE_WRITE,\
    page_ids
from dbr.functions import TextIsEmpty
from dbr.language import GT
from dbr import Logger
from dbr.wizard import WizardPage


ID_Import = 100
ID_Remove = 101

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

class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_SCRIPTS)
        
        # Allows calling parent methods
        self.debreate = parent.parent
        
        
        self.preinst = DebianScript(self, ID_INST_PRE)
        self.postinst = DebianScript(self, ID_INST_POST)
        self.prerm = DebianScript(self, ID_RM_PRE)
        self.postrm = DebianScript(self, ID_RM_POST)
        
        # Radio buttons for displaying between pre- and post- install scripts
        rb_preinst = wx.RadioButton(self, self.preinst.GetId(), self.preinst.GetName(), style=wx.RB_GROUP)
        rb_postinst = wx.RadioButton(self, self.postinst.GetId(), self.postinst.GetName())
        rb_prerm = wx.RadioButton(self, self.prerm.GetId(), self.prerm.GetName())
        rb_postrm = wx.RadioButton(self, self.postrm.GetId(), self.postrm.GetName())
        
        self.script_objects = (
            (self.preinst, rb_preinst),
            (self.postinst, rb_postinst),
            (self.prerm, rb_prerm),
            (self.postrm, rb_postrm),
        )
        
        for S, RB in self.script_objects:
            wx.EVT_RADIOBUTTON(RB, RB.GetId(), self.ScriptSelect)
        
        rb_layout = wx.BoxSizer(wx.HORIZONTAL)
        rb_layout.AddMany([
            (rb_preinst),
            (rb_postinst),
            (rb_prerm),
            (rb_postrm),
        ])
        
        # Sizer for left half of scripts panel
        layout_left = wx.BoxSizer(wx.VERTICAL)
        
        layout_left.Add(rb_layout, 0, wx.EXPAND|wx.BOTTOM, 5)
        
        for S, RB in self.script_objects:
            layout_left.Add(S, 1, wx.EXPAND)
        
        # *** Auto-Link options *** #
        
        # Executable list - generate button will make scripts to link to files in this list
        self.xlist = []
        
        # Auto-Link path for new link
        self.al_text = wx.StaticText(self, -1, GT(u'Path'))
        self.al_input = dbr.PathCtrl(self, -1, u'/usr/bin', dbr.PATH_WARN)
        
        #wx.EVT_KEY_UP(self.al_input, ChangeInput)
        
        alpath_sizer = wx.BoxSizer(wx.HORIZONTAL)
        alpath_sizer.Add(self.al_text, 0, wx.ALIGN_CENTER)
        alpath_sizer.Add(self.al_input, 1, wx.ALIGN_CENTER)
        
        # Auto-Link executables to be linked
        if wx.MAJOR_VERSION < 3: # FIXME: wx. 3.0 compat
            self.executables = wx.ListCtrl(self, -1, size=(200,200),
            	style=wx.BORDER_SIMPLE|wx.LC_SINGLE_SEL)
            self.executables.InsertColumn(0, u'')
        
        else:
            self.executables = wx.ListCtrl(self, -1, size=(200,200))
            #self.executables.SetSingleStyle(wx.LC_REPORT)
            self.executables.SetSingleStyle(wx.LC_SINGLE_SEL)
        
        # Auto-Link import, generate and remove buttons
        self.al_import = dbr.ButtonImport(self, ID_Import)
        self.al_import.SetToolTip(wx.ToolTip(GT(u'Import executables from Files section')))
        self.al_del = dbr.ButtonDel(self, ID_Remove)
        self.al_gen = dbr.ButtonBuild(self)
        self.al_gen.SetToolTip(wx.ToolTip(GT(u'Generate Scripts')))
        
        wx.EVT_BUTTON(self.al_import, ID_Import, self.ImportExe)
        wx.EVT_BUTTON(self.al_gen, -1, self.OnGenerate)
        wx.EVT_BUTTON(self.al_del, ID_Remove, self.ImportExe)
        
        albutton_sizer = wx.BoxSizer(wx.HORIZONTAL)
        albutton_sizer.Add(self.al_import, 1)#, wx.ALIGN_CENTER|wx.RIGHT, 5)
        albutton_sizer.Add(self.al_del, 1)
        albutton_sizer.Add(self.al_gen, 1)#, wx.ALIGN_CENTER)
        
        # Nice border for auto-generate scripts area
        self.autogen_border = wx.StaticBox(self, -1, GT(u'Auto-Link Executables'), size=(20,20))  # Size mandatory or causes gui errors
        autogen_box = wx.StaticBoxSizer(self.autogen_border, wx.VERTICAL)
        autogen_box.Add(alpath_sizer, 0, wx.EXPAND)
        autogen_box.Add(self.executables, 0, wx.TOP|wx.BOTTOM, 5)
        autogen_box.Add(albutton_sizer, 0, wx.EXPAND)
        #autogen_box.AddSpacer(5)
        #autogen_box.Add(self.al_del, 0, wx.ALIGN_CENTER)
        
        # Text explaining Auto-Link
        '''self.al_text = wx.StaticText(self, -1, 'How to use Auto-Link: Press the "import" button to \
import any executables from the "files" tab.  Then press the "generate" button.  "postinst" and "prerm" \
scripts will be created that will place a symbolic link to your executables in the path displayed above.')
        self.al_text.Wrap(210)'''
        
        # *** HELP *** #
        self.button_help = dbr.ButtonQuestion64(self)
        
        wx.EVT_BUTTON(self.button_help, wx.ID_HELP, self.OnHelpButton)
        
        # Sizer for right half of scripts panel
        layout_right = wx.BoxSizer(wx.VERTICAL)
        layout_right.AddSpacer(17)
        layout_right.Add(autogen_box, 0)
        #layout_right.Add(self.al_text, 0)
        layout_right.Add(self.button_help, 0, wx.ALIGN_CENTER)
        
        
        # ----- Layout
        layout_main = wx.BoxSizer(wx.HORIZONTAL)
        layout_main.Add(layout_left, 1, wx.EXPAND|wx.ALL, 5)
        layout_main.Add(layout_right, 0, wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_main)
        self.Layout()
        
        # Initialize script display
        self.ScriptSelect(None)
    
    
    def ScriptSelect(self, event):
        for S, RB in self.script_objects:
            if RB.GetValue():
                S.Show()
            else:
                S.Hide()
        
        self.Layout()
    
    
    # Importing the executable for Auto-Link
    def ImportExe(self, event):
        event_id = event.GetId()
        if event_id == ID_Import:
            # First clear the Auto-Link display and the executable list
            self.executables.DeleteAllItems()
            self.xlist = []
            
            # Get executables from "files" tab
            files = self.debreate.page_files.dest_area
            it_max = files.GetItemCount()  # Sets the max iterate value
            count = 0
            while count < it_max:
                # Searches for executables (distinguished by red text)
                if files.GetItemTextColour(count) == (255, 0, 0, 255):
                    filename = os.path.split(files.GetItemText(count))[1]  # Get the filename from the source
                    dest = files.GetItem(count, 1)  # Get the destination of executable
                    try:
                        # If destination doesn't start with "/" do not include executable
                        if dest.GetText()[0] == u'/':
                            if dest.GetText()[-1] == u'/' or dest.GetText()[-1] == u' ':
                                # In case the full path of the destination is "/" keep going
                                if len(dest.GetText()) == 1:
                                    dest_path = u''
                                else:
                                    search = True
                                    slashes = 1  # Set the number of spaces to remove from dest path in case of multiple "/"
                                    while search:
                                        # Find the number of slashes/spaces at the end of the filename
                                        endline = slashes-1
                                        if dest.GetText()[-slashes] == u'/' or dest.GetText()[-slashes] == u' ':
                                            slashes += 1
                                        else:
                                            dest_path = dest.GetText()[:-endline]
                                            search = False
                            else:
                                dest_path = dest.GetText()
                            
                            # Put "destination/filename" together in executable list
                            self.xlist.insert(0, u'%s/%s' %(dest_path, filename))
                            self.executables.InsertStringItem(0, filename)
                            self.executables.SetItemTextColour(0, u'red')
                        else:
                            print(u'panscripts.py: The executables destination is not valid')
                    except IndexError:
                        print(u'panscripts.py: The executables destination is not available')
                count += 1
        
        elif event_id == ID_Remove:
            exe = self.executables.GetFirstSelected()
            if exe != -1:
                self.executables.DeleteItem(exe)
                self.xlist.remove(self.xlist[exe])
    
    
    def OnGenerate(self, event):
        # Create the scripts to link the executables
        
        # Create a list of commands to put into the script
        postinst_list = []
        prerm_list = []
        
        link_path = self.al_input.GetValue() # Get destination for link from Auto-Link input textctrl
        total = len(self.xlist)  # Get the amount of links to be created
        
        if total > 0:
            cont = True
            
            # If the link path does not exist on the system post a warning message
            if os.path.isdir(link_path) == False:
                cont = False
                msg_path = GT(u'Path "%s" does not exist. Continue?')
                link_error_dia = wx.MessageDialog(self, msg_path % (link_path), GT(u'Path Warning'),
                    style=wx.YES_NO)
                if link_error_dia.ShowModal() == wx.ID_YES:
                    cont = True
            
            if cont:
                count = 0
                while count < total:
                    filename = os.path.split(self.xlist[count])[1]
                    if u'.' in filename:
                        linkname = u'.'.join(filename.split(u'.')[:-1])
                        link = u'%s/%s' % (link_path, linkname)
                    else:
                        link = u'%s/%s' % (link_path, filename)
                        #link = u'%s/%s' % (link_path, os.path.split(self.xlist[count])[1])
                    postinst_list.append(u'ln -fs "%s" "%s"' % (self.xlist[count], link))
                    prerm_list.append(u'rm "%s"' % (link))
                    count += 1
                
                postinst = u'\n\n'.join(postinst_list)
                prerm = u'\n\n'.join(prerm_list)
                
                self.te_postinst.SetValue(u'#! /bin/bash -e\n\n%s' % postinst)
                self.chk_postinst.SetValue(True)
                self.te_prerm.SetValue(u'#! /bin/bash -e\n\n%s' % prerm)
                self.chk_prerm.SetValue(True)
                
                dia = wx.MessageDialog(self, GT(u'post-install and pre-remove scripts generated'), GT(u'Success'), wx.OK)
                dia.ShowModal()
                dia.Destroy()
    
    def ChangeBG(self, exists):
        if self.al_input.GetValue() == u'':
            self.al_input.SetValue(u'/')
        elif exists == False:
            self.al_input.SetBackgroundColour((255, 0, 0, 255))
        else:
            self.al_input.SetBackgroundColour((255, 255, 255, 255))
    
    # *** HELP *** #
    def OnHelpButton(self, event):
        self.al_help = wx.Dialog(self, -1, GT(u'Auto-Link Help'))
        description = GT(u'Debreate offers an Auto-Link Executables feature. What this does is finds any executables in the Files section and creates a postinst script that will create soft links to them in the specified path. This is useful if you are installing executables to a directory that is not found in the system PATH but want to access it from the PATH. For example, if you install an executable "bar" to the directory "/usr/share/foo" in order to execute "bar" from a terminal you would have to type /usr/share/foo/bar. Auto-Link can be used to place a link to "bar" somewhere on the system path like "/usr/bin". Then all that needs to be typed is bar to execute the program. Auto-Link also creates a prerm script that will delete the link upon removing the package.')
        instructions = GT(u'How to use Auto-Link: Press the IMPORT button to import any executables from the Files section. Then press the GENERATE button. Post-Install and Pre-Remove scripts will be created that will place symbolic links to your executables in the path displayed above.')

        self.al_help_te = wx.TextCtrl(self.al_help, -1, u'%s\n\n%s' % (description, instructions),
                style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.al_help_ok = dbr.ButtonConfirm(self.al_help)
        
        al_help_sizer = wx.BoxSizer(wx.VERTICAL)
        al_help_sizer.AddMany([ (self.al_help_te, 1, wx.EXPAND), (self.al_help_ok, 0, wx.ALIGN_RIGHT) ])
        self.al_help.SetSizer(al_help_sizer)
        self.al_help.Layout()
        
        self.al_help.ShowModal()
        self.al_help.CenterOnParent(wx.BOTH)
        self.al_help.Close()
    
    
    def ResetAllFields(self):
        for rb in self.script_chk:
            self.script_chk[rb].SetValue(False)
        for rb in self.script_te:
            self.script_te[rb].Clear()
#			# Reset to show Preinstall script as default
#			if rb == self.rb_preinst:
#				self.script_te[rb].Show()
#			else:
#				self.script_te[rb].Hide()
        self.rb_preinst.SetValue(True)
        self.ScriptSelect(None)
        
        self.al_input.SetValue(u'/usr/bin')
        self.al_input.SetBackgroundColour((255, 255, 255, 255))
        self.executables.DeleteAllItems()
    
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
    
    
    # FIXME: Deprecated
    def GatherData(self):
        # Custom dictionary of scripts
        script_list = (
            (self.chk_preinst, self.te_preinst, u'PREINST'),
            (self.chk_postinst, self.te_postinst, u'POSTINST'),
            (self.chk_prerm, self.te_prerm, u'PRERM'),
            (self.chk_postrm, self.te_postrm, u'POSTRM')
        )
        
        # Create a list to return the data
        data = []
        #make_scripts = False # Return empty script section
        for group in script_list:
            if group[0].GetValue():
                #make_scripts = True
                data.append(u'<<%s>>\n1\n%s\n<</%s>>' % (group[2], group[1].GetValue(), group[2]))
            else:
                data.append(u'<<%s>>\n0\n<</%s>>' % (group[2], group[2]))
                
        
        return u'<<SCRIPTS>>\n%s\n<</SCRIPTS>>' % u'\n'.join(data)
    
    
    def Export(self, out_dir):
        return_code = (0, None)
        
        for S, O in self.script_objects:
            if S.IsExportable():
                return_code = S.Export(out_dir, False)
                
                if return_code[0]:
                    return return_code
        
        return return_code


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
        shell_options.append(u'/bin/sh')
        for P in u'/bin/', u'/usr/bin/', u'/usr/bin/env ':
            for S in sorted(shell_descriptions, key=unicode.lower):
                if S == u'sh':
                    pass
                
                else:
                    shell_options.append(P + S)
        
        self.shell = wx.ComboBox(self, self.GetId(), choices=shell_options)
        self.shell.SetStringSelection(u'/bin/bash')
        
        shell_layout = wx.BoxSizer(wx.HORIZONTAL)
        shell_layout.Add(wx.StaticText(self, label=u'#!'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        shell_layout.Add(self.shell, 1)
        
        self.script_body = wx.TextCtrl(self, self.GetId(), style=wx.TE_MULTILINE)
        
        sizer_v1 = wx.BoxSizer(wx.VERTICAL)
        sizer_v1.Add(shell_layout, 0)
        sizer_v1.Add(self.script_body, 1, wx.EXPAND)
        
        self.SetSizer(sizer_v1)
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
    
    
    ## Retrieves whether or not the script is used & should be exported
    #  
    #  The text area is checked &, if not empty, signifies that
    #    the user want to export the script.
    #  \return
    #        \b \e bool : 'True' if text area is not empty, 'False' otherwise
    def IsExportable(self):
        return (not TextIsEmpty(self.script_body.GetValue()))
    
    ## Exports the script to a text file
    #  
    #  \param out_dir
    #        \b \e str : Target directory to output file
    #  \param executable
    #        \b \e bool : Make file executable
    def Export(self, out_dir, executable=True):
        if not os.path.isdir(out_dir):
            Logger.Error(__name__, GT(u'Directory not available: {}'.format(out_dir)))
            return (ERR_DIR_NOT_AVAILABLE, __name__)
        
        absolute_filename = u'{}/{}-{}'.format(out_dir, page_ids[self.parent.GetId()].upper(), self.script_filename)
        script_text = u'#!{}\n\n{}'.format(self.shell.GetValue(), self.script_body.GetValue())
        
        #add_newline = script_text.split(u'\n')[-1] != u''
        
        script_w = open(absolute_filename, u'w')
        script_w.write(script_text)
        
        #if add_newline:
        #    script_w.write(u'\n\n')
        
        script_w.close()
        
        if not os.path.isfile(absolute_filename):
            Logger.Error(__name__, GT(u'Could not write to file: {}'.format(absolute_filename)))
            return (ERR_FILE_WRITE, __name__)
        
        return (0, None)
    
    
    ## Fills the script
    #  
    #  \param value
    #        \b \e unicode|str : Text to be displayed
    def SetValue(self, value):
        self.script_body.SetValue(value)
