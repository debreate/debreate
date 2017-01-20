# -*- coding: utf-8 -*-

## \package ui.prompt

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.buttons        import ReplaceStandardButtons
from globals.strings    import TextIsEmpty


## Custom TextEntryDialog that defines Clear method
class TextEntryDialog(wx.TextEntryDialog):
    def __init__(self, parent, message, caption=u'Please enter text', defaultValue=u'',
            pos=wx.DefaultPosition, style=wx.OK|wx.CANCEL|wx.CENTER):
        wx.TextEntryDialog.__init__(self, parent, message, caption, defaultValue, style, pos)
        
        ReplaceStandardButtons(self)
        
        self.stored_value = wx.EmptyString
        self.stored_insertion = 0
        
        # *** Event Handling *** #
        
        bound_id = None
        for FIELD in self.GetChildren():
            field_id = FIELD.GetId()
            if isinstance(FIELD, wx.Button) and field_id == wx.ID_OK:
                FIELD.Bind(wx.EVT_BUTTON, self.OnConfirm)
                
                bound_id = field_id
        
        if not bound_id:
            # FIXME: Can't use Logger in this module
            print(u'WARNING: [{}] Confirm button was not bound to button event, insertion point will not be updated'.format(__name__))
        
        elif bound_id != wx.ID_OK:
            # FIXME: Can't use Logger in this module
            print(u'WARNING: [{}] Button event was bound to button with non-ID ID_OK: {}'.format(__name__, bound_id))
    
    
    ## Clear the text input
    #  
    #  \return
    #    \b \e True if text input is empty
    def Clear(self):
        self.SetValue(wx.EmptyString)
        
        return TextIsEmpty(self.Value)
    
    
    ## Ends a modal dialog, passing a value to be returned from the wxDialog::ShowModal invocation
    #  
    #  \override wx.TextEntryDialog.EndModal
    def EndModal(self, retCode):
        self.StoreValue()
        self.StoreInsertionPoint()
        
        return wx.TextEntryDialog.EndModal(self, retCode)
    
    
    ## Retrieves insertion point of the TextCtrl instance
    #  
    #  \return
    #    Index of insertion point
    def GetInsertionPoint(self):
        text_ctrl = self.GetTextCtrl()
        if text_ctrl:
            return text_ctrl.GetInsertionPoint()
    
    
    ## Retrieve dialog's TextCtrl instance
    def GetTextCtrl(self):
        for FIELD in self.GetChildren():
            if isinstance(FIELD, wx.TextCtrl):
                return FIELD
    
    
    ## Retrieves value from TextCtrl instance
    def GetValue(self):
        text_ctrl = self.GetTextCtrl()
        if text_ctrl:
            return self.GetTextCtrl().GetValue()
    
    
    ## Extra actions to take when pressing 'OK/Confirm' button
    #  
    #  - Stores insertion point for updating when dialog is shown again
    #  FIXME: Event not propagating from inherited class
    def OnConfirm(self, event=None):
        self.stored_insertion = self.GetInsertionPoint()
        
        if event:
            event_object = event.GetEventObject()
            
            if isinstance(event_object, wx.Button):
                event_id = event_object.GetId()
            
            else:
                event_id = event.GetId()
        
        else:
            event_id = wx.ID_OK
        
        self.EndModal(event_id)
    
    
    ## Sets TextCtrl instance's insertion point from stored value
    def RestoreInsertionPoint(self):
        # DEBUG: Start
        print(u'\nTextEntryDialog.RestoreInsertionPoint:')
        print(u'  Restoring insertion point: {}'.format(self.stored_insertion))
        # DEBUG: End
        
        self.SetInsertionPoint(self.stored_insertion)
        
        # Reset to default
        self.stored_insertion = 0
    
    
    ## Sets TextCtrl instance's value from stored value
    def RestoreValue(self):
        # DEBUG: Start
        print(u'\nTextEntryDialog.RestoreValue:')
        print(u'  Restoring value: {}'.format(self.stored_value))
        # DEBUG: End
        
        self.SetValue(self.stored_value)
        
        # Reset to default
        self.stored_value = wx.EmptyString
    
    
    ## Set insertion point of TextCtrl instance
    #  
    #  FIXME: Not working
    #  \param point
    #    Index at with to set carat
    def SetInsertionPoint(self, pos):
        # DEBUG: Line
        print(u'\nTextEntryDialog.SetInsertionPoint:')
        
        text_ctrl = self.GetTextCtrl()
        
        # DEBUG: Start
        print(u'  TextCtrl instance: {}'.format(type(text_ctrl)))
        print(u'  Insertion point before: {}'.format(text_ctrl.GetInsertionPoint()))
        # DEBUG: End
        
        if text_ctrl:
            text_ctrl.SetInsertionPoint(pos)
            
            # DEBUG: Line
            print(u'  Insertion point after:  {}'.format(text_ctrl.GetInsertionPoint()))
            
            return True
        
        # DEBUG: Line
        print(u'  Error: TextCtrl instance is None type')
        
        return False
    
    
    ## Set insertion point of TextContrl to end
    def SetInsertionPointEnd(self):
        text_ctrl = self.GetTextCtrl()
        if text_ctrl:
            text_ctrl.SetInsertionPointEnd()
            
            return True
        
        return False
    
    
    ## Show modal dialog
    #  
    #  Differences from inherited method:
    #  - Replaces insertion point & sets focus back on text area
    #  \override wx.TextEntryDialog.ShowModal
    def ShowModal(self):
        if self.stored_value:
            self.RestoreValue()
            self.RestoreInsertionPoint()
        
        # Put focus back on text control
        self.SetFocus()
        
        return wx.TextEntryDialog.ShowModal(self)
    
    
    ## Stores TextCtrl instance's insertion point
    def StoreInsertionPoint(self):
        self.stored_insertion = self.GetInsertionPoint()
    
    
    ## Stores TextCtrl instance's value
    def StoreValue(self):
        self.stored_value = self.GetValue()
