# -*- coding: utf-8 -*-


import os
from wx import \
    ALIGN_CENTER as wxALIGN_CENTER, \
	ALL as wxALL, \
    NO_DEFAULT as wxNO_DEFAULT, \
	EXPAND as wxEXPAND, \
	HORIZONTAL as wxHORIZONTAL, \
    ICON_EXCLAMATION as wxICON_EXCLAMATION, \
    LEFT as wxLEFT, \
	TE_MULTILINE as wxTE_MULTILINE, \
	VERTICAL as wxVERTICAL, \
	EVT_BUTTON as wxEVT_BUTTON, \
    EVT_CHOICE as wxEVT_CHOICE, \
    ID_NO as wxID_NO, \
    RIGHT as wxRIGHT, \
    TOP as wxTOP, \
    YES_NO as wxYES_NO
from wx import \
	BoxSizer as wxBoxSizer, \
	Button as wxButton, \
	Choice as wxChoice, \
    MessageDialog as wxMessageDialog, \
	NewId as wxNewId, \
	Panel as wxPanel, \
    StaticText as wxStaticText, \
	TextCtrl as wxTextCtrl

import dbr


ID = wxNewId()  # FIXME: ID will be retrieved from constants


# Globals
copyright_header = u'Copyright © {} <copyright holder(s)> [<email>]\n\n'


class Panel(wxPanel):
    def __init__(self, parent, ID=ID):  # FIXME: ID unused
        wxPanel.__init__(self, parent, ID, name=_(u'Copyright'))
        
        self.debreate = parent.parent
        
        license_list = dbr.GetSystemLicensesList()
        # FIXME: Change to 'self.builtin_licenses
        self.local_licenses = dbr.GetLicenseTemplatesList()
        
        # Do not use local licenses if already located on system
        for lic in license_list:
            if lic in self.local_licenses:
                self.local_licenses.remove(lic)
        
        # Add the remaining licenses to the selection list
        for lic in self.local_licenses:
            license_list.append(lic)
        
        license_list.sort(key=unicode.lower)
        
        ## A list of available license templates
        self.lic_choices = wxChoice(self, -1, choices=license_list)
        self.lic_choices.SetSelection(0)
        
        wxEVT_CHOICE(self.lic_choices, -1, self.OnSelectTemplate)
        
        template_btn = wxButton(self, -1, _(u'Generate Template'))
        self.template_btn_simple = wxButton(self, -1, _(u'Generate Linked Template'))
        
        self.OnSelectTemplate(self.lic_choices)
                
        wxEVT_BUTTON(template_btn, -1, self.OnGenerateTemplate)
        wxEVT_BUTTON(self.template_btn_simple, -1, self.GenerateLinkedTemplate)
        
        sizer_H1 = wxBoxSizer(wxHORIZONTAL)
        sizer_H1.Add(template_btn, 1, wxTOP|wxRIGHT, 5)
        sizer_H1.Add(self.template_btn_simple, 1, wxTOP|wxLEFT, 5)
        
        sizer_V1 = wxBoxSizer(wxHORIZONTAL)
        sizer_V1.Add(
            wxStaticText(self, -1, _(u'Available Templates')),
            0,
            wxTOP|wxLEFT|wxRIGHT|wxALIGN_CENTER,
            5
        )
        sizer_V1.Add(self.lic_choices, 0, wxTOP, 5)
        sizer_V1.Add(sizer_H1, 1, wxLEFT, 150)
        
        ## Area where license text is displayed
        self.cp_display = wxTextCtrl(self, style=wxTE_MULTILINE)
        
        main_sizer = wxBoxSizer(wxVERTICAL)
        main_sizer.Add(sizer_V1, 0, wxALL, 5)
        main_sizer.Add(self.cp_display, 1, wxEXPAND|wxALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
    
    def GetCopyright(self):
        return self.cp_display.GetValue()
    
    def GatherData(self):
        data = self.GetCopyright()
        return u'<<COPYRIGHT>>\n{}\n<</COPYRIGHT>>'.format(data)
    
    def SetCopyright(self, data):
        self.cp_display.SetValue(data)
    
    def ResetAllFields(self):
        self.cp_display.Clear()
    
    def OnSelectTemplate(self, event):
        if type(event) != wxChoice:
            choice = event.GetEventObject()
        else:
            choice = event
        
        template = choice.GetString(choice.GetSelection())
        
        if template in self.local_licenses:
            self.template_btn_simple.Disable()
        else:
            self.template_btn_simple.Enable()
    
    def OnGenerateTemplate(self, event):
        license_name = self.lic_choices.GetString(self.lic_choices.GetSelection())
        
        if dbr.FieldEnabled(self.template_btn_simple):
            self.CopyStandardLicense(license_name)
        
        else:
            self.GenerateTemplate(license_name)
    
    def CopyStandardLicense(self, license_name):
        if self.DestroyLicenseText():
            license_path = u'{}/{}'.format(dbr.system_licenses_path, license_name)
            
            if not os.path.isfile(license_path):
                # FIXME: Should have an error dialog pop up
                print(u'ERROR: Could not locate standard license: {}'.format(license_path))
                return
            
            self.cp_display.Clear()
            self.cp_display.LoadFile(license_path)
            
            # FIXME: Need to clear empty lines & beginning of document
            
            self.cp_display.SetInsertionPoint(0)
            self.cp_display.WriteText(copyright_header.format(dbr.GetYear()))
            self.cp_display.SetInsertionPoint(0)
            
        self.cp_display.SetFocus()
    
    def GenerateTemplate(self, l_name):
        if self.DestroyLicenseText():
            self.cp_display.Clear()
            
            l_path = dbr.GetLicenseTemplateFile(l_name)
            
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
                            l_lines[l_index] = str(dbr.GetYear()).join(LI.split(DEL))
                        l_index += 1
                
                self.cp_display.SetValue(u'\n'.join(l_lines))
                
                self.cp_display.SetInsertionPoint(0)
        
        self.cp_display.SetFocus()
    
    def GenerateLinkedTemplate(self, event):
        if self.DestroyLicenseText():
            self.cp_display.Clear()
            
            license_path = u'{}/{}'.format(dbr.system_licenses_path, self.lic_choices.GetString(self.lic_choices.GetSelection()))
    
            self.cp_display.WriteText(copyright_header.format(dbr.GetYear()))
            self.cp_display.WriteText(license_path)
            
            self.cp_display.SetInsertionPoint(0)
            
        self.cp_display.SetFocus()
    
    def DestroyLicenseText(self):
        empty = self.cp_display.IsEmpty()
        
        if not empty:
            if wxMessageDialog(self.debreate, _(u'This will destroy all license text. Do you want to continue?'), _(u'Warning'),
                    wxYES_NO|wxNO_DEFAULT|wxICON_EXCLAMATION).ShowModal() == wxID_NO:
                return 0
        
        return 1
