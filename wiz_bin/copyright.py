# -*- coding: utf-8 -*-

## \package wiz_bin.copyright

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.functions          import GetLongestLine
from dbr.language           import GT
from dbr.log                import Logger
from dbr.templates          import GetCustomLicenses
from dbr.templates          import GetLocalLicenses
from dbr.templates          import GetSysLicenses
from dbr.templates          import app_licenses_path
from dbr.templates          import local_licenses_path
from dbr.templates          import sys_licenses_path
from globals.dateinfo       import GetYear
from globals.execute        import ExecuteCommand
from globals.execute        import GetExecutable
from globals.fileio         import ReadFile
from globals.ident          import btnid
from globals.ident          import pgid
from globals.ident          import selid
from globals.strings        import GS
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetMainWindow
from input.select           import Choice
from input.text             import TextAreaPanelESS
from ui.button              import CreateButton
from ui.dialog              import ConfirmationDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.style               import layout as lyt
from ui.wizard              import WizardPage


# Globals
copyright_header = GT(u'Copyright © {} <copyright holder(s)> [<email>]')


## Copyright page
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.COPYRIGHT)
        
        self.custom_licenses = []
        
        ## A list of available license templates
        self.sel_templates = Choice(self, selid.LICENSE, name=u'list»')
        self.sel_templates.default = 0
        
        # Initialize the template list
        self.OnRefreshTemplateList()
        
        btn_template = CreateButton(self, GT(u'Full Template'), u'full', name=u'full»')
        self.btn_template_simple = CreateButton(self, GT(u'Short Template'), u'short',
                name=u'short»')
        btn_refresh = CreateButton(self, GT(u'Refresh Template List'), u'refresh', btnid.REFRESH,
                name=u'btn refresh')
        btn_open = CreateButton(self, GT(u'Open Template Directory'), u'browse', btnid.BROWSE,
                name=u'btn opendir', commands=u'xdg-open')
        
        if not self.sel_templates.GetCount():
            self.sel_templates.Enable(False)
            btn_template.Enable(False)
            self.btn_template_simple.Enable(False)
        
        ## Area where license text is displayed
        self.dsp_copyright = TextAreaPanelESS(self, monospace=True, name=u'license')
        self.dsp_copyright.EnableDropTarget()
        
        SetPageToolTips(self)
        
        # Initiate tooltip for drop-down selector
        if self.sel_templates.IsEnabled():
            self.OnSelectTemplate(self.sel_templates)
        
        # *** Event Handling *** #
        
        self.sel_templates.Bind(wx.EVT_CHOICE, self.OnSelectTemplate)
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnOpenPath)
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnRefreshTemplateList)
        btn_template.Bind(wx.EVT_BUTTON, self.OnFullTemplate)
        self.btn_template_simple.Bind(wx.EVT_BUTTON, self.OnSimpleTemplate)
        
        # *** Layout *** #
        
        lyt_top = BoxSizer(wx.HORIZONTAL)
        lyt_top.Add(wx.StaticText(self, label=GT(u'Available Templates')), 0,
                lyt.CNTR_VERT)
        lyt_top.Add(self.sel_templates, 0, lyt.CNTR_VERT|wx.LEFT, 5)
        lyt_top.Add(btn_template, 0, wx.LEFT, 5)
        lyt_top.Add(self.btn_template_simple)
        lyt_top.Add(btn_refresh)
        lyt_top.Add(btn_open)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_top, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        lyt_main.Add(self.dsp_copyright, 1, wx.EXPAND|lyt.PAD_LRB, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def DestroyLicenseText(self):
        if not TextIsEmpty(self.dsp_copyright.GetValue()):
            warn_msg = GT(u'This will destroy all license text.')
            warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))
            
            if ConfirmationDialog(GetMainWindow(), text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
                return False
        
        return True
    
    
    ## TODO: Doxygen
    def ExportPage(self):
        return self.Get()
    
    
    ## TODO: Doxygen
    def GatherData(self):
        data = self.Get()
        return u'<<COPYRIGHT>>\n{}\n<</COPYRIGHT>>'.format(data)
    
    
    ## Retrieve contents of page
    def Get(self):
        return self.dsp_copyright.GetValue()
    
    
    ## Retrieves the name of the template currently selected
    def GetCurrentTemplateName(self):
        return GetField(self, selid.LICENSE).GetStringSelection()
    
    
    ## TODO: Doxygen
    def GetLicensePath(self, template_name=None):
        # Default to currently selected template
        if not template_name:
            template_name = self.GetCurrentTemplateName()
        
        # User templates have priority
        license_path = u'{}/{}'.format(local_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        license_path = u'{}/{}'.format(sys_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        license_path = u'{}/{}'.format(app_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        return None
    
    
    ## Tells the app whether this page should be added to build
    def IsBuildExportable(self):
        return not TextIsEmpty(self.dsp_copyright.GetValue())
    
    
    ## TODO: Doxygen
    def OnFullTemplate(self, event=None):
        selected_template = self.sel_templates.GetStringSelection()
        template_file = self.GetLicensePath(selected_template)
        
        if self.DestroyLicenseText():
            if not template_file or not os.path.isfile(template_file):
                ShowErrorDialog(GT(u'Could not locate license file: {}').format(self.GetCurrentTemplateName()))
                
                return
            
            Logger.Debug(__name__, u'Copying license {}'.format(template_file))
            
            license_text = ReadFile(template_file, no_strip=u' ')
            
            # Number defines how many empty lines to add after the copyright header
            # Boolean/Integer defines whether copyright header should be centered/offset
            add_header = {
                u'Artistic': (1, True),
                u'BSD': (0, False),
            }
            
            template_name = os.path.basename(template_file)
            if template_name in add_header:
                license_text = license_text.split(u'\n')
                
                empty_lines = add_header[template_name][0]
                for L in range(empty_lines):
                    license_text.insert(0, wx.EmptyString)
                
                header = copyright_header.format(GetYear())
                
                center_header = add_header[template_name][1]
                if center_header:
                    Logger.Debug(__name__, u'Centering header...')
                    
                    offset = 0
                    
                    # Don't use isinstance() here because boolean is an instance of integer
                    if type(center_header) == int:
                        offset = center_header
                    
                    else:
                        # Use the longest line found in the text to center the header
                        longest_line = GetLongestLine(license_text)
                        
                        Logger.Debug(__name__, u'Longest line: {}'.format(longest_line))
                        
                        header_length = len(header)
                        if header_length < longest_line:
                            offset = (longest_line - header_length) / 2
                    
                    if offset:
                        Logger.Debug(__name__, u'Offset: {}'.format(offset))
                        
                        header = u'{}{}'.format(u' ' * offset, header)
                
                # Special changes for BSD license
                if template_name == u'BSD':
                    line_index = 0
                    for LI in license_text:
                        if u'copyright (c)' in LI.lower():
                            license_text[line_index] = header
                            
                            break
                        
                        line_index += 1
                
                else:
                    license_text.insert(0, header)
                
                license_text = u'\n'.join(license_text)
            
            if not license_text:
                ShowErrorDialog(GT(u'License template is empty'))
                
                return
            
            self.dsp_copyright.SetValue(license_text)
            self.dsp_copyright.SetInsertionPoint(0)
        
        self.dsp_copyright.SetFocus()
    
    
    ## Opens directory containing currently selected license
    def OnOpenPath(self, event=None):
        CMD_open = GetExecutable(u'xdg-open')
        
        if CMD_open:
            path = self.GetLicensePath()
            
            if not path:
                ShowErrorDialog(GT(u'Error retrieving template path: {}').format(self.GetCurrentTemplateName()))
                
                return False
            
            path = os.path.dirname(path)
            
            if os.path.isdir(path):
                ExecuteCommand(CMD_open, (path,))
                
                return True
        
        return False
    
    
    ## Repopulates template list
    def OnRefreshTemplateList(self, event=None):
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
        
        self.custom_licenses.sort(key=GS.lower)
        
        sel_templates = GetField(self, selid.LICENSE)
        
        selected = None
        if sel_templates.GetCount():
            selected = sel_templates.GetStringSelection()
        
        sel_templates.Set(sorted(licenses, key=GS.lower))
        
        if selected:
            if not sel_templates.SetStringSelection(selected):
                # Selected template file was not found
                sel_templates.SetSelection(sel_templates.GetDefaultValue())
                
                # Update short template button enabled state
                self.OnSelectTemplate()
        
        else:
            sel_templates.SetSelection(sel_templates.GetDefaultValue())
    
    
    ## Enables/Disables simple template button
    #  
    #  Simple template generation is only available
    #  for system  licenses.
    def OnSelectTemplate(self, event=None):
        choice = GetField(self, selid.LICENSE)
        if choice:
            template = choice.GetString(choice.GetSelection())
            
            if template in self.custom_licenses:
                self.btn_template_simple.Disable()
            
            else:
                self.btn_template_simple.Enable()
            
            self.SetTemplateToolTip()
    
    
    ## TODO: Doxygen
    def OnSimpleTemplate(self, event=None):
        if self.DestroyLicenseText():
            self.dsp_copyright.Clear()
            
            license_path = u'{}/{}'.format(sys_licenses_path, self.sel_templates.GetString(self.sel_templates.GetSelection()))
            
            self.dsp_copyright.WriteText(u'{}\n\n{}'.format(copyright_header.format(GetYear()), license_path))
            self.dsp_copyright.SetInsertionPoint(0)
        
        self.dsp_copyright.SetFocus()
    
    
    ## Resets all page fields to default values
    def Reset(self):
        self.dsp_copyright.Clear()
        
        if self.sel_templates.IsEnabled():
            self.sel_templates.SetSelection(self.sel_templates.default)
            self.OnSelectTemplate(self.sel_templates)
    
    
    ## Sets the text of the displayed copyright
    def Set(self, data):
        self.dsp_copyright.SetValue(data)
    
    
    ## TODO: Doxygen
    def SetTemplateToolTip(self):
        license_name = self.sel_templates.GetString(self.sel_templates.GetSelection())
        license_path = self.GetLicensePath(license_name)
        
        if license_path:
            self.sel_templates.SetToolTip(wx.ToolTip(license_path))
            return
        
        self.sel_templates.SetToolTip(None)
