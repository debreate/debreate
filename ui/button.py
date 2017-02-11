# -*- coding: utf-8 -*-

## \package ui.buttons
#  
#  Custom buttons for application

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.containers     import Contains
from dbr.image          import GetBitmap
from dbr.language       import GT
from dbr.log            import Logger
from fields.cmdfield    import CommandField
from globals            import ident
from globals.ident      import btnid
from globals.ident      import genid
from globals.paths      import ConcatPaths
from globals.paths      import PATH_bitmaps
from globals.strings    import GS
from globals.strings    import IsString
from ui.layout          import BoxSizer
from ui.style           import layout as lyt


## Standard button that inherits CommandField
class Button(wx.Button, CommandField):
    def __init__(self, parent, btnId=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=0, name=wx.ButtonNameStr, commands=None, requireAll=False):
        
        wx.Button.__init__(self, parent, btnId, label, pos, size, style, name=name)
        CommandField.__init__(self, commands, requireAll)


## The same as wx.BitmapButton but defaults to style=wx.NO_BORDER
class CustomButton(wx.BitmapButton, CommandField):
    def __init__(self, parent, bitmap, btnId=wx.ID_ANY, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
            name=wx.ButtonNameStr, commands=None, requireAll=False):
        
        if not isinstance(bitmap, wx.Bitmap):
            bitmap = wx.Bitmap(bitmap)
        
        wx.BitmapButton.__init__(self, parent, btnId, bitmap, pos, size, style|wx.NO_BORDER,
                validator, name)
        CommandField.__init__(self, commands, requireAll)


## TODO: Doxygen
class ButtonAdd(CustomButton):
    def __init__(self, parent, btnId=wx.ID_ADD, name=u'btn add'):
        CustomButton.__init__(self, parent, GetBitmap(u'add', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Add')))


## TODO: Doxygen
class ButtonAppend(CustomButton):
    def __init__(self, parent, btnId=genid.APPEND, name=u'btn append'):
        CustomButton.__init__(self, parent, GetBitmap(u'append', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Append')))


## TODO: Doxygen
class ButtonBrowse(CustomButton):
    def __init__(self, parent, btnId=genid.BROWSE, name=u'btn browse'):
        CustomButton.__init__(self, parent, GetBitmap(u'browse', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))


## TODO: Doxygen
class ButtonBrowse64(CustomButton):
    def __init__(self, parent, btnId=genid.BROWSE, name=u'btn browse'):
        
        CustomButton.__init__(self, parent, GetBitmap(u'browse', 64, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Browse')))


## TODO: Doxygen
class ButtonBuild(CustomButton):
    def __init__(self, parent, btnId=genid.BUILD, name=u'btn build'):
        CustomButton.__init__(self, parent, GetBitmap(u'build', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Build')))


## TODO: Doxygen
class ButtonBuild64(CustomButton):
    def __init__(self, parent, btnId=genid.BUILD, name=u'btn build'):
        CustomButton.__init__(self, parent, GetBitmap(u'build', 64, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Build')))


## TODO: Doxygen
class ButtonCancel(CustomButton):
    def __init__(self, parent, btnId=wx.ID_CANCEL, name=u'btn cancel'):
        CustomButton.__init__(self, parent, GetBitmap(u'cancel', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Cancel')))


## TODO: Doxygen
class ButtonClear(CustomButton):
    def __init__(self, parent, btnId=wx.ID_CLEAR, name=u'btn clear'):
        CustomButton.__init__(self, parent, GetBitmap(u'clear', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Clear')))


## TODO: Doxygen
class ButtonConfirm(CustomButton):
    def __init__(self, parent, btnId=wx.ID_OK, name=u'btn confirm'):
        CustomButton.__init__(self, parent, GetBitmap(u'confirm', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Confirm')))


## TODO: Doxygen
class ButtonHelp(CustomButton):
    def __init__(self, parent, btnId=wx.ID_HELP, name=u'btn help'):
        CustomButton.__init__(self, parent, GetBitmap(u'help', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTipString(GT(u'Help'))


## TODO: Doxygen
class ButtonHelp64(CustomButton):
    def __init__(self, parent, btnId=wx.ID_HELP, name=u'btn help'):
        CustomButton.__init__(self, parent, GetBitmap(u'help', 64, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTipString(GT(u'Help'))


## Button with an arrow for importing info from other pages
class ButtonImport(CustomButton):
    def __init__(self, parent, btnId=genid.IMPORT, name=u'btn import'):
        CustomButton.__init__(self, parent, GetBitmap(u'import', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Import')))


## TODO: Doxygen
class ButtonNext(CustomButton):
    def __init__(self, parent, btnId=ident.NEXT, name=u'btn next'):
        CustomButton.__init__(self, parent, GetBitmap(u'next', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Next')))


## TODO: Doxygen
class ButtonPrev(CustomButton):
    def __init__(self, parent, btnId=ident.PREV, name=u'btn previous'):
        CustomButton.__init__(self, parent, GetBitmap(u'prev', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Previous')))


## TODO: Doxygen
class ButtonPreview(CustomButton):
    def __init__(self, parent, btnId=wx.ID_PREVIEW, name=u'btn preview'):
        CustomButton.__init__(self, parent, GetBitmap(u'preview', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))


## TODO: Doxygen
class ButtonPreview64(CustomButton):
    def __init__(self, parent, btnId=wx.ID_PREVIEW, name=u'btn preview'):
        CustomButton.__init__(self, parent, GetBitmap(u'preview', 64, u'button'),
                btnId=btnId, name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Preview')))


## Button for refreshing displayed controls
class ButtonRefresh(CustomButton):
    def __init__(self, parent, btnId=wx.ID_REFRESH, name=u'btn refresh'):
        CustomButton.__init__(self, parent, GetBitmap(u'refresh', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Refresh')))


## TODO: Doxygen
class ButtonRemove(CustomButton):
    def __init__(self, parent, btnId=wx.ID_REMOVE, name=u'btn remove'):
        CustomButton.__init__(self, parent, GetBitmap(u'remove', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Remove')))


## TODO: Doxygen
class ButtonSave(CustomButton):
    def __init__(self, parent, btnId=wx.ID_SAVE, name=u'btn save'):
        CustomButton.__init__(self, parent, GetBitmap(u'save', 32, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Save')))


## TODO: Doxygen
class ButtonSave64(CustomButton):
    def __init__(self, parent, btnId=wx.ID_SAVE, name=u'btn save'):
        CustomButton.__init__(self, parent, GetBitmap(u'save', 64, u'button'), btnId=btnId,
                name=name)
        
        self.SetToolTip(wx.ToolTip(GT(u'Save')))


## TODO: Doxygen
class LayoutButton(BoxSizer):
    def __init__(self, button, label, parent=None, btnId=wx.ID_ANY, size=32,
            tooltip=None, name=None, showLabel=True):
        
        BoxSizer.__init__(self, wx.VERTICAL)
        
        if IsString(button):
            self.Button = CreateButton(parent, label, button, size, btnId, tooltip, name)
        
        else:
            self.Button = button
        
        self.Add(self.Button, 1, wx.ALIGN_CENTER)
        
        if isinstance(self.Button, CustomButton):
            if not label:
                label = self.Button.Name
            
            self.Label = wx.StaticText(self.Button.GetParent(), label=label)
            
            self.Add(self.Label, 0, wx.ALIGN_CENTER)
            
            self.Show(self.Label, showLabel)
    
    
    ## TODO: Doxygen
    def Bind(self, eventType, eventHandler):
        self.Button.Bind(eventType, eventHandler)
    
    
    ## TODO: Doxygen
    def GetLabel(self):
        if isinstance(self.Button, CustomButton):
            return self.Label.GetLabel()
        
        return self.Button.GetLabel()
    
    
    ## TODO: Doxygen
    def LabelIsShown(self):
        if not isinstance(self.Button, CustomButton):
            # Instance is a wx.Button
            return True
        
        return self.IsShown(self.Label)
    
    
    ## TODO: Doxygen
    def ShowLabel(self, show=True):
        self.Show(self.Label, show)


## BoxSizer class to distinguish between other sizers
class ButtonSizer(BoxSizer):
    def __init__(self, orient):
        BoxSizer.__init__(self, orient)
    
    
    ## TODO: Doxygen
    def Add(self, button, proportion=0, flag=0, border=0, label=None, userData=None):
        # FIXME: Create method to call from Add & Insert methods & reduce code
        if isinstance(button, LayoutButton):
            add_object = button
        
        else:
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
    
    
    ## Changes label for all buttons with specified ID
    #
    #  \param btnId
    #    \b \e Integer ID of buttons to change labels
    #  \param newLabel
    #    New \b \e string label for button
    #  \return
    #    \b \e True if matching button found
    def SetLabel(self, btnId, newLabel):
        label_set = False
        
        for SI in self.GetChildren():
            btn_objects = SI.GetSizer()
            if btn_objects:
                btn_objects = btn_objects.GetChildren()
                
                button = btn_objects[0].GetWindow()
                
                if button and button.GetId() == btnId:
                    if isinstance(button, CustomButton):
                        static_text = btn_objects[1].GetWindow()
                        static_text.SetLabel(newLabel)
                        button.SetToolTipString(newLabel)
                        
                        label_set = True
                    
                    else:
                        button.SetLabel(newLabel)
                        button.SetToolTipString(newLabel)
                        
                        label_set = True
        
        return label_set
    
    
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
#    \b \e ui.button.ButtonSizer instance containing the buttons
def AddCustomButtons(window, button_ids, parent_sizer=None, show_labels=True, reverse=True,
            flag=wx.ALIGN_RIGHT|lyt.PAD_RB, border=5):
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
    
    if isinstance(parent_sizer, wx.BoxSizer):
        parent_sizer.Add(lyt_buttons, 0, flag, border)
        
        return None
    
    # parent_sizer is boolean
    elif parent_sizer:
        window.GetSizer().Add(lyt_buttons, 0, flag, border)
        
        return None
    
    return lyt_buttons


## Find sizer instance that contains buttons
#  
#  Helper function for ReplaceStandardButtons
#
#  \param sizer
#    \b \e wx.Sizer or \b \e wx.Window instance to search for child button sizer
def GetButtonSizer(sizer):
    if isinstance(sizer, wx.Window):
        sizer = sizer.GetSizer()
    
    if isinstance(sizer, (ButtonSizer, wx.StdDialogButtonSizer)):
        return sizer
    
    for S in sizer.GetChildren():
        S = S.GetSizer()
        
        if S:
            S = GetButtonSizer(S)
            
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
    if isinstance(dialog, (wx.FileDialog, wx.MessageDialog)):
        Logger.Warn(__name__, u'FIXME: Cannot replace buttons on object type: {}'.format(type(dialog)))
        
        return
    
    lyt_buttons = GetButtonSizer(dialog.GetSizer())
    
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


## Creates a new custom button
#
#  \param parent
#    \b \e wx.Window parent instance
#  \param label
#    Text to be shown on button or tooltip
#  \param btnId
#    <b><i>Integer identifier
#  \param image
#    Base name of image file to use for custom buttons (uses standard image if set to 'None')
#  \param size
#    Image size to use for button
#  \param tooltip
#    Text to display when cursor hovers over button
#  \param name
#    Name attribute
#  \return
#    ui.button.CustomButton instance or wx.Button instance if image file not found
def CreateButton(parent, label, btnId=wx.ID_ANY, image=None, size=32, tooltip=None, name=None,
            commands=None, requireAll=False):
    if not name:
        name = label
    
    if not image:
        image = btnid.GetImage(btnId)
    
    image = ConcatPaths((PATH_bitmaps, u'button', GS(size), u'{}.png'.format(image)))
    
    button = None
    
    if image:
        if not os.path.isfile(image):
            Logger.Warn(
                    __name__,
                    u'CreateButton: Attempted to set not-existent image for button (ID {}):'.format(btnId),
                    details=image
                    )
        
        else:
            button = CustomButton(parent, image, btnId, name=name, commands=commands,
                    requireAll=requireAll)
    
    # Use a standard button
    if not button:
        button = Button(parent, btnId, label, name=name, commands=commands,
                requireAll=requireAll)
    
    if not tooltip:
        tooltip = label
    
    button.SetToolTipString(tooltip)
    
    return button
