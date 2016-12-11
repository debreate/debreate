# -*- coding: utf-8 -*-

## \package wiz_bin.copyright

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.dialogs            import ConfirmationDialog
from dbr.functions          import GetSystemLicensesList
from dbr.functions          import TextIsEmpty
from dbr.language           import GT
from dbr.textinput          import MonospaceTextCtrl
from globals                import ident
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetTopWindow


## Copyright page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ident.COPYRIGHT, name=GT(u'Copyright'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        # FIXME: Ignore symbolic links
        opts_licenses = GetSystemLicensesList()
        
        ## A list of available license templates
        self.sel_templates = wx.Choice(self, choices=opts_licenses, name=u'list»')
        self.sel_templates.SetSelection(0)
        
        btn_template = wx.Button(self, label=GT(u'Generate Template'), name=u'gen»')
        
        if not self.sel_templates.GetCount():
            btn_template.Enable(False)
            self.sel_templates.Enable(False)
        
        ## Area where license text is displayed
        self.dsp_copyright = MonospaceTextCtrl(self, name=u'license')
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_template, 1)
        lyt_buttons.Add(self.sel_templates, 1)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_buttons, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        lyt_main.Add(self.dsp_copyright, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        btn_template.Bind(wx.EVT_BUTTON, self.GenerateTemplate)
    
    
    ## TODO: Doxygen
    def DestroyLicenseText(self):
        if not TextIsEmpty(self.dsp_copyright.GetValue()):
            warn_msg = GT(u'This will destroy all license text. Do you want to continue?')
            warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))
            
            if ConfirmationDialog(GetTopWindow(), text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
                return False
        
        return True
    
    
    ## TODO: Doxygen
    def ExportPage(self):
        return self.GetCopyright()
    
    
    ## TODO: Doxygen
    def GatherData(self):
        data = self.GetCopyright()
        return u'<<COPYRIGHT>>\n{}\n<</COPYRIGHT>>'.format(data)
    
    
    ## TODO: Doxygen
    def GenerateTemplate(self, event=None):
        if not self.DestroyLicenseText():
            return
        
        self.dsp_copyright.Clear()
        
        lic_path = u'/usr/share/common-licenses/{}'.format(self.sel_templates.GetStringSelection())
        cpright = u'Copyright: <year> <copyright holder> <email>'
        
        self.dsp_copyright.SetValue(u'{}\n\n{}'.format(cpright, lic_path))
    
    
    ## TODO: Doxygen
    def GetCopyright(self):
        return self.dsp_copyright.GetValue()
    
    
    ## TODO: Doxygen
    def IsBuildExportable(self):
        return not TextIsEmpty(self.dsp_copyright.GetValue())
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.dsp_copyright.Clear()
    
    
    ## TODO: Doxygen
    def SetCopyright(self, data):
        self.dsp_copyright.SetValue(data)
