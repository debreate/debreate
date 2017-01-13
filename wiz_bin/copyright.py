# -*- coding: utf-8 -*-

## \package wiz_bin.copyright

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.error              import ShowError
from dbr.functions          import GetSystemLicensesList
from dbr.functions          import GetYear
from dbr.functions          import RemovePreWhitespace
from dbr.language           import GT
from dbr.templates          import GetLicenseTemplateFile
from dbr.templates          import GetLicenseTemplatesList
from dbr.templates          import application_licenses_path
from dbr.templates          import local_licenses_path
from dbr.textinput          import MonospaceTextArea
from dbr.wizard             import WizardPage
from globals                import ident
from globals.constants      import system_licenses_path
from globals.errorcodes     import errno
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import FieldEnabled
from globals.wizardhelper   import GetPage
from globals.wizardhelper   import GetTopWindow


# Globals
copyright_header = GT(u'Copyright © {} <copyright holder(s)> [<email>]\n\n')


## Copyright page
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.COPYRIGHT)
        
        # FIXME: Ignore symbolic links
        opts_licenses = GetSystemLicensesList()
        
        # FIXME: Change variable name to 'self.builtin_licenses
        self.opts_local_licenses = GetLicenseTemplatesList()
        
        # Do not use local licenses if already located on system
        for lic in opts_licenses:
            if lic in self.opts_local_licenses:
                self.opts_local_licenses.remove(lic)
        
        # Add the remaining licenses to the selection list
        for lic in self.opts_local_licenses:
            opts_licenses.append(lic)
        
        opts_licenses.sort(key=unicode.lower)
        
        ## A list of available license templates
        self.sel_templates = wx.Choice(self, choices=opts_licenses, name=u'list»')
        self.sel_templates.default = 0
        self.sel_templates.SetSelection(self.sel_templates.default)
        
        btn_template = wx.Button(self, label=GT(u'Generate Template'), name=u'full»')
        self.btn_template_simple = wx.Button(self, label=GT(u'Generate Linked Template'), name=u'link»')
        
        if not self.sel_templates.GetCount():
            self.sel_templates.Enable(False)
            btn_template.Enable(False)
            self.btn_template_simple.Enable(False)
        
        ## Area where license text is displayed
        self.dsp_copyright = MonospaceTextArea(self, name=u'license')
        
        SetPageToolTips(self)
        
        if self.sel_templates.IsEnabled():
            self.OnSelectTemplate(self.sel_templates)
        
        # *** Layout *** #
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_template, 1, wx.TOP|wx.RIGHT, 5)
        lyt_buttons.Add(self.btn_template_simple, 1, wx.TOP|wx.LEFT, 5)
        
        lyt_label = wx.BoxSizer(wx.HORIZONTAL)
        lyt_label.Add(
            wx.StaticText(self, label=GT(u'Available Templates')),
            0,
            wx.TOP|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,
            5
        )
        lyt_label.Add(self.sel_templates, 0, wx.TOP, 5)
        lyt_label.Add(lyt_buttons, 1, wx.LEFT, 150)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_label, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        lyt_main.Add(self.dsp_copyright, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        self.sel_templates.Bind(wx.EVT_CHOICE, self.OnSelectTemplate)
        
        btn_template.Bind(wx.EVT_BUTTON, self.OnGenerateTemplate)
        self.btn_template_simple.Bind(wx.EVT_BUTTON, self.GenerateLinkedTemplate)
    
    
    ## TODO: Doxygen
    def CopyStandardLicense(self, license_name):
        main_window = GetTopWindow()
        
        if self.DestroyLicenseText():
            license_path = u'{}/{}'.format(system_licenses_path, license_name)
            
            if not os.path.isfile(license_path):
                ShowError(main_window, u'{}: {}'.format(GT(u'Could not locate standard license'), license_path))
                return
            
            FILE_BUFFER = open(license_path, u'r')
            license_text = FILE_BUFFER.read()
            FILE_BUFFER.close()
            
            self.dsp_copyright.Clear()
            self.dsp_copyright.SetValue(RemovePreWhitespace(license_text))
            
            add_header = (
                u'Artistic',
                u'BSD',
            )
            
            self.dsp_copyright.SetInsertionPoint(0)
            
            if license_name in add_header:
                self.dsp_copyright.WriteText(copyright_header.format(GetYear()))
                self.dsp_copyright.SetInsertionPoint(0)
        
        self.dsp_copyright.SetFocus()
    
    
    ## TODO: Doxygen
    def DestroyLicenseText(self):
        main_window = GetTopWindow()
        
        empty = TextIsEmpty(self.dsp_copyright.GetValue())
        
        if not empty:
            if wx.MessageDialog(main_window, GT(u'This will destroy all license text. Do you want to continue?'), GT(u'Warning'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION).ShowModal() == wx.ID_NO:
                return 0
        
        return 1
    
    
    ## TODO: Doxygen
    def ExportBuild(self, stage):
        stage = u'{}/usr/share/doc/{}'.format(stage, GetPage(ident.CONTROL).GetPackageName()).replace(u'//', u'/')
        
        # FIXME: Should be error check
        self.Export(stage, u'copyright')
        
        return (0, None)
    
    
    ## TODO: Doxygen
    def GenerateLinkedTemplate(self, event=None):
        if self.DestroyLicenseText():
            self.dsp_copyright.Clear()
            
            license_path = u'{}/{}'.format(system_licenses_path, self.sel_templates.GetString(self.sel_templates.GetSelection()))
            
            self.dsp_copyright.WriteText(copyright_header.format(GetYear()))
            self.dsp_copyright.WriteText(license_path)
            
            self.dsp_copyright.SetInsertionPoint(0)
        
        self.dsp_copyright.SetFocus()
    
    
    ## TODO: Doxygen
    def GenerateTemplate(self, l_name):
        if self.DestroyLicenseText():
            self.dsp_copyright.Clear()
            
            l_path = GetLicenseTemplateFile(l_name)
            
            if l_path:
                l_data = open(l_path)
                l_lines = l_data.read().split(u'\n')
                l_data.close()
                
                delimeters = (
                    u'<year>',
                    u'<years>',
                    u'<year(s)>',
                    u'<date>',
                    u'<dates>',
                    u'<date(s)>',
                )
                
                for DEL in delimeters:
                    l_index = 0
                    for LI in l_lines:
                        if DEL in LI:
                            l_lines[l_index] = str(GetYear()).join(LI.split(DEL))
                        l_index += 1
                
                self.dsp_copyright.SetValue(u'\n'.join(l_lines))
                
                self.dsp_copyright.SetInsertionPoint(0)
        
        self.dsp_copyright.SetFocus()
    
    
    ## TODO: Doxygen
    def GetCopyright(self):
        return self.dsp_copyright.GetValue()
    
    
    ## TODO: Doxygen
    def GetLicensePath(self, template_name):
        # User templates have priority
        license_path = u'{}/{}'.format(local_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        license_path = u'{}/{}'.format(system_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        license_path = u'{}/{}'.format(application_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        return None
    
    
    ## Retrieve copyright/license text
    #  
    #  \return
    #        \b \e tuple(str, str) : Filename & copyright/license text
    def GetPageInfo(self):
        license_text = self.dsp_copyright.GetValue()
        
        if TextIsEmpty(license_text):
            return None
        
        return (__name__, license_text)
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, filename):
        if not os.path.isfile(filename):
            return errno.ENOENT
        
        FILE_BUFFER = open(filename, u'r')
        copyright_data = FILE_BUFFER.read().split(u'\n')
        FILE_BUFFER.close()
        
        # Remove preceding empty lines
        remove_index = 0
        for I in copyright_data:
            if not TextIsEmpty(I):
                break
            
            remove_index += 1
        
        for I in reversed(range(remove_index)):
            copyright_data.remove(copyright_data[I])
        
        copyright_data = u'\n'.join(copyright_data)
        
        self.dsp_copyright.SetValue(copyright_data)
        
        return 0
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        return not TextIsEmpty(self.dsp_copyright.GetValue())
    
    
    ## TODO: Doxygen
    def OnGenerateTemplate(self, event=None):
        license_name = self.sel_templates.GetString(self.sel_templates.GetSelection())
        
        if FieldEnabled(self.btn_template_simple):
            self.CopyStandardLicense(license_name)
        
        else:
            self.GenerateTemplate(license_name)
    
    
    ## TODO: Doxygen
    def OnSelectTemplate(self, event=None):
        if isinstance(event, wx.Choice):
            choice = event
        
        else:
            choice = event.GetEventObject()
        
        template = choice.GetString(choice.GetSelection())
        
        if template in self.opts_local_licenses:
            self.btn_template_simple.Disable()
        
        else:
            self.btn_template_simple.Enable()
        
        self.SetTemplateToolTip()
    
    
    ## TODO: Doxygen
    def ResetPageInfo(self):
        self.dsp_copyright.Clear()
        
        if self.sel_templates.IsEnabled():
            self.sel_templates.SetSelection(self.sel_templates.default)
            self.OnSelectTemplate(self.sel_templates)
    
    
    ## TODO: Doxygen
    def SetCopyright(self, data):
        self.dsp_copyright.SetValue(data)
    
    
    ## TODO: Doxygen
    def SetTemplateToolTip(self):
        license_name = self.sel_templates.GetString(self.sel_templates.GetSelection())
        license_path = self.GetLicensePath(license_name)
        
        if license_path:
            self.sel_templates.SetToolTip(wx.ToolTip(license_path))
            return
        
        self.sel_templates.SetToolTip(None)
