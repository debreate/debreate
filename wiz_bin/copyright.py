# -*- coding: utf-8 -*-


import wx

from dbr.language   import GT
from globals.ident  import ID_COPYRIGHT


class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_COPYRIGHT, name=GT(u'Copyright'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        lic_options = (
            u'Apache-2.0', u'Artistic', u'BSD', u'GFDL', u'GFDL-1.2',
            u'GFDL-1.3', u'GPL', u'GPL-1', u'GPL-2', u'GPL-3', u'LGPL',
            u'LGPL-2', u'LGPL-2.1', u'LGPL-3'
        )
        template_btn = wx.Button(self, -1, u'Generate Template')
        self.template_lic = wx.Choice(self, -1, choices=lic_options)
        self.template_lic.SetSelection(0)
        
        wx.EVT_BUTTON(template_btn, -1, self.GenerateTemplate)
        
        template_sizer = wx.BoxSizer(wx.HORIZONTAL)
        template_sizer.Add(template_btn, 1)
        template_sizer.Add(self.template_lic, 1)
        
        self.cp_display = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(template_sizer, 0, wx.ALL, 5)
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
    
    def GenerateTemplate(self, event):
        lic_path = u'/usr/share/common-licenses/{}'.format(self.template_lic.GetString(self.template_lic.GetSelection()))
        text = u''
        if (not self.cp_display.IsEmpty()):
            text = u'\n{}'.format(self.cp_display.GetValue())
            self.cp_display.Clear()
        copyright = u'Copyright: <year> <copyright holder> <email>'
        text = u'{}\n\n{}\n{}'.format(copyright, lic_path, text)
        self.cp_display.SetValue(text)
