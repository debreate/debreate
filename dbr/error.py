# -*- coding: utf-8 -*-

## \package dbr.error


import wx

from dbr.language   import GT
from dbr.log        import Logger


def ShowError(window, message, error_id=None):
    error_dialog = wx.MessageDialog(window, message, GT(u'Error'),
            style=wx.OK|wx.ICON_ERROR)
    if error_id:
        error_id = u'{}: {}'.format(GT(u'Error ID'), error_id)
        error_dialog.SetExtendedMessage(error_id)
        
        # Modify for Logger
        message = u'{}; {}'.format(message, error_id)
    
    Logger.Error(
        u'{}: {}'.format(GT(u'Window ID'), window.GetId()), message)
    
    error_dialog.ShowModal()
