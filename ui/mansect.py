# -*- coding: utf-8 -*-

## \package ui.mansect

# MIT licensing
# See: docs/LICENSE.txt


import traceback, wx

from dbr.language       import GT
from dbr.log            import Logger
from globals.dateinfo   import GetDayInt
from globals.dateinfo   import GetMonthInt
from globals.dateinfo   import GetYear
from globals.ident      import manid
from ui.button          import ButtonRemove
from ui.dialog          import ShowErrorDialog
from ui.layout          import BoxSizer
from ui.panel           import BorderedPanel
from ui.selectinput     import ComboBox
from ui.textinput       import TextArea
from ui.textinput       import TextAreaPanel


DEFAULT_MANSECT_STYLE = manid.REMOVABLE


## Base class for manpage parts
#  
#  \param label
#    Only used if style is STATIC
class ManSectBase:
    def __init__(self, parent, label=None, style=DEFAULT_MANSECT_STYLE):
        self.Parent = parent
        self.Style = style
        
        if self.HasStyle((manid.CHOICE & manid.MUTABLE)):
            # FIXME: Raise exception
            Logger.Error(__name__, u'Cannot use CHOICE and MUTABLE styles together')
            return
        
        # Allow adding multiple instances of object
        self.Multiple = True
        
        self.Panel = BorderedPanel(parent)
        
        if self.HasStyle(manid.CHOICE):
            self.Label = wx.Choice(self.Panel)
        
        elif self.HasStyle(manid.MUTABLE):
            self.Label = ComboBox(self.Panel)
        
        else:
            self.Label = wx.StaticText(self.Panel)
            
            if label:
                self.Label.SetLabel(label)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.HORIZONTAL)
        lyt_main.Add(self.Label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        
        if style & manid.REMOVABLE:
            lyt_main.Add(ButtonRemove(self.Panel))
        
        self.Panel.SetSizer(lyt_main)
    
    
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
    
    
    ## Retrieves the section label or StaticText instance
    #  
    #  \param string
    #    If \b \e True, retrieves string value, otherwise retrieves StaticText instance
    #  \return
    #    \b \e String or \b \e wx.StaticText instance
    def GetLabel(self, string=True):
        if string:
            label = self.Label.GetLabel()
            
            # DEBUG: Line
            print(u'\nDEBUG: ui.mansect.SingleLineSect.GetLabel: Label type: {}'.format(type(label)))
            
            return label
        
        return self.Label
    
    
    ## TODO: Doxygen
    def GetLabelObject(self):
        return self.GetLabel(False)
    
    
    ## Retrieve the main object
    def GetObject(self):
        return self.Panel
    
    
    ## Retrieve RemoveButton instance
    def GetButton(self):
        for FIELD in self.Panel.GetChildren():
            if isinstance(FIELD, ButtonRemove):
                return FIELD
    
    
    ## Retrieve the object's sizer instance
    def GetSizer(self):
        return self.Panel.GetSizer()
    
    
    ## Retrieve styling used by instance
    def GetStyle(self):
        return self.Style
    
    
    ## Check if instance is using style
    def HasStyle(self, style):
        return self.Style & style
    
    
    ## Checks multiple instances can be uses
    def MultipleAllowed(self):
        return self.Multiple
    
    
    ## Sets the section label
    #  
    #  \param label
    #    \b \e String value or wx.StaticText instance for new label
    def SetLabel(self, label):
        if isinstance(label, wx.StaticText):
            label = label.GetLabel()
        
        self.Label.SetLabel(label)


## TODO: Doxygen
class ManSect(ManSectBase):
    def __init__(self, parent, label=None, style=DEFAULT_MANSECT_STYLE):
        ManSectBase.__init__(self, parent, label, style)
        
        FLAGS = 0
        
        if self.HasStyle(manid.MULTILINE):
            self.Input = TextAreaPanel(self.Panel)
            FLAGS = wx.EXPAND|FLAGS
        
        else:
            self.Input = TextArea(self.Panel)
            FLAGS = wx.ALIGN_CENTER_VERTICAL|FLAGS
        
        lyt_input = wx.BoxSizer(wx.HORIZONTAL)
        lyt_input.Add(self.Input, 0, FLAGS)
        
        lyt_main = self.GetSizer()
        lyt_main.Insert(1, lyt_input, 0, FLAGS)


## TODO: Doxygen
#  
#  This section is required
#  FIXME: Should derive from wx.Panel/BorderedPanel???
class ManBanner(ManSectBase):
    def __init__(self, parent):
        ManSectBase.__init__(self, parent)
        
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
class ManSectName(ManSectBase):
    def __init__(self, parent):
        ManSectBase.__init__(self, parent)
        
        self._add_field(GT(u'Program'), wx.TextCtrl(parent))
        self._add_field(GT(u'Description'), wx.TextCtrl(parent))


## TODO: Doxygen
class ManSectSynopsis(ManSectBase):
    def __init__(self, parent):
        ManSectBase.__init__(self, parent)
        
        self._add_field(GT(u'Synopsis'), TextAreaPanel(parent), expand=True)


## Generic manpage section
class ManSection(ManSectBase):
    def __init__(self, parent):
        ManSectBase.__init__(self, parent)
        
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
    #  \override ui.mansect.ManSectBase.GetObject
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
        
        return ManSectBase.GetObject(self)
    
    
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
