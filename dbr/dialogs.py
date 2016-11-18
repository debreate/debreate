# -*- coding: utf-8 -*-

## \package dbr.dialogs


import os, wx

from dbr.buttons        import ButtonConfirm
from dbr.custom         import TextIsEmpty
from dbr.language       import GT
from dbr.log            import Logger
from dbr.textinput      import MultilineTextCtrlPanel
from dbr.workingdir     import ChangeWorkingDirectory
from globals.bitmaps    import ICON_ERROR
from globals.bitmaps    import ICON_INFORMATION
from globals.paths      import PATH_app
from globals.project    import project_wildcards
from globals.project    import supported_suffixes


class OverwriteDialog(wx.MessageDialog):
    def __init__(self, parent, path):
        wx.MessageDialog.__init__(self, parent, wx.EmptyString,
                style=wx.ICON_QUESTION|wx.YES_NO|wx.YES_DEFAULT)
        
        self.parent = parent
        
        self.SetYesNoLabels(GT(u'Replace'), GT(u'Cancel'))
        
        filename = os.path.basename(path)
        dirname = os.path.basename(os.path.dirname(path))
        
        self.SetMessage(
            GT(u'A file named "{}" already exists. Do you want to replace it?').format(filename)
        )
        
        self.SetExtendedMessage(
            GT(u'The file already exists in "{}". Replacing it will overwrite its contents.').format(dirname)
        )


class StandardDirDialog(wx.DirDialog):
    def __init__(self, parent, title, style=wx.DD_DEFAULT_STYLE):
        
        # Setting os.getcwd() causes dialog to always be opened in working directory
        wx.DirDialog.__init__(self, parent, title, os.getcwd(),
                style=style|wx.DD_DIR_MUST_EXIST|wx.DD_NEW_DIR_BUTTON|wx.DD_CHANGE_DIR)
        
        # FIXME: Find inherited bound event
        wx.EVT_BUTTON(self, wx.ID_OPEN, self.OnAccept)
        
        self.CenterOnParent()
    
    
    def OnAccept(self, event=None):
        path = self.GetPath()
        
        if os.path.isdir(path):
            self.EndModal(wx.ID_OK)
            return
        
        print(u'DEBUG: [dbr.dialogs] Path is not a directory: {}'.format(path))


class StandardFileDialog(wx.FileDialog):
    def __init__(self, parent, title, default_extension=wx.EmptyString,
                wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE):
        
        # Setting os.getcwd() causes dialog to always be opened in working directory
        wx.FileDialog.__init__(self, parent, title, os.getcwd(), wildcard=wildcard, style=style)
        
        self.parent = parent
        
        self.extension = default_extension
        
        # FIXME: Should use ID_SAVE & ID_OPEN
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnAccept)
        
        self.CenterOnParent()
    
    
    def GetDirectory(self, directory=None):
        if directory == None:
            directory = self.GetPath()
        
        # Recursively check for first directory in hierarchy
        if not os.path.isdir(directory):
            return self.GetDirectory(os.path.dirname(directory))
        
        return directory
    
    
    def GetExtension(self):
        return self.extension
    
    
    ## FIXME: Seems to be being called 3 times
    def GetFilename(self, *args, **kwargs):
        filename = wx.FileDialog.GetFilename(self, *args, **kwargs)
        
        # Allow users to manually set filename extension
        if not self.HasExtension(filename):
            if not filename.split(u'.')[-1] == self.extension:
                filename = u'{}.{}'.format(filename, self.extension)
        
        return filename
    
    
    ## Fixme: Seems to be being called twice
    def GetPath(self, *args, **kwargs):
        path = wx.FileDialog.GetPath(self, *args, **kwargs)
        
        if len(path):
            if path[-1] == u'.':
                #wx.MessageDialog(self, GT(u'Filename cannot end with "{}"').format(path[-1]), GT(u'Error'),
                #        style=wx.ICON_ERROR|wx.OK).ShowModal()
                name_error = wx.MessageDialog(wx.GetApp().GetTopWindow(), GT(u'Error'),
                        style=wx.ICON_ERROR|wx.OK)
                
                name_error.SetExtendedMessage(GT(u'Name cannot end with "{}"').format(path[-1]))
                # FIXME: Setting icon causes segfault
                #name_error.SetIcon(MAIN_ICON)
                name_error.ShowModal()
                
                return None
        
        out_dir = os.path.dirname(path)
        return u'{}/{}'.format(out_dir, self.GetFilename())
    
    
    def HasExtension(self, path):
        if u'.' in path:
            if path.split(u'.')[-1] != u'':
                return True
        
        return False
    
    
    def OnAccept(self, event=None):
        path = self.GetPath()
        
        if path:
            if os.path.isfile(path):
                overwrite = OverwriteDialog(wx.GetApp().GetTopWindow(), path).ShowModal()
                
                if overwrite != wx.ID_YES:
                    return
                
                os.remove(path)
            
            # File & directory dialogs should call this function
            ChangeWorkingDirectory(self.GetDirectory())
            
            self.EndModal(wx.ID_OK)


# FIXME: Unneeded?
class StandardFileSaveDialog(StandardFileDialog):
    def __init__(self, parent, title, default_extension=wx.EmptyString,
            wildcard=wx.FileSelectorDefaultWildcardStr):
        
        # Initialize parent class
        StandardFileDialog.__init__(self, parent, title, default_extension=default_extension,
                wildcard=wildcard, style=wx.FD_SAVE)


# FIXME: Unneded?
class StandardFileOpenDialog(StandardFileDialog):
    def __init__(self, parent, title, default_extension=wx.EmptyString,
            wildcard=wx.FileSelectorDefaultWildcardStr):
        
        # Initialize parent class
        StandardFileDialog.__init__(self, parent, title, default_extension=default_extension,
                wildcard=wildcard, style=wx.FD_OPEN)
    
    
    def OnAccept(self, event=None):
        # File & directory dialogs should call this function
        ChangeWorkingDirectory(self.GetDirectory())
        
        self.EndModal(wx.ID_OK)



# *** MESSAGE & ERROR *** #

## Displays a dialog with message & details
#  
#  FIXME: Crashes if icon is wx.NullBitmap
#  \param parent
#        \b \e wx.Window : The parent window
#  \param title
#        \b \e unicode|str : Text to display in title bar
#  \param icon
#        \b \e wx.Bitmap|unicode|str : Image to display
class DetailedMessageDialog(wx.Dialog):
    def __init__(self, parent, title=GT(u'Message'), icon=wx.NullBitmap, text=wx.EmptyString,
            details=wx.EmptyString, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(500,500), style=style)
        
        # Allow using strings for 'icon' argument
        if isinstance(icon, (unicode, str)):
            icon = wx.Bitmap(icon)
        
        self.icon = wx.StaticBitmap(self, -1, icon)
        
        self.text = wx.StaticText(self, -1, text)
        
        self.button_details = wx.ToggleButton(self, -1, GT(u'Details'))
        self.btn_copy_details = wx.Button(self, label=GT(u'Copy details'))
        
        wx.EVT_TOGGLEBUTTON(self.button_details, -1, self.ToggleDetails)
        wx.EVT_BUTTON(self.btn_copy_details, wx.ID_ANY, self.OnCopyDetails)
        
        if TextIsEmpty(details):
            self.button_details.Hide()
            
        layout_btn_H1 = wx.BoxSizer(wx.HORIZONTAL)
        layout_btn_H1.Add(self.button_details, 1)
        layout_btn_H1.Add(self.btn_copy_details, 1)
        
        self.details = MultilineTextCtrlPanel(self, value=details, size=(300,150), style=wx.TE_READONLY)
        
        self.button_ok = ButtonConfirm(self)
        
        layout_RV = wx.BoxSizer(wx.VERTICAL)
        layout_RV.AddSpacer(10)
        layout_RV.Add(self.text)
        layout_RV.AddSpacer(20)
        layout_RV.Add(layout_btn_H1)
        layout_RV.Add(self.details, 1, wx.EXPAND)
        layout_RV.Add(self.button_ok, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.RIGHT|wx.BOTTOM, 5)
        
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.icon, 0, wx.ALL, 20)
        self.main_sizer.Add(layout_RV, 1, wx.EXPAND)
        self.main_sizer.AddSpacer(10)
        
        #self.SetInitialSize()
        
        self.SetAutoLayout(True)
        self.ToggleDetails()
        
        self.btn_copy_details.Hide()
        self.details.Hide()
        
        
        if details != wx.EmptyString:
            self.SetBestWidth()
        
        self.CenterOnParent()
    
    
    # FIXME:
    def OnCopyDetails(self, event=None):
        print(u'DEBUG: Copying details to clipboard ...')
        
        cb_set = False
        
        clipboard = wx.Clipboard()
        if clipboard.Open():
            print(u'DEBUG: Clipboard opened')
            
            details = wx.TextDataObject(self.details.GetValue())
            print(u'DEBUG: Details set to:\n{}'.format(details.GetText()))
            
            clipboard.Clear()
            print(u'DEBUG: Clipboard cleared')
            
            cb_set = clipboard.SetData(details)
            print(u'DEBUG: Clipboard data set')
            
            clipboard.Flush()
            print(u'DEBUG: Clipboard flushed')
            
            clipboard.Close()
            print(u'DEBUG: Clipboard cloased')
        
        del clipboard
        print(u'DEBUG: Clipboard object deleted')
        
        wx.MessageBox(GT(u'FIXME: Details not copied to clipboard'), GT(u'Debug'))
    
    
    ## Sets the minimum width of the details text area
    #  
    #  FIXME: Doesn't work
    def SetBestWidth(self):
        W, H = self.details.GetSize()
        
        for L in self.details.GetValue().split(u'\n'):
            line_length = len(L)
            if line_length > W:
                W = line_length
        
        Logger.Debug(__name__, GT(u'Longest line in details: {}').format(W))
        
        self.details.SetMinSize(wx.Size(W, H))
        self.Layout()
    
    
    def SetDetails(self, details):
        self.details.SetValue(details)
        self.details.SetSize(self.details.GetBestSize())
        
        if not self.button_details.IsShown():
            self.button_details.Show()
        
        #self.SetBestFittingSize()
        self.Layout()
    
    
    def ToggleDetails(self, event=None):
        if self.button_details.GetValue():
            self.details.Show()
        
        else:
            self.details.Hide()
        
        self.SetSizerAndFit(self.main_sizer)
        self.Layout()


## Message dialog that shows an error & details
class ErrorDialog(DetailedMessageDialog):
    def __init__(self, parent, text=wx.EmptyString, details=wx.EmptyString):
        DetailedMessageDialog.__init__(self, parent, GT(u'Error'), ICON_ERROR, text, details)
        
        if not TextIsEmpty(details):
            self.btn_copy_details.Show()
        
        self.Layout()
    
    
    def SetDetails(self, details):
        if not self.btn_copy_details.IsShown():
            self.btn_copy_details.Show()
        
        DetailedMessageDialog.SetDetails(self, details)


## Dialog shown when Debreate is run for first time
#  
#  If configuration file is not found or corrupted
#    this dialog is shown.
class FirstRun(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, GT(u'Debreate First Run'), size=(450,300))
        
        m2 = GT(u'This message only displays on the first run, or if\nthe configuration file becomes corrupted.')
        m3 = GT(u'The default configuration file will now be created.')
        m4 = GT(u'To delete this file, type the following command in a\nterminal:')
        
        message1 = GT(u'Thank you for using Debreate.')
        message1 = u'{}\n\n{}'.format(message1, m2)
        
        message2 = m3
        message2 = u'{}\n{}'.format(message2, m4)
        
        # Set the titlebar icon
        self.SetIcon(wx.Icon(u'{}/bitmaps/debreate64.png'.format(PATH_app), wx.BITMAP_TYPE_PNG))
        
        # Display a message to create a config file
        text1 = wx.StaticText(self, label=message1)
        text2 = wx.StaticText(self, label=message2)
        
        rm_cmd = wx.StaticText(self, label=u'rm -f ~/.config/debreate/config')
        
        layout_V1 = wx.BoxSizer(wx.VERTICAL)
        layout_V1.Add(text1, 1)
        layout_V1.Add(text2, 1, wx.TOP, 15)
        layout_V1.Add(rm_cmd, 0, wx.TOP, 10)
        
        # Show the Debreate icon
        dbicon = wx.Bitmap(u'{}/bitmaps/debreate64.png'.format(PATH_app), wx.BITMAP_TYPE_PNG)
        icon = wx.StaticBitmap(self, -1, dbicon)
        
        # Button to confirm
        self.button_ok = wx.Button(self, wx.ID_OK)
        
        # Nice border
        self.border = wx.StaticBox(self, -1)
        border_box = wx.StaticBoxSizer(self.border, wx.HORIZONTAL)
        border_box.AddSpacer(10)
        border_box.Add(icon, 0, wx.ALIGN_CENTER)
        border_box.AddSpacer(10)
        border_box.Add(layout_V1, 1, wx.ALIGN_CENTER)
        
        # Set Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(border_box, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(self.button_ok, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM|wx.TOP, 5)
        
        self.SetSizer(sizer)
        self.Layout()


## Retrieves a dialog for display
#  
#  If 'Use custom dialogs' is selected from
#    the main window, the a custom defined
#    dialog is returned. Otherwise the systems
#    default dialog is used.
#    FIXME: Perhaps should be moved to dbr.custom
#  \param main_window
#        Debreate's main window class
#  \param title
#        Text to be shown in the dialogs's title bar
#  \param ext_filter
#        Wildcard to be used to filter filenames
#  \param default_extension
#        The default filename extension to use when opening or closing a file
#          Only applies to custom dialogs
#  \return
#        The dialog window to be shown
#  
#  \b Alias: \e dbr.GetFileSaveDialog
def GetFileSaveDialog(main_window, title, ext_filters, extension=None):
    if isinstance(ext_filters, (list, tuple)):
        ext_filters = u'|'.join(ext_filters)
    
    file_save = StandardFileSaveDialog(main_window, title, default_extension=extension,
            wildcard=ext_filters)
    
    return file_save


def GetFileOpenDialog(main_window, title, ext_filters, default_extension=None):
    if isinstance(ext_filters, (list, tuple)):
        ext_filters = u'|'.join(ext_filters)
    
    file_open = StandardFileOpenDialog(main_window, title, wildcard=ext_filters)
    
    return file_open


def GetDirDialog(main_window, title):
    dir_open = StandardDirDialog(main_window, title)
    
    return dir_open


## Used to display a dialog window
#  
#  For custom dialogs, the method 'DisplayModal()' is used
#    to display the dialog. For stock dialogs, 'ShowModal()'
#    is used. The dialog that will be shown is determined
#    from 'GetFileSaveDialog'.
#    FIXME: Perhaps should be moved to dbr.custom
#  \param main_window
#    Debreate's main window class
#  \param dialog
#    The dialog window to be shown
#  \return
#    'True' if the dialog's return value is 'wx..ID_OK', 'False'
#      otherwise
#  
#  \b Alias: \e dbr.ShowDialog
def ShowDialog(dialog):
    # Dialog's parent should be set to main window
    #debreate = dialog.GetParent()
    
    if False: #debreate.cust_dias.IsChecked():
        return dialog.DisplayModal()
    else:
        return dialog.ShowModal() == wx.ID_OK


## Displays an instance of ErrorDialog class
#  
#  \param text
#        \b \e str|unicode: Explanation of error
#  \param details
#        \b \e str|unicode: Extended details of error
#  \param module
#        \b \e str|unicode: Module where error was caught (used for Logger output)
#  \param warn
#        \b \e bool: Show log message as warning instead of error
def ShowErrorDialog(text, details=None, module=None, warn=False):
    Logger.Debug(__name__, GT(u'Text: {}').format(text))
    Logger.Debug(__name__, GT(u'Details: {}').format(details))
    Logger.Debug(__name__, GT(u'Module: {}').format(module))
    Logger.Debug(__name__, GT(u'Logger warning instead of error: {}').format(warn))
    
    PrintLogMessage = Logger.Error
    if warn:
        PrintLogMessage = Logger.Warning
    
    logger_text = text
    
    if isinstance(text, (tuple, list)):
        logger_text = u'; '.join(text)
        text = u'\n'.join(text)
    
    if details:
        logger_text = u'{}:\n{}'.format(logger_text, details)
    
    main_window = wx.GetApp().GetTopWindow()
    
    if not module:
        module = main_window.__name__
    
    PrintLogMessage(module, logger_text)
    
    error_dialog = ErrorDialog(main_window, text)
    if details:
        error_dialog.SetDetails(details)
    
    error_dialog.ShowModal()


## A function that displays a modal message dialog on the main window
def ShowMessageDialog(text, title=GT(u'Message'), details=None, module=None):
    main_window = wx.GetApp().GetTopWindow()
    if not module:
        module = main_window.__name__
    
    logger_text = text
    if isinstance(text, (tuple, list)):
        logger_text = u'; '.join(text)
        text = u'\n'.join(text)
    
    if details:
        logger_text = u'{}:\n{}'.format(logger_text, details)
    
    message_dialog = DetailedMessageDialog(main_window, title, ICON_INFORMATION, text)
    if details:
        message_dialog.SetDetails(details)
    
    Logger.Debug(module, logger_text)
    
    message_dialog.ShowModal()


def GetDialogWildcards(ID):
    proj_def = project_wildcards[ID][0]
    wildcards = list(project_wildcards[ID][1])
    
    for X in range(len(wildcards)):
        wildcards[X] = u'.{}'.format(wildcards[X])
    
    # Don't show list of suffixes in dialog's description
    if project_wildcards[ID][1] != supported_suffixes:
        proj_def = u'{} ({})'.format(proj_def, u', '.join(wildcards))
    
    for X in range(len(wildcards)):
        wildcards[X] = u'*{}'.format(wildcards[X])
    
    return (proj_def, u';'.join(wildcards))
