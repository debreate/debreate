# -*- coding: utf-8 -*-

## \package wiz_bin.copyright

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.error              import ShowError
from dbr.functions          import GetSystemLicensesList
from dbr.functions          import GetYear
from dbr.functions          import RemovePreWhitespace
from dbr.functions          import TextIsEmpty
from dbr.language           import GT
from dbr.templates          import GetLicenseTemplateFile
from dbr.templates          import GetLicenseTemplatesList
from dbr.templates          import application_licenses_path
from dbr.templates          import local_licenses_path
from dbr.textinput          import MT_BTN_BR
from dbr.textinput          import MonospaceTextCtrl
from dbr.wizard             import WizardPage
from globals                import ident
from globals.constants      import system_licenses_path
from globals.errorcodes     import errno
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import FieldEnabled, GetPage
from globals.wizardhelper   import GetTopWindow


# Globals
copyright_header = GT(u'Copyright © {} <copyright holder(s)> [<email>]\n\n')


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.COPYRIGHT)
        
        # FIXME: Ignore symbolic links
        license_list = GetSystemLicensesList()
        # FIXME: Change variable name to 'self.builtin_licenses
        self.local_licenses = GetLicenseTemplatesList()
        
        # Do not use local licenses if already located on system
        for lic in license_list:
            if lic in self.local_licenses:
                self.local_licenses.remove(lic)
        
        # Add the remaining licenses to the selection list
        for lic in self.local_licenses:
            license_list.append(lic)
        
        license_list.sort(key=unicode.lower)
        
        ## A list of available license templates
        self.lic_choices = wx.Choice(self, -1, choices=license_list)
        self.lic_choices.SetSelection(0)
        
        template_btn = wx.Button(self, label=GT(u'Generate Template'), name=u'full')
        self.template_btn_simple = wx.Button(self, label=GT(u'Generate Linked Template'), name=u'link')
        
        self.OnSelectTemplate(self.lic_choices)
        
        ## Area where license text is displayed
        self.cp_display = MonospaceTextCtrl(self, button=MT_BTN_BR, name=u'license')
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        sizer_H1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_H1.Add(template_btn, 1, wx.TOP|wx.RIGHT, 5)
        sizer_H1.Add(self.template_btn_simple, 1, wx.TOP|wx.LEFT, 5)
        
        sizer_V1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_V1.Add(
            wx.StaticText(self, -1, GT(u'Available Templates')),
            0,
            wx.TOP|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,
            5
        )
        sizer_V1.Add(self.lic_choices, 0, wx.TOP, 5)
        sizer_V1.Add(sizer_H1, 1, wx.LEFT, 150)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(sizer_V1, 0, wx.ALL, 5)
        main_sizer.Add(self.cp_display, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
        
        # *** Event handlers *** #
        
        wx.EVT_CHOICE(self.lic_choices, -1, self.OnSelectTemplate)
        
        wx.EVT_BUTTON(template_btn, -1, self.OnGenerateTemplate)
        wx.EVT_BUTTON(self.template_btn_simple, -1, self.GenerateLinkedTemplate)
    
    
    ## TODO: Doxygen
    def CopyStandardLicense(self, license_name):
        main_window = GetTopWindow()
        
        if self.DestroyLicenseText():
            license_path = u'{}/{}'.format(system_licenses_path, license_name)
            
            if not os.path.isfile(license_path):
                ShowError(main_window, u'{}: {}'.format(GT(u'Could not locate standard license'), license_path))
                return
            
            FILE = open(license_path, u'r')
            license_text = FILE.read()
            FILE.close()
            
            self.cp_display.Clear()
            self.cp_display.SetValue(RemovePreWhitespace(license_text))
            
            add_header = (
                u'Artistic',
                u'BSD',
            )
            
            self.cp_display.SetInsertionPoint(0)
            
            if license_name in add_header:
                self.cp_display.WriteText(copyright_header.format(GetYear()))
                self.cp_display.SetInsertionPoint(0)
            
        self.cp_display.SetFocus()
    
    
    ## TODO: Doxygen
    def DestroyLicenseText(self):
        main_window = GetTopWindow()
        
        empty = TextIsEmpty(self.cp_display.GetValue())
        
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
            self.cp_display.Clear()
            
            license_path = u'{}/{}'.format(system_licenses_path, self.lic_choices.GetString(self.lic_choices.GetSelection()))
    
            self.cp_display.WriteText(copyright_header.format(GetYear()))
            self.cp_display.WriteText(license_path)
            
            self.cp_display.SetInsertionPoint(0)
            
        self.cp_display.SetFocus()
    
    
    ## TODO: Doxygen
    def GenerateTemplate(self, l_name):
        if self.DestroyLicenseText():
            self.cp_display.Clear()
            
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
                
                self.cp_display.SetValue(u'\n'.join(l_lines))
                
                self.cp_display.SetInsertionPoint(0)
        
        self.cp_display.SetFocus()
    
    
    ## TODO: Doxygen
    def GetCopyright(self):
        return self.cp_display.GetValue()
    
    
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
        license_text = self.cp_display.GetValue()
        
        if TextIsEmpty(license_text):
            return None
        
        return (__name__, license_text)
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, filename):
        if not os.path.isfile(filename):
            return errno.ENOENT
        
        FILE = open(filename, u'r')
        copyright_data = FILE.read().split(u'\n')
        FILE.close()
        
        # Remove preceding empty lines
        remove_index = 0
        for I in copyright_data:
            if not TextIsEmpty(I):
                break
            
            remove_index += 1
        
        for I in reversed(range(remove_index)):
            copyright_data.remove(copyright_data[I])
        
        copyright_data = u'\n'.join(copyright_data)
        
        self.cp_display.SetValue(copyright_data)
        
        return 0
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        return not TextIsEmpty(self.cp_display.GetValue())
    
    
    ## TODO: Doxygen
    def OnGenerateTemplate(self, event=None):
        license_name = self.lic_choices.GetString(self.lic_choices.GetSelection())
        
        if FieldEnabled(self.template_btn_simple):
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
        
        if template in self.local_licenses:
            self.template_btn_simple.Disable()
        else:
            self.template_btn_simple.Enable()
        
        self.SetTemplateToolTip()
    
    
    ## TODO: Doxygen
    def ResetPageInfo(self):
        self.cp_display.Clear()
    
    
    ## TODO: Doxygen
    def SetCopyright(self, data):
        self.cp_display.SetValue(data)
    
    
    ## TODO: Doxygen
    def SetTemplateToolTip(self):
        license_name = self.lic_choices.GetString(self.lic_choices.GetSelection())
        license_path = self.GetLicensePath(license_name)
        
        if license_path:
            self.lic_choices.SetToolTip(wx.ToolTip(license_path))
            return
        
        self.lic_choices.SetToolTip(None)
