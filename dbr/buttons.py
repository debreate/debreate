# -*- coding: utf-8 -*-

## \package dbr.buttons
#  
#  Custom buttons for application

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from globals            import ident
from globals.bitmaps    import BUTTON_HELP
from globals.bitmaps    import BUTTON_REFRESH
from globals.paths      import PATH_app


## The same as wx.BitmapButton but defaults to style=wx.NO_BORDER
class CustomButton(wx.BitmapButton):
    def __init__(self, parent, bitmap, ID=wx.ID_ANY, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
            name=wx.ButtonNameStr):
        
        if not isinstance(bitmap, wx.Bitmap):
            bitmap = wx.Bitmap(bitmap)
        
        wx.BitmapButton.__init__(self, parent, ID, bitmap, pos, size, style|wx.NO_BORDER,
                validator, name)


## TODO: Doxygen
class ButtonAdd(CustomButton):
    def __init__(self, parent, ID=wx.ID_ADD, name=u'btn add'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/add32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Add')))


## TODO: Doxygen
class ButtonAppend(CustomButton):
    def __init__(self, parent, ID=ident.APPEND, name=u'btn append'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/pipe32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Append')))


## TODO: Doxygen
class ButtonBrowse(CustomButton):
    def __init__(self, parent, ID=ident.BROWSE, name=u'btn browse'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/browse32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))


## TODO: Doxygen
class ButtonBrowse64(CustomButton):
    def __init__(self, parent, ID=ident.BROWSE, name=u'btn browse'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/browse64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))


## TODO: Doxygen
class ButtonBuild(CustomButton):
    def __init__(self, parent, ID=ident.BUILD, name=u'btn build'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/build32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Build')))


## TODO: Doxygen
class ButtonBuild64(CustomButton):
    def __init__(self, parent, ID=ident.BUILD, name=u'btn build'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/build64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Build')))


## TODO: Doxygen
class ButtonCancel(CustomButton):
    def __init__(self, parent, ID=wx.ID_CANCEL, name=u'btn cancel'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/cancel32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Cancel')))


## TODO: Doxygen
class ButtonClear(CustomButton):
    def __init__(self, parent, ID=wx.ID_CLEAR, name=u'btn clear'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/clear32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Clear')))


## TODO: Doxygen
class ButtonConfirm(CustomButton):
    def __init__(self, parent, ID=wx.ID_OK, name=u'btn confirm'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/confirm32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Confirm')))


## TODO: Doxygen
class ButtonHelp(CustomButton):
    def __init__(self, parent, ID=wx.ID_HELP, name=u'btn help'):
        CustomButton.__init__(self, parent, BUTTON_HELP, ID=ID, name=name)
        
        self.SetToolTipString(GT(u'Help'))


## TODO: Doxygen
class ButtonHelp64(CustomButton):
    def __init__(self, parent, ID=wx.ID_HELP, name=u'btn help'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/question64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTipString(GT(u'Help'))


## Button with an arrow for importing info from other pages
class ButtonImport(CustomButton):
    def __init__(self, parent, ID=ident.IMPORT, name=u'btn import'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/import32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Import')))


## TODO: Doxygen
class ButtonNext(CustomButton):
    def __init__(self, parent, ID=ident.NEXT, name=u'btn next'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/next32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Next')))


## TODO: Doxygen
class ButtonPrev(CustomButton):
    def __init__(self, parent, ID=ident.PREV, name=u'btn previous'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/prev32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Previous')))


## TODO: Doxygen
class ButtonPreview(CustomButton):
    def __init__(self, parent, ID=wx.ID_PREVIEW, name=u'btn preview'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/preview32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))


## TODO: Doxygen
class ButtonPreview64(CustomButton):
    def __init__(self, parent, ID=wx.ID_PREVIEW, name=u'btn preview'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/preview64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))


## Button for refreshing displayed controls
class ButtonRefresh(CustomButton):
    def __init__(self, parent, ID=wx.ID_REFRESH, name=u'btn refresh'):
        CustomButton.__init__(self, parent, BUTTON_REFRESH,
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Refresh')))


## TODO: Doxygen
class ButtonRemove(CustomButton):
    def __init__(self, parent, ID=wx.ID_REMOVE, name=u'btn remove'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/del32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Remove')))


## TODO: Doxygen
class ButtonSave(CustomButton):
    def __init__(self, parent, ID=wx.ID_SAVE, name=u'btn save'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/save32.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Save')))


## TODO: Doxygen
class ButtonSave64(CustomButton):
    def __init__(self, parent, ID=wx.ID_SAVE, name=u'btn save'):
        CustomButton.__init__(self, parent, wx.Bitmap(u'{}/bitmaps/save64.png'.format(PATH_app)),
                ID=ID, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Save')))


## Find sizer instance that contains buttons
#  
#  Helper function for ReplaceStandardButtons
def _get_button_sizer(sizer):
    if isinstance(sizer, wx.StdDialogButtonSizer):
        return sizer
    
    for S in sizer.GetChildren():
        S = S.GetSizer()
        
        if S:
            S = _get_button_sizer(S)
            
            if isinstance(S, wx.StdDialogButtonSizer):
                return S


## Replaces standard dialog buttons with custom ones
#  
#  \param dialog
#    Dialog instance containing the buttons
def ReplaceStandardButtons(dialog):
    lyt_buttons = _get_button_sizer(dialog.GetSizer())
    
    removed_button_ids = []
    insert_index = 0
    found_button = False
    
    if lyt_buttons:
        for FIELD in lyt_buttons.GetChildren():
            FIELD = FIELD.GetWindow()
            
            if isinstance(FIELD, wx.Button):
                lyt_buttons.Detach(FIELD)
                removed_button_ids.append(FIELD.GetId())
                FIELD.Destroy()
                
                found_button = True
            
            if not found_button:
                insert_index += 1
    
    for ID in reversed(removed_button_ids):
        if ID == wx.ID_OK:
            lyt_buttons.Insert(insert_index, ButtonConfirm(dialog))
            continue
        
        if ID == wx.ID_CANCEL:
            lyt_buttons.Insert(insert_index, ButtonCancel(dialog))
            continue
        
        lyt_buttons.Insert(insert_index, wx.Button(dialog, ID))
    
    dialog.Fit()
    dialog.Layout()
