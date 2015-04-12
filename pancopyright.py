import wxversion
wxversion.select(['2.6', '2.7', '2.8'])
import wx

ID = wx.NewId()

class Panel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id, name=_('Copyright'))
        
        self.debreate = parent.parent
        
        self.cp_display = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.cp_display, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
    
    def GetCopyright(self):
        return self.cp_display.GetValue()
    
    def GatherData(self):
        data = self.GetCopyright()
        return "<<COPYRIGHT>>\n%s\n<</COPYRIGHT>>" % data
    
    def SetCopyright(self, data):
        self.cp_display.SetValue(data)
    
    def ResetAllFields(self):
        self.cp_display.Clear()