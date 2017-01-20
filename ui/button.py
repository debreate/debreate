# -*- coding: utf-8 -*-

## \package ui.buttons
#  
#  Custom buttons for application

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.containers     import Contains
from dbr.language       import GT
from globals            import ident
from globals.bitmaps    import BUTTON_HELP
from globals.bitmaps    import BUTTON_REFRESH
from globals.paths      import PATH_app
from ui.layout          import BoxSizer


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


## BoxSizer class to distinguish between other sizers
class ButtonSizer(BoxSizer):
    def __init__(self, orient):
        BoxSizer.__init__(self, orient)
    
    
    ## TODO: Doxygen
    def Add(self, button, proportion=0, flag=0, border=0, label=None, userData=None):
        # FIXME: Create method to call from Add & Insert methods & reduce code
        if isinstance(button, CustomButton):
            if label == None:
                label = button.GetToolTipString()
            
            add_object = BoxSizer(wx.VERTICAL)
            add_object.Add(button, 0, wx.ALIGN_CENTER)
            add_object.Add(wx.StaticText(button.Parent, label=label), 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        else:
            add_object = button
        
        return BoxSizer.Add(self, add_object, proportion, flag, border, userData)
    
    
    ## TODO: Doxygen
    def HideLabels(self):
        self.ShowLabels(False)
    
    
    ## TODO: Doxygen
    def Insert(self, index, button, proportion=0, flag=0, border=0, label=None, userData=None):
        if isinstance(button, CustomButton):
            if label == None:
                label = button.GetToolTipString()
            
            add_object = BoxSizer(wx.VERTICAL)
            add_object.Add(button, 0, wx.ALIGN_CENTER)
            add_object.Add(wx.StaticText(button.Parent, label=label), 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        else:
            add_object = button
        
        return BoxSizer.Insert(self, index, add_object, proportion, flag, border, userData)
    
    
    ## Show or hide text labels
    def ShowLabels(self, show=True):
        buttons = self.GetChildren()
        
        if buttons:
            for SIZER in self.GetChildren():
                SIZER = SIZER.GetSizer()
                
                if SIZER:
                    label = SIZER.GetChildren()[1]
                    label.Show(show)
            
            window = self.GetContainingWindow()
            if window:
                window.Layout()


button_list = {
    wx.ID_CANCEL: ButtonCancel,
    wx.ID_OK: ButtonConfirm,
    wx.ID_HELP: ButtonHelp,
    wx.ID_SAVE: ButtonSave,
    }


## TODO: Doxygen
#  
#  \param button_ids
#    \b \e List of IDs of buttons to be added
#  \param parent_sizer
#    The \b \e wx.Sizer instance that the buttons sizer should be added to
#  \param show_labels:
#    If True, button labels will be shown on custom button instances
#  \param reverse
#    Reverse order of buttons added
#  \return
#    \b \e BoxSizer instance containing the buttons
def AddCustomButtons(window, button_ids, parent_sizer=None, show_labels=True, reverse=True):
    lyt_buttons = ButtonSizer(wx.HORIZONTAL)
    
    if reverse:
        button_ids = reversed(button_ids)
    
    for ID in button_ids:
        if ID in button_list:
            new_button = button_list[ID](window)
            lyt_buttons.Add(new_button, 1)
            
            continue
        
        # Use a standard button if custom button not available
        new_button = wx.Button(window, ID)
        lyt_buttons.Add(new_button, 0, wx.ALIGN_CENTER)
    
    lyt_buttons.ShowLabels(show_labels)
    
    if parent_sizer:
        parent_sizer.Add(lyt_buttons)
        
        return None
    
    return lyt_buttons


## Find sizer instance that contains buttons
#  
#  Helper function for ReplaceStandardButtons
def _get_button_sizer(sizer):
    if isinstance(sizer, (ButtonSizer, wx.StdDialogButtonSizer)):
        return sizer
    
    for S in sizer.GetChildren():
        S = S.GetSizer()
        
        if S:
            S = _get_button_sizer(S)
            
            if S:
                return S


def _get_containing_sizer(parent, sizer):
    if isinstance(parent, wx.Window):
        parent = parent.GetSizer()
    
    if not parent or parent == sizer:
        return None
    
    if Contains(parent, sizer):
        return parent
    
    for S in parent.GetChildren():
        S = S.GetSizer()
        
        if S:
            S = _get_containing_sizer(S, sizer)
            
            if S:
                return S


## Replaces standard dialog buttons with custom ones
#  
#  \param dialog
#    Dialog instance containing the buttons
def ReplaceStandardButtons(dialog):
    if isinstance(dialog, wx.MessageDialog):
        print(u'ERROR: [{}] FIXME: Cannot replace buttons on wx.MessageDialog'.format(__name__))
        return
    
    lyt_buttons = _get_button_sizer(dialog.GetSizer())
    
    removed_button_ids = []
    
    if lyt_buttons:
        for FIELD in lyt_buttons.GetChildren():
            FIELD = FIELD.GetWindow()
            
            if isinstance(FIELD, wx.Button):
                lyt_buttons.Detach(FIELD)
                removed_button_ids.append(FIELD.GetId())
                FIELD.Destroy()
    
    # Replace sizer with ButtonSizer
    if not isinstance(lyt_buttons, ButtonSizer):
        container_sizer = _get_containing_sizer(dialog, lyt_buttons)
        
        index = 0
        for S in container_sizer.GetChildren():
            S = S.GetSizer()
            
            if S and S == lyt_buttons:
                break
            
            index += 1
        
        container_sizer.Remove(lyt_buttons)
        lyt_buttons = ButtonSizer(wx.HORIZONTAL)
        container_sizer.Insert(index, lyt_buttons, 0, wx.ALIGN_RIGHT)
    
    # Don't add padding to first item
    FLAGS = 0
    
    for ID in removed_button_ids:
        if ID in button_list:
            lyt_buttons.Add(button_list[ID](dialog), 0, FLAGS, 5)
        
        else:
            # Failsafe to add regular wx.Button
            lyt_buttons.Add(wx.Button(dialog, ID), 0, FLAGS, 5)
        
        if not FLAGS:
            FLAGS = wx.LEFT
    
    dialog.Fit()
    dialog.Layout()
