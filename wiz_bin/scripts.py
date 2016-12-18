# -*- coding: utf-8 -*-

## \package wiz_bin.scripts

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.buttons            import ButtonBuild
from dbr.buttons            import ButtonImport
from dbr.buttons            import ButtonQuestion64
from dbr.buttons            import ButtonRemove
from dbr.dialogs            import ConfirmationDialog
from dbr.dialogs            import DetailedMessageDialog
from dbr.functions          import TextIsEmpty
from dbr.language           import GT
from wxcustom.listinput     import ListCtrlPanel
from dbr.log                import Logger
from dbr.markdown           import MarkdownDialog
from dbr.panel              import BorderedPanel
from dbr.pathctrl           import PATH_WARN
from dbr.pathctrl           import PathCtrl
from dbr.textinput          import MonospaceTextArea
from globals                import ident
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetPage
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
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ident.SCRIPTS, name=GT(u'Scripts'))
        
        self.SetScrollbars(20, 20, 0, 0)
        
        # Check boxes for choosing scripts
        self.chk_preinst = wx.CheckBox(self, ID_INST_PRE, GT(u'Make this script'), name=GT(u'Pre-Install'))
        self.chk_postinst = wx.CheckBox(self, ID_INST_POST, GT(u'Make this script'), name=GT(u'Post-Install'))
        self.chk_prerm = wx.CheckBox(self, ID_RM_PRE, GT(u'Make this script'), name=GT(u'Pre-Remove'))
        self.chk_postrm = wx.CheckBox(self, ID_RM_POST, GT(u'Make this script'), name=GT(u'Post-Remove'))
        
        for S in self.chk_preinst, self.chk_postinst, self.chk_prerm, self.chk_postrm:
            S.SetToolTipString(u'{} {}'.format(S.GetName(), GT(u'script will be created from text below')))
            
            S.Bind(wx.EVT_CHECKBOX, self.OnToggleScripts)
        
        # Radio buttons for displaying between pre- and post- install scripts
        self.rb_preinst = wx.RadioButton(self, ID_INST_PRE, GT(u'Pre-Install'),
                name=u'preinst', style=wx.RB_GROUP)
        self.rb_postinst = wx.RadioButton(self, ID_INST_POST, GT(u'Post-Install'),
                name=u'postinst')
        self.rb_prerm = wx.RadioButton(self, ID_RM_PRE, GT(u'Pre-Remove'),
                name=u'prerm')
        self.rb_postrm = wx.RadioButton(self, ID_RM_POST, GT(u'Post-Remove'),
                name=u'postrm')
        
        # Text area for each radio button
        self.ti_preinst = MonospaceTextArea(self, ID_INST_PRE, name=u'script body')
        self.ti_postinst = MonospaceTextArea(self, ID_INST_POST, name=u'script body')
        self.ti_prerm = MonospaceTextArea(self, ID_RM_PRE, name=u'script body')
        self.ti_postrm = MonospaceTextArea(self, ID_RM_POST, name=u'script body')
        
        for TI in self.ti_preinst, self.ti_postinst, self.ti_prerm, self.ti_postrm:
            TI.EnableDropTarget()
        
        # Set script text areas to default enabled/disabled setting
        self.OnToggleScripts()
        
        self.grp_te = {	self.rb_preinst: self.ti_preinst, self.rb_postinst: self.ti_postinst,
                            self.rb_prerm: self.ti_prerm, self.rb_postrm: self.ti_postrm
                            }
        
        self.grp_chk = {	self.rb_preinst: self.chk_preinst, self.rb_postinst: self.chk_postinst,
                            self.rb_prerm: self.chk_prerm, self.rb_postrm: self.chk_postrm }
        
        for rb in self.grp_te:
            self.grp_te[rb].Hide()
        
        for rb in self.grp_chk:
            self.grp_chk[rb].Hide()
        
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
        
        # Auto-Link import, generate and remove buttons
        btn_al_import = ButtonImport(pnl_autolink)
        btn_al_remove = ButtonRemove(pnl_autolink)
        btn_al_generate = ButtonBuild(pnl_autolink)
        
        # Auto-Link help
        btn_help = ButtonQuestion64(pnl_autolink)
        
        # Initialize script display
        self.ScriptSelect(None)
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        # Organizing radio buttons
        lyt_sel_script = wx.BoxSizer(wx.HORIZONTAL)
        lyt_sel_script.AddMany((
            (self.chk_preinst),(self.chk_postinst),
            (self.chk_prerm),(self.chk_postrm)
            ))
        lyt_sel_script.AddStretchSpacer(1)
        lyt_sel_script.Add(self.rb_preinst, 0)
        lyt_sel_script.Add(self.rb_postinst, 0)
        lyt_sel_script.Add(self.rb_prerm, 0)
        lyt_sel_script.Add(self.rb_postrm, 0)
        
        # Sizer for left half of scripts panel
        lyt_left = wx.BoxSizer(wx.VERTICAL)
        lyt_left.Add(lyt_sel_script, 0, wx.EXPAND|wx.BOTTOM, 5)
        lyt_left.Add(self.ti_preinst, 1, wx.EXPAND)
        lyt_left.Add(self.ti_postinst, 1, wx.EXPAND)
        lyt_left.Add(self.ti_prerm, 1,wx.EXPAND)
        lyt_left.Add(self.ti_postrm, 1, wx.EXPAND)
        
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
        
        lyt_right = wx.BoxSizer(wx.VERTICAL)
        lyt_right.AddSpacer(30)
        lyt_right.Add(wx.StaticText(self, label=GT(u'Auto-Link Executables')),
                0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        lyt_right.Add(pnl_autolink, 0, wx.EXPAND)
        
        lyt_main = wx.BoxSizer(wx.HORIZONTAL)
        lyt_main.Add(lyt_left, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 5)
        lyt_main.Add(lyt_right, 0, wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        for rb in self.grp_te:
            rb.Bind(wx.EVT_RADIOBUTTON, self.ScriptSelect)
        
        btn_al_import.Bind(wx.EVT_BUTTON, self.ImportExe)
        wx.EVT_BUTTON(btn_al_generate, wx.ID_ANY, self.OnGenerate)
        wx.EVT_BUTTON(btn_al_remove, wx.ID_REMOVE, self.ImportExe)
        wx.EVT_BUTTON(btn_help, wx.ID_HELP, self.OnHelpButton)
    
    
    ## TODO: Doxygen
    def ChangeBG(self, exists):
        if exists == False:
            self.ti_autolink.SetBackgroundColour((255, 0, 0, 255))
        
        else:
            self.ti_autolink.SetBackgroundColour((255, 255, 255, 255))
    
    
    ## TODO: Doxygen
    def ExportPage(self):
        script_controls = {
            u'preinst': (self.chk_preinst, self.ti_preinst,),
            u'postinst': (self.chk_postinst, self.ti_postinst,),
            u'prerm': (self.chk_prerm, self.ti_prerm),
            u'postrm': (self.chk_postrm, self.ti_postrm),
        }
        
        script_list = []
        
        for S in script_controls:
            chk, te = script_controls[S]
            if chk.GetValue():
                script_list.append((S, te.GetValue()))
        
        return tuple(script_list)
    
    
    ## TODO: Doxygen
    def GatherData(self):
        # Custom dictionary of scripts
        script_list = (
            (self.chk_preinst, self.ti_preinst, u'PREINST'),
            (self.chk_postinst, self.ti_postinst, u'POSTINST'),
            (self.chk_prerm, self.ti_prerm, u'PRERM'),
            (self.chk_postrm, self.ti_postrm, u'POSTRM')
        )
        
        # Create a list to return the data
        data = []
        for group in script_list:
            if group[0].GetValue():
                data.append(u'<<{}>>\n1\n{}\n<</{}>>'.format(group[2], group[1].GetValue(), group[2]))
            
            else:
                data.append(u'<<{}>>\n0\n<</{}>>'.format(group[2], group[2]))
        
        return u'<<SCRIPTS>>\n{}\n<</SCRIPTS>>'.format(u'\n'.join(data))
    
    
    ## Imports executables for Auto-Link
    def ImportExe(self, event=None):
        ID = event.GetId()
        if ID == ident.IMPORT:
            # First clear the Auto-Link display and the executable list
            self.executables.DeleteAllItems()
            self.lst_executables = []
            
            # Get executables from "files" tab
            #files = wx.GetApp().GetTopWindow().page_files.dest_area
            files = GetField(GetPage(ident.FILES), ident.F_LIST)
            MAX = files.GetItemCount()  # Sets the max iterate value
            count = 0
            while count < MAX:
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
                                    # Set the number of spaces to remove from dest path in case of multiple "/"
                                    slashes = 1
                                    while search:
                                        # Find the number of slashes/spaces at the end of the filename
                                        endline = slashes - 1
                                        if dest.GetText()[-slashes] == u'/' or dest.GetText()[-slashes] == u' ':
                                            slashes += 1
                                        
                                        else:
                                            dest_path = dest.GetText()[:-endline]
                                            search = False
                            
                            else:
                                dest_path = dest.GetText()
                            
                            # Put "destination/filename" together in executable list
                            self.lst_executables.insert(0, u'{}/{}'.format(dest_path, filename))
                            self.executables.InsertStringItem(0, filename)
                            self.executables.SetItemTextColour(0, u'red')
                        
                        else:
                            print(u'{}: The executables destination is not valid'.format(__name__))
                    
                    except IndexError:
                        print(u'{}: The executables destination is not available'.format(__name__))
                
                count += 1
        
        elif ID in (wx.ID_REMOVE, wx.WXK_DELETE):
            exe = self.executables.GetFirstSelected()
            if exe != -1:
                self.executables.DeleteItem(exe)
                self.lst_executables.remove(self.lst_executables[exe])
    
    
    ## TODO: Doxygen
    def IsBuildExportable(self):
        for chk in self.chk_preinst, self.chk_postinst, self.chk_prerm, self.chk_postrm:
            if chk.GetValue():
                return True
        
        return False
    
    
    ## Creates scripts that link the executables
    def OnGenerate(self, event=None):
        main_window = GetTopWindow()
        # Get the amount of links to be created
        total = len(self.lst_executables)
        
        if total > 0:
            non_empty_scripts = []
            checked_scripts = (
                (self.ti_postinst, self.rb_postinst),
                (self.ti_prerm, self.rb_prerm),
                )
            
            for TI, RB in checked_scripts:
                if not TextIsEmpty(TI.GetValue()):
                    non_empty_scripts.append(RB.GetLabel())
            
            # Warn about overwriting previous post-install & pre-remove scripts
            if non_empty_scripts:
                warn_msg = GT(u'The following scripts will be overwritten if you continue: {}')
                warn_msg = u'{}\n\n{}'.format(warn_msg.format(u', '.join(non_empty_scripts)), GT(u'Continue?'))
                
                warn_dialog = ConfirmationDialog(main_window, text=warn_msg)
                
                if warn_dialog.ShowModal() not in (wx.ID_OK, wx.OK):
                    return
                
                warn_dialog.Destroy()
                del warn_msg, warn_dialog
            
            # Get destination for link from Auto-Link input textctrl
            link_path = self.ti_autolink.GetValue()
            
            # Warn about linking in a directory that does not exist on the current filesystem
            if not os.path.isdir(link_path):
                warn_msg = GT(u'Path "{}" does not exist.')
                warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))
                
                warn_dialog = ConfirmationDialog(main_window, text=warn_msg.format(link_path))
                
                if warn_dialog.ShowModal() not in (wx.ID_OK, wx.OK):
                    return
                
                warn_dialog.Destroy()
                del warn_msg, warn_dialog
            
            self.chk_postinst.SetValue(True)
            self.chk_prerm.SetValue(True)
            
            # Update scripts' text area enabled status
            self.OnToggleScripts()
            
            # Create a list of commands to put into the script
            postinst_list = []
            prerm_list = []
            
            count = 0
            while count < total:
                filename = os.path.split(self.lst_executables[count])[1]
                if u'.' in filename:
                    linkname = u'.'.join(filename.split(u'.')[:-1])
                    link = u'{}/{}'.format(link_path, linkname)
                
                else:
                    link = u'{}/{}'.format(link_path, filename)
                
                postinst_list.append(u'ln -fs "{}" "{}"'.format(self.lst_executables[count], link))
                prerm_list.append(u'rm -f "{}"'.format(link))
                count += 1
            
            postinst = u'\n\n'.join(postinst_list)
            prerm = u'\n\n'.join(prerm_list)
            
            self.ti_postinst.SetValue(u'#! /bin/bash -e\n\n{}'.format(postinst))
            self.ti_prerm.SetValue(u'#! /bin/bash -e\n\n{}'.format(prerm))
            
            DetailedMessageDialog(main_window, GT(u'Success'),
                    text=GT(u'Post-Install and Pre-Remove scripts generated')).ShowModal()
    
    
    ## TODO: Doxygen
    def OnHelpButton(self, event=None):
        al_help = MarkdownDialog(self, title=GT(u'Auto-Link Help'))
        description = GT(u'Debreate offers an Auto-Link Executables feature. What this does is finds any executables in the Files section and creates a postinst script that will create soft links to them in the specified path. This is useful if you are installing executables to a directory that is not found in the system PATH but want to access it from the PATH. For example, if you install an executable "bar" to the directory "/usr/share/foo" in order to execute "bar" from a terminal you would have to type /usr/share/foo/bar. Auto-Link can be used to place a link to "bar" somewhere on the system path like "/usr/bin". Then all that needs to be typed is bar to execute the program. Auto-Link also creates a prerm script that will delete the link upon removing the package.')
        instructions = GT(u'How to use Auto-Link: Press the IMPORT button to import any executables from the Files section. Then press the GENERATE button. Post-Install and Pre-Remove scripts will be created that will place symbolic links to your executables in the path displayed above.')
        
        al_help.SetText(u'{}\n\n{}'.format(description, instructions))
        
        al_help.ShowModal()
        al_help.CenterOnParent(wx.BOTH)
        al_help.Close()
    
    
    ## TODO: Doxygen
    def OnToggleScripts(self, event=None):
        Logger.Debug(__name__, u'Toggling scripts')
        
        fields = (
            (self.ti_preinst, self.chk_preinst.GetValue()),
            (self.ti_postinst, self.chk_postinst.GetValue()),
            (self.ti_prerm, self.chk_prerm.GetValue()),
            (self.ti_postrm, self.chk_postrm.GetValue()),
            )
        
        for F, enable in fields:
            F.Enable(enable)
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        for rb in self.grp_chk:
            self.grp_chk[rb].SetValue(False)
        
        for rb in self.grp_te:
            self.grp_te[rb].Clear()
        
        self.OnToggleScripts()
        
        self.rb_preinst.SetValue(True)
        self.ScriptSelect(None)
        
        self.ti_autolink.SetValue(self.ti_autolink.default)
        self.ti_autolink.SetBackgroundColour((255, 255, 255, 255))
        self.executables.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def ScriptSelect(self, event=None):
        for rb in self.grp_te:
            if rb.GetValue() == True:
                self.grp_te[rb].Show()
                self.grp_chk[rb].Show()
            
            else:
                self.grp_te[rb].Hide()
                self.grp_chk[rb].Hide()
        
        self.Layout()
    
    
    ## TODO: Doxygen
    def SetFieldData(self, data):
        preinst = (
            data.split(u'<<PREINST>>\n')[1].split(u'\n<</PREINST>>')[0].split(u'\n'),
            self.chk_preinst,
            )
        postinst = (
            data.split(u'<<POSTINST>>\n')[1].split(u'\n<</POSTINST>>')[0].split(u'\n'),
            self.chk_postinst,
            )
        prerm = (
            data.split(u'<<PRERM>>\n')[1].split(u'\n<</PRERM>>')[0].split(u'\n'),
            self.chk_prerm,
            )
        postrm = (
            data.split(u'<<POSTRM>>\n')[1].split(u'\n<</POSTRM>>')[0].split(u'\n'),
            self.chk_postrm,
            )
        
        for S, CHK in (preinst, postinst, prerm, postrm):
            if S[0].isnumeric() and int(S[0]) > 0:
                CHK.SetValue(True)
                # Remove unneeded integer
                S.pop(0)
        
        # Enable/Disable scripts text areas
        self.OnToggleScripts()
        
        if self.chk_preinst.GetValue():
            self.ti_preinst.SetValue(u'\n'.join(preinst[0]))
        
        if self.chk_postinst.GetValue():
            self.ti_postinst.SetValue(u'\n'.join(postinst[0]))
        
        if self.chk_prerm.GetValue():
            self.ti_prerm.SetValue(u'\n'.join(prerm[0]))
        
        if self.chk_postrm.GetValue():
            self.ti_postrm.SetValue(u'\n'.join(postrm[0]))
