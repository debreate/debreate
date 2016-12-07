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
from dbr.markdown           import MarkdownDialog
from dbr.panel              import BorderedPanel
from dbr.pathctrl           import PATH_WARN
from dbr.pathctrl           import PathCtrl
from dbr.textinput          import MonospaceTextCtrl
from globals.ident          import FID_LIST
from globals.ident          import ID_FILES
from globals.ident          import ID_IMPORT
from globals.ident          import ID_SCRIPTS
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetPage


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
        wx.ScrolledWindow.__init__(self, parent, ID_SCRIPTS, name=GT(u'Scripts'))
        
        self.SetScrollbars(20, 20, 0, 0)
        
        # Check boxes for choosing scripts
        self.chk_preinst = wx.CheckBox(self, ID_INST_PRE, GT(u'Make this script'), name=GT(u'Pre-Install'))
        self.chk_postinst = wx.CheckBox(self, ID_INST_POST, GT(u'Make this script'), name=GT(u'Post-Install'))
        self.chk_prerm = wx.CheckBox(self, ID_RM_PRE, GT(u'Make this script'), name=GT(u'Pre-Remove'))
        self.chk_postrm = wx.CheckBox(self, ID_RM_POST, GT(u'Make this script'), name=GT(u'Post-Remove'))
        
        for S in self.chk_preinst, self.chk_postinst, self.chk_prerm, self.chk_postrm:
            S.SetToolTipString(u'{} {}'.format(S.GetName(), GT(u'script will be created from text below')))
        
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
        self.te_preinst = MonospaceTextCtrl(self, ID_INST_PRE, name=u'script body')
        self.te_postinst = MonospaceTextCtrl(self, ID_INST_POST, name=u'script body')
        self.te_prerm = MonospaceTextCtrl(self, ID_RM_PRE, name=u'script body')
        self.te_postrm = MonospaceTextCtrl(self, ID_RM_POST, name=u'script body')
        
        self.grp_te = {	self.rb_preinst: self.te_preinst, self.rb_postinst: self.te_postinst,
                            self.rb_prerm: self.te_prerm, self.rb_postrm: self.te_postrm
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
        
        # Auto-Link executables to be linked
        self.executables = ListCtrlPanel(pnl_autolink, size=(200,200), name=u'al list')
        self.executables.SetSingleStyle(wx.LC_SINGLE_SEL)
        
        # Auto-Link import, generate and remove buttons
        btn_al_import = ButtonImport(pnl_autolink, ID_IMPORT)
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
        lyt_left.Add(self.te_preinst, 1, wx.EXPAND)
        lyt_left.Add(self.te_postinst, 1, wx.EXPAND)
        lyt_left.Add(self.te_prerm, 1,wx.EXPAND)
        lyt_left.Add(self.te_postrm, 1, wx.EXPAND)
        
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
        
        wx.EVT_BUTTON(btn_al_import, ID_IMPORT, self.ImportExe)
        wx.EVT_BUTTON(btn_al_generate, wx.ID_ANY, self.OnGenerate)
        wx.EVT_BUTTON(btn_al_remove, wx.ID_REMOVE, self.ImportExe)
        wx.EVT_BUTTON(btn_help, wx.ID_HELP, self.OnHelpButton)
    
    
    ## TODO: Doxygen
    def ChangeBG(self, exists):
        if self.ti_autolink.GetValue() == u'':
            self.ti_autolink.SetValue(u'/')
        
        elif exists == False:
            self.ti_autolink.SetBackgroundColour((255, 0, 0, 255))
        
        else:
            self.ti_autolink.SetBackgroundColour((255, 255, 255, 255))
    
    
    ## TODO: Doxygen
    def ExportPage(self):
        script_controls = {
            u'preinst': (self.chk_preinst, self.te_preinst,),
            u'postinst': (self.chk_postinst, self.te_postinst,),
            u'prerm': (self.chk_prerm, self.te_prerm),
            u'postrm': (self.chk_postrm, self.te_postrm),
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
            (self.chk_preinst, self.te_preinst, u'PREINST'),
            (self.chk_postinst, self.te_postinst, u'POSTINST'),
            (self.chk_prerm, self.te_prerm, u'PRERM'),
            (self.chk_postrm, self.te_postrm, u'POSTRM')
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
        if ID == ID_IMPORT:
            # First clear the Auto-Link display and the executable list
            self.executables.DeleteAllItems()
            self.lst_executables = []
            
            # Get executables from "files" tab
            #files = wx.GetApp().GetTopWindow().page_files.dest_area
            files = GetField(GetPage(ID_FILES), FID_LIST)
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
                    
                    postinst_list.append(u'ln -fs "{}" "{}"'.format(self.lst_executables[count], link))
                    prerm_list.append(u'rm "{}"'.format(link))
                    count += 1
                
                postinst = u'\n\n'.join(postinst_list)
                prerm = u'\n\n'.join(prerm_list)
                
                self.te_postinst.SetValue(u'#! /bin/bash -e\n\n{}'.format(postinst))
                self.chk_postinst.SetValue(True)
                self.te_prerm.SetValue(u'#! /bin/bash -e\n\n{}'.format(prerm))
                self.chk_prerm.SetValue(True)
                
                dia = wx.MessageDialog(self, GT(u'post-install and pre-remove scripts generated'), GT(u'Success'), wx.OK)
                dia.ShowModal()
                dia.Destroy()
    
    
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
    def ResetAllFields(self):
        for rb in self.grp_chk:
            self.grp_chk[rb].SetValue(False)
        
        for rb in self.grp_te:
            self.grp_te[rb].Clear()
        
        self.rb_preinst.SetValue(True)
        self.ScriptSelect(None)
        
        self.ti_autolink.SetValue(u'/usr/bin')
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
        preinst = data.split(u'<<PREINST>>\n')[1].split(u'\n<</PREINST>>')[0]
        postinst = data.split(u'<<POSTINST>>\n')[1].split(u'\n<</POSTINST>>')[0]
        prerm = data.split(u'<<PRERM>>\n')[1].split(u'\n<</PRERM>>')[0]
        postrm = data.split(u'<<POSTRM>>\n')[1].split(u'\n<</POSTRM>>')[0]
        
        if int(preinst[0]):
            self.chk_preinst.SetValue(True)
            self.te_preinst.SetValue(preinst[2:]) # 2 removes firs line
        
        else:
            self.chk_preinst.SetValue(False)
            self.te_preinst.Clear()
        
        if int(postinst[0]):
            self.chk_postinst.SetValue(True)
            self.te_postinst.SetValue(postinst[2:]) # 2 removes firs line
        
        else:
            self.chk_postinst.SetValue(False)
            self.te_postinst.Clear()
        
        if int(prerm[0]):
            self.chk_prerm.SetValue(True)
            self.te_prerm.SetValue(prerm[2:]) # 2 removes firs line
        
        else:
            self.chk_prerm.SetValue(False)
            self.te_prerm.Clear()
        
        if int(postrm[0]):
            self.chk_postrm.SetValue(True)
            self.te_postrm.SetValue(postrm[2:]) # 2 removes firs line
        
        else:
            self.chk_postrm.SetValue(False)
            self.te_postrm.Clear()
