# -*- coding: utf-8 -*-

## \package dbr.mansect

# MIT licensing
# See: docs/LICENSE.txt


import traceback, wx

from dbr.buttons        import ButtonRemove
from dbr.dialogs        import ShowErrorDialog
from dbr.language       import GT
from dbr.log            import Logger
from dbr.selectinput    import ComboBox
from dbr.textinput      import TextArea
from dbr.textinput      import TextAreaPanel
from globals.dateinfo   import GetDayInt
from globals.dateinfo   import GetMonthInt
from globals.dateinfo   import GetYear
from ui.layout          import BoxSizer


## Base class for manpage parts
class ManBase:
    def __init__(self, parent):
        self.Parent = parent
        
        # Allow adding multiple instances of object
        self.Multiple = False
        
        self.lyt_main = BoxSizer(wx.VERTICAL)
    
    
    ## TODO: Doxygen
    def _add_field(self, label, window, count=1, expand=False):
        if isinstance(label, (unicode, str)):
            label = wx.StaticText(self.Parent, label=label)
        
        lyt_field = BoxSizer(wx.HORIZONTAL)
        
        for X in range(count):
            if expand:
                lyt_field.Add(window, 1, wx.EXPAND)
                continue
            
            lyt_field.Add(window, 1)
        
        self.lyt_main.Add(label, 0, wx.ALIGN_BOTTOM|wx.LEFT, 5)
        
        if expand:
            self.lyt_main.Add(lyt_field, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 5)
        
        else:
            self.lyt_main.Add(lyt_field, 1, wx.LEFT|wx.BOTTOM, 5)
        
        self.Parent.Layout()
    
    
    ## Retrieve the main sizer object
    def GetObject(self):
        return self.lyt_main
    
    
    ## Checks multiple instances can be uses
    def MultipleAllowed(self):
        return self.Multiple


## TODO: Doxygen
#  
#  This section is required
#  FIXME: Should derive from wx.Panel/BorderedPanel???
class ManBanner(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        txt_date = wx.StaticText(parent, label=GT(u'Date'))
        spin_year = wx.SpinCtrl(parent, min=1900, max=2100, initial=GetYear(string_value=False))
        spin_month = wx.SpinCtrl(parent, min=1, max=12, initial=GetMonthInt())
        spin_day = wx.SpinCtrl(parent, min=1, max=31, initial=GetDayInt())
        
        # FIXME: What is this for?
        txt_unknown1 = wx.StaticText(parent, label=GT(u'Unknown'))
        ti_unknown1 = wx.TextCtrl(parent)
        
        # FIXME: What is this for?
        txt_unknown2 = wx.StaticText(parent, label=GT(u'Unknown'))
        ti_unknown2 = wx.TextCtrl(parent)
        
        # *** Layout *** #
        
        lyt_date = wx.GridBagSizer()
        lyt_date.Add(txt_date, (1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        lyt_date.Add(wx.StaticText(parent, label=GT(u'Year')), (0, 1))
        lyt_date.Add(wx.StaticText(parent, label=GT(u'Month')), (0, 2))
        lyt_date.Add(wx.StaticText(parent, label=GT(u'Day')), (0, 3))
        lyt_date.Add(spin_year, (1, 1), flag=wx.LEFT, border=5)
        lyt_date.Add(spin_month, (1, 2))
        lyt_date.Add(spin_day, (1, 3))
        
        lyt_uknwn1 = BoxSizer(wx.HORIZONTAL)
        lyt_uknwn1.Add(txt_unknown1, 0, wx.ALIGN_CENTER_VERTICAL)
        lyt_uknwn1.Add(ti_unknown1, 0, wx.LEFT, 5)
        
        lyt_uknwn2 = BoxSizer(wx.HORIZONTAL)
        lyt_uknwn2.Add(txt_unknown2, 0, wx.ALIGN_CENTER_VERTICAL)
        lyt_uknwn2.Add(ti_unknown2, 0, wx.LEFT, 5)
        
        self.lyt_main = BoxSizer(wx.VERTICAL)
        self.lyt_main.Add(lyt_date, 0, wx.TOP, 5)
        self.lyt_main.Add(lyt_uknwn1, 0, wx.TOP, 5)
        self.lyt_main.Add(lyt_uknwn2, 0, wx.TOP, 5)


## TODO: Doxygen
class ManSectName(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        self._add_field(GT(u'Program'), wx.TextCtrl(parent))
        self._add_field(GT(u'Description'), wx.TextCtrl(parent))


## TODO: Doxygen
class ManSectSynopsis(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        self._add_field(GT(u'Synopsis'), TextAreaPanel(parent), expand=True)


## Generic manpage section
class ManSection(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        self.sections = (
            GT(u'Name'),
            GT(u'Synopsis'),
            GT(u'Configuration'),
            GT(u'Description'),
            GT(u'Options'),
            GT(u'Exit status'),
            GT(u'Return value'),
            GT(u'Errors'),
            GT(u'Environment'),
            GT(u'Files'),
            GT(u'Versions'),
            GT(u'Conforming to'),
            GT(u'Notes'),
            GT(u'Bugs'),
            GT(u'Example'),
            )
        
        self.sect_name = None
        # FIXME: Replace with checkbox
        self.btn_remove = None
        
        # *** Layout *** #
        
        self.lyt_main = wx.GridBagSizer()
    
    
    ## Retrieve the remove button
    def GetButton(self):
        return self.btn_remove
    
    
    ## Retrieve the main sizer object
    #  
    #  \override dbr.mansect.ManBase.GetObject
    def GetObject(self, section_name=None, multiline=False, static=False, expand=False,
                removable=False):
        if static:
            try:
                self.sect_name = wx.StaticText(self.Parent, label=section_name)
            
            except TypeError:
                err_l1 = GT(u'Could not remove section')
                err_l2 = GT(u'Please report this problem to the developers')
                ShowErrorDialog(u'{}\n\n{}'.format(err_l1, err_l2), traceback.format_exc())
                
                return None
        
        else:
            self.sect_name = wx.Choice(self.Parent, choices=self.sections)
        
        if multiline:
            value = TextAreaPanel(self.Parent)
            FLAG_VALUE = wx.EXPAND|wx.LEFT
            FLAG_LABEL = wx.ALIGN_TOP
        
        else:
            value = TextArea(self.Parent)
            FLAG_VALUE = wx.ALIGN_CENTER_VERTICAL|wx.LEFT
            FLAG_LABEL = wx.ALIGN_CENTER_VERTICAL
        
        self.lyt_main.Add(self.sect_name, (0, 0), flag=FLAG_LABEL)
        self.lyt_main.Add(value, (0, 1), flag=FLAG_VALUE, border=5)
        
        if expand:
            self.lyt_main.AddGrowableCol(1)
        
        if removable:
            self.btn_remove = ButtonRemove(self.Parent)
            
            self.lyt_main.Add(self.btn_remove, (0, 2), flag=wx.RIGHT, border=5)
        
        return ManBase.GetObject(self)
    
    
    ## TODO: Doxygen
    def SetSectionName(self, section_name):
        if isinstance(self.sect_name, (ComboBox, wx.TextCtrl,)):
            self.sect_name.SetValue(section_name)
            
            return True
        
        elif isinstance(self.sect_name, wx.StaticText):
            self.sect_name.SetLabel(section_name)
            
            return True
        
        Logger.Warning(__name__, u'Could not set section name: {}'.format(section_name))
        
        return False
