# -*- coding: utf-8 -*-


# System imports
import wx, os

# Local imports
import dbr.font
from dbr.constants import ID_COPYRIGHT
from dbr.functions import TextIsEmpty


# Globals
copyright_header = u'Copyright © {} <copyright holder(s)> [<email>]\n\n'


class Panel(wx.Panel):
    def __init__(self, parent):  # FIXME: ID unused
        wx.Panel.__init__(self, parent, ID_COPYRIGHT, name=_(u'Copyright'))
        
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
        self.lic_choices = wx.Choice(self, -1, choices=license_list)
        self.lic_choices.SetSelection(0)
        
        wx.EVT_CHOICE(self.lic_choices, -1, self.OnSelectTemplate)
        
        template_btn = wx.Button(self, -1, _(u'Generate Template'))
        self.template_btn_simple = wx.Button(self, -1, _(u'Generate Linked Template'))
        
        self.OnSelectTemplate(self.lic_choices)
                
        wx.EVT_BUTTON(template_btn, -1, self.OnGenerateTemplate)
        wx.EVT_BUTTON(self.template_btn_simple, -1, self.GenerateLinkedTemplate)
        
        sizer_H1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_H1.Add(template_btn, 1, wx.TOP|wx.RIGHT, 5)
        sizer_H1.Add(self.template_btn_simple, 1, wx.TOP|wx.LEFT, 5)
        
        sizer_V1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_V1.Add(
            wx.StaticText(self, -1, _(u'Available Templates')),
            0,
            wx.TOP|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,
            5
        )
        sizer_V1.Add(self.lic_choices, 0, wx.TOP, 5)
        sizer_V1.Add(sizer_H1, 1, wx.LEFT, 150)
        
        ## Area where license text is displayed
        self.cp_display = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        self.cp_display.SetFont(dbr.font.MONOSPACED_LG)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(sizer_V1, 0, wx.ALL, 5)
        main_sizer.Add(self.cp_display, 1, wx.EXPAND|wx.ALL, 5)
        
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
        if type(event) != wx.Choice:
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
            if wx.MessageDialog(self.debreate, _(u'This will destroy all license text. Do you want to continue?'), _(u'Warning'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION).ShowModal() == wx.ID_NO:
                return 0
        
        return 1
    
    
    ## Retrieve copyright/license text
    #  
    #  \return
    #        \b \e tuple(str, str) : Filename & copyright/license text
    def GetPageInfo(self):
        license_text = self.cp_display.GetValue()
        
        if TextIsEmpty(license_text):
            return None
        
        return (__name__, license_text)
