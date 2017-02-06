# -*- coding: utf-8 -*-

## \package wizbin.scripts

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.language       import GT
from dbr.log            import Logger
from globals.fileio     import FileItem
from globals.fileio     import GetFiles
from globals.fileio     import ReadFile
from globals.ident      import genid
from globals.ident      import inputid
from globals.ident      import pgid
from globals.strings    import TextIsEmpty
from globals.tooltips   import SetPageToolTips
from input.list         import BasicFileList
from input.markdown     import MarkdownDialog
from input.pathctrl     import PathCtrl
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
from wiz.helper         import FieldEnabled
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
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.SCRIPTS)
        
        preinst = DebianScript(self, ID_INST_PRE)
        postinst = DebianScript(self, ID_INST_POST)
        prerm = DebianScript(self, ID_RM_PRE)
        postrm = DebianScript(self, ID_RM_POST)
        
        # Check boxes for choosing scripts
        chk_preinst = wx.CheckBox(self, ID_INST_PRE, GT(u'Make this script'), name=GT(u'Pre-Install'))
        chk_postinst = wx.CheckBox(self, ID_INST_POST, GT(u'Make this script'), name=GT(u'Post-Install'))
        chk_prerm = wx.CheckBox(self, ID_RM_PRE, GT(u'Make this script'), name=GT(u'Pre-Remove'))
        chk_postrm = wx.CheckBox(self, ID_RM_POST, GT(u'Make this script'), name=GT(u'Post-Remove'))
        
        for S in chk_preinst, chk_postinst, chk_prerm, chk_postrm:
            S.SetToolTipString(u'{} {}'.format(S.GetName(), GT(u'script will be created from text below')))
            
            S.Bind(wx.EVT_CHECKBOX, self.OnToggleScripts)
        
        # Radio buttons for displaying between pre- and post- install scripts
        # FIXME: Names settings for tooltips are confusing
        rb_preinst = wx.RadioButton(self, preinst.GetId(), GT(u'Pre-Install'),
                name=preinst.FileName, style=wx.RB_GROUP)
        rb_postinst = wx.RadioButton(self, postinst.GetId(), GT(u'Post-Install'),
                name=postinst.FileName)
        rb_prerm = wx.RadioButton(self, prerm.GetId(), GT(u'Pre-Remove'),
                name=prerm.FileName)
        rb_postrm = wx.RadioButton(self, postrm.GetId(), GT(u'Post-Remove'),
                name=postrm.FileName)
        
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
        txt_autolink = wx.StaticText(pnl_autolink, label=GT(u'Path'), name=u'target')
        self.ti_autolink = PathCtrl(pnl_autolink, value=u'/usr/bin', warn=True)
        self.ti_autolink.SetName(u'target')
        self.ti_autolink.default = self.ti_autolink.GetValue()
        
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
        
        for DS, CHK, RB in self.script_objects:
            RB.Bind(wx.EVT_RADIOBUTTON, self.ScriptSelect)
        
        wx.EVT_BUTTON(btn_al_import, genid.IMPORT, self.ImportExes)
        wx.EVT_BUTTON(btn_al_generate, wx.ID_ANY, self.OnGenerate)
        wx.EVT_BUTTON(btn_al_remove, wx.ID_REMOVE, self.ImportExes)
        wx.EVT_BUTTON(btn_help, wx.ID_HELP, self.OnHelpButton)
        
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
        lyt_ti_autolink.Add(txt_autolink, 0, wx.ALIGN_CENTER)
        lyt_ti_autolink.Add(self.ti_autolink, 1, wx.ALIGN_CENTER)
        
        lyt_btn_autolink = BoxSizer(wx.HORIZONTAL)
        lyt_btn_autolink.Add(btn_al_import, 0)
        lyt_btn_autolink.Add(btn_al_remove, 0, wx.LEFT|wx.RIGHT, 5)
        lyt_btn_autolink.Add(btn_al_generate, 0)
        
        lyt_autolink = BoxSizer(wx.VERTICAL)
        lyt_autolink.Add(lyt_ti_autolink, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, 5)
        lyt_autolink.Add(self.Executables, 3, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
        lyt_autolink.Add(lyt_btn_autolink, 0, wx.ALIGN_CENTER_HORIZONTAL)
        lyt_autolink.Add(btn_help, 1, wx.ALIGN_CENTER)
        
        pnl_autolink.SetSizer(lyt_autolink)
        pnl_autolink.SetAutoLayout(True)
        pnl_autolink.Layout()
        
        # Sizer for right half of scripts panel
        lyt_right = BoxSizer(wx.VERTICAL)
        # Line up panels to look even
        lyt_right.AddSpacer(32)
        lyt_right.Add(wx.StaticText(self, label=GT(u'Auto-Link Executables')),
                0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        lyt_right.Add(pnl_autolink, 0, wx.EXPAND)
        
        lyt_main = BoxSizer(wx.HORIZONTAL)
        lyt_main.Add(lyt_left, 1, wx.EXPAND|wx.ALL, 5)
        lyt_main.Add(lyt_right, 0, wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def ChangeBG(self, exists):
        if exists == False:
            self.ti_autolink.SetBackgroundColour((255, 0, 0, 255))
        
        else:
            self.ti_autolink.SetBackgroundColour((255, 255, 255, 255))
    
    
    ## TODO: Doxygen
    def ExportBuild(self):
        script_controls = {
            u'preinst': (self.script_ojects[0][0], self.script_ojects[0][2],),
            u'postinst': (self.script_ojects[1][0], self.script_ojects[1][2],),
            u'prerm': (self.script_ojects[2][0], self.script_ojects[2][2],),
            u'postrm': (self.script_ojects[3][0], self.script_ojects[3][2],),
        }
        
        script_list = []
        
        for S in script_controls:
            chk, te = script_controls[S]
            if chk.GetValue():
                script_list.append((S, te.GetValue()))
        
        return tuple(script_list)
    
    
    ## Retrieves page data from fields
    def Get(self):
        scripts = {
            
            }
        
        for DS, CHK, RB in self.script_objects:
            if CHK.GetValue():
                scripts[DS.GetFilename()] = DS.GetValue()
        
        return scripts
    
    
    ## TODO: Doxygen
    def GetSaveData(self):
        # Custom dictionary of scripts
        script_list = (
            (self.script_ojects[0][0], self.script_ojects[0][2], u'PREINST'),
            (self.script_ojects[1][0], self.script_ojects[1][2], u'POSTINST'),
            (self.script_ojects[2][0], self.script_ojects[2][2], u'PRERM'),
            (self.script_ojects[3][0], self.script_ojects[3][2], u'POSTRM')
        )
        
        # Create a list to return the data
        data = []
        for group in script_list:
            if group[0].GetValue():
                data.append(u'<<{}>>\n1\n{}\n<</{}>>'.format(group[2], group[1].GetValue(), group[2]))
            
            else:
                data.append(u'<<{}>>\n0\n<</{}>>'.format(group[2], group[2]))
        
        return u'<<SCRIPTS>>\n{}\n<</SCRIPTS>>'.format(u'\n'.join(data))
    
    
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
    
    
    ## TODO: Doxygen
    #
    #  FIXME: Should be done in DebianScript class method???
    def ImportFromFile(self, filename):
        Logger.Debug(__name__, GT(u'Importing script: {}').format(filename))
        
        script_name = filename.split(u'-')[-1]
        script_object = None
        
        for DS, CHK, RB in self.script_objects:
            if script_name == DS.GetFilename():
                script_object = DS
                
                break
        
        # Loading the actual text
        if script_object != None:
            script_object.SetValue(ReadFile(filename))
    
    
    ## Checks if one or more scripts can be exported
    def IsOkay(self):
        for chk in self.script_ojects:
            chk = chk[0]
            if chk.GetValue():
                return True
        
        return False
    
    
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
            
            for CHK in self.script_objects[1][1], self.script_objects[2][1]:
                CHK.SetValue(True)
            
            # Update scripts' text area enabled status
            self.OnToggleScripts()
            
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
            
            self.script_objects[1][0].SetValue(u'#!/bin/bash -e\n\n{}'.format(postinst))
            self.script_objects[2][0].SetValue(u'#!/bin/bash -e\n\n{}'.format(prerm))
            
            DetailedMessageDialog(main_window, GT(u'Success'),
                    text=GT(u'Post-Install and Pre-Remove scripts generated')).ShowModal()
    
    
    ## TODO: Doxygen
    def OnHelpButton(self, event=None):
        al_help = MarkdownDialog(self, title=GT(u'Auto-Link Help'))
        description = GT(u'Debreate offers an Auto-Link Executables feature. What this does is finds any executables in the Files section and creates a postinst script that will create soft links to them in the specified path. This is useful if you are installing executables to a directory that is not found in the system PATH but want to access it from the PATH. For example, if you install an executable "bar" to the directory "/usr/share/foo" in order to execute "bar" from a terminal you would have to type /usr/share/foo/bar. Auto-Link can be used to place a link to "bar" somewhere on the system path like "/usr/bin". Then all that needs to be typed is bar to execute the program. Auto-Link also creates a prerm script that will delete the link upon removing the package.')
        instructions = GT(u'How to use Auto-Link: Press the IMPORT button to import any executables from the Files section. Then press the GENERATE button. Post-Install and Pre-Remove scripts will be created that will place symbolic links to your executables in the path displayed above.')
        
        al_help.SetText(u'{}\n\n{}'.format(description, instructions))
        
        ShowDialog(al_help)
    
    
    ## TODO: Doxygen
    def OnToggleScripts(self, event=None):
        Logger.Debug(__name__, u'Toggling scripts')
        
        for DS, CHK, RB in self.script_objects:
            DS.Enable(CHK.GetValue())
    
    
    ## Resets all fields on page to default values
    def Reset(self):
        for DS, CHK, RB in self.script_objects:
            CHK.Reset()
            DS.Reset()
        
        self.OnToggleScripts()
        
        self.script_objects[0][2].SetValue(True)
        self.ScriptSelect(None)
        
        self.ti_autolink.Reset()
        self.Executables.Reset()
    
    
    ## TODO: Doxygen
    def ScriptSelect(self, event=None):
        for DS, CHK, RB in self.script_objects:
            if RB.GetValue():
                CHK.Show()
                DS.Show()
            
            else:
                CHK.Hide()
                DS.Hide()
        
        self.Layout()
    
    
    ## TODO: Doxygen
    def Set(self, data):
        chk_preinst = self.script_objects[0][1]
        chk_postinst = self.script_objects[1][1]
        chk_prerm = self.script_objects[2][1]
        chk_postrm = self.script_objects[3][1]
        
        preinst = (
            data.split(u'<<PREINST>>\n')[1].split(u'\n<</PREINST>>')[0].split(u'\n'),
            chk_preinst,
            )
        postinst = (
            data.split(u'<<POSTINST>>\n')[1].split(u'\n<</POSTINST>>')[0].split(u'\n'),
            chk_postinst,
            )
        prerm = (
            data.split(u'<<PRERM>>\n')[1].split(u'\n<</PRERM>>')[0].split(u'\n'),
            chk_prerm,
            )
        postrm = (
            data.split(u'<<POSTRM>>\n')[1].split(u'\n<</POSTRM>>')[0].split(u'\n'),
            chk_postrm,
            )
        
        for S, CHK in (preinst, postinst, prerm, postrm):
            if S[0].isnumeric() and int(S[0]) > 0:
                CHK.SetValue(True)
                # Remove unneeded integer
                S.pop(0)
        
        # Enable/Disable scripts text areas
        self.OnToggleScripts()
        
        if chk_preinst.GetValue():
            self.script_objects[0][0].SetValue(u'\n'.join(preinst[0]))
        
        if chk_postinst.GetValue():
            self.script_objects[1][0].SetValue(u'\n'.join(postinst[0]))
        
        if chk_prerm.GetValue():
            self.script_objects[2][0].SetValue(u'\n'.join(prerm[0]))
        
        if chk_postrm.GetValue():
            self.script_objects[3][0].SetValue(u'\n'.join(postrm[0]))


## Class defining a Debian package script
#  
#  A script's filename is one of 'preinst', 'prerm',
#    'postinst', or 'postrm'. Scripts are stored in the
#    (FIXME: Don't remember section name) section of the package & are executed in the
#    order dictated by the naming convention:
#    'Pre Install', 'Pre Remove/Uninstall',
#    'Post Install', & 'Post Remove/Uninstall'.
class DebianScript(wx.Panel):
    def __init__(self, parent, scriptId):
        wx.Panel.__init__(self, parent, scriptId)
        
        ## Filename used for exporting script
        self.FileName = id_definitions[scriptId].lower()
        
        ## String name used for display in the application
        self.ScriptName = None
        self.SetScriptName()
        
        self.ScriptBody = TextAreaPanelESS(self, self.GetId(), monospace=True)
        self.ScriptBody.EnableDropTarget()
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.ScriptBody, 1, wx.EXPAND|wx.TOP, 5)
        
        self.SetSizer(lyt_main)
        self.SetAutoLayout(True)
        self.Layout()
        
        # Scripts are hidden by default
        self.Hide()
    
    
    ## TODO: Doxygen
    def Disable(self):
        return self.Enable(False)
    
    
    ## TODO: Doxygen
    def Enable(self, enable=True):
        return self.ScriptBody.Enable(enable)
    
    
    ## Retrieves the filename to use for exporting
    #  
    #  \return
    #        \b \e str : Script filename
    def GetFilename(self):
        return self.FileName
    
    
    ## Retrieves the script's name for display
    #  
    #  \return
    #        \b \e str : String representation of script's name
    def GetName(self):
        return self.ScriptName
    
    
    ## TODO: Doxygen
    def GetValue(self):
        return self.ScriptBody.GetValue()
    
    
    ## TODO: Doxygen
    def IsEnabled(self):
        return FieldEnabled(self.ScriptBody)
    
    
    ## Retrieves whether or not the script is used & should be exported
    #  
    #  The text area is checked &, if not empty, signifies that
    #    the user want to export the script.
    #  \return
    #        \b \e bool : 'True' if text area is not empty, 'False' otherwise
    def IsOkay(self):
        return not TextIsEmpty(self.ScriptBody.GetValue())
    
    
    ## Resets all members to default values
    def Reset(self):
        self.ScriptBody.Clear()
    
    
    ## Sets the name of the script to be displayed
    #  
    #  Sets the displayed script name to a value of either 'Pre Install',
    #    'Pre Uninstall', 'Post Install', or 'Post Uninstall'. 'self.FileName'
    #    is used to determine the displayed name.
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
    
    
    ## Fills the script
    #  
    #  \param value
    #    Text to be displayed
    def SetValue(self, value):
        self.ScriptBody.SetValue(value)
