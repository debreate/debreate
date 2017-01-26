# -*- coding: utf-8 -*-

## \package ui.dialog

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.language           import GT
from dbr.log                import Logger
from dbr.workingdir         import ChangeWorkingDirectory
from globals.bitmaps        import ICON_ERROR
from globals.bitmaps        import ICON_EXCLAMATION
from globals.bitmaps        import ICON_INFORMATION
from globals.bitmaps        import ICON_QUESTION
from globals.moduleaccess   import ModuleAccessCtrl
from globals.project        import project_wildcards
from globals.project        import supported_suffixes
from globals.strings        import TextIsEmpty
from globals.wizardhelper   import GetMainWindow
from input.select           import ComboBox
from input.text             import TextAreaPanel
from ui.button              import AddCustomButtons
from ui.hyperlink           import Hyperlink
from ui.layout              import BoxSizer


## A base dialog class
#  
#  Differences from wx.Dialog:
#    * Border is always resizable.
#    * Centers on parent when ShowModal is called.
class BaseDialog(wx.Dialog):
    def __init__(self, parent=None, ID=wx.ID_ANY, title=GT(u'Title'), pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr):
        if parent == None:
            parent = GetMainWindow()
        
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style|wx.RESIZE_BORDER, name)
    
    
    ## Centers on parent then shows dialog in modal form
    #  
    #  \override wx.Dialog.ShowModal
    def ShowModal(self):
        if self.GetParent():
            self.CenterOnParent()
        
        return wx.Dialog.ShowModal(self)


## TODO: Doxygen
class StandardDirDialog(wx.DirDialog):
    def __init__(self, parent, title, style=wx.DD_DEFAULT_STYLE):
        
        # Setting os.getcwd() causes dialog to always be opened in working directory
        wx.DirDialog.__init__(self, parent, title, os.getcwd(),
                style=style|wx.DD_DIR_MUST_EXIST|wx.DD_NEW_DIR_BUTTON|wx.DD_CHANGE_DIR)
        
        # FIXME: Find inherited bound event
        self.Bind(wx.EVT_BUTTON, self.OnAccept)
        
        self.CenterOnParent()
    
    
    ## TODO: Doxygen
    def OnAccept(self, event=None):
        path = self.GetPath()
        
        if os.path.isdir(path):
            self.EndModal(wx.ID_OK)
            return
        
        # FIXME: Use Logger
        print(u'DEBUG: [{}] Path is not a directory: {}'.format(__name__, path))


## A standard system file dialog modified for advanced use
class StandardFileDialog(wx.FileDialog):
    def __init__(self, parent, title=u'Choose a file', defaultFile=u'',
            defaultExt=None, wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE,
            pos=wx.DefaultPosition, size=wx.DefaultSize, name=u'filedlg'):
        
        # Setting os.getcwd() causes dialog to always be opened in working directory
        wx.FileDialog.__init__(self, parent, title, os.getcwd(), defaultFile, wildcard, style, pos)
        
        self.SetSize(size)
        self.SetName(name)
        self.Extension = defaultExt
        
        if style & wx.FD_SAVE:
            wx.EVT_BUTTON(self, self.AffirmativeId, self.OnAccept)
        
        if self.GetWindowStyleFlag() & wx.FD_CHANGE_DIR:
            Logger.Warn(__name__, u'Found FD_CHANGE_DIR style, could conflict with OnAccept method')
        
        self.CenterOnParent()
    
    
    ## TODO: Doxygen
    def GetExtension(self):
        return self.Extension
    
    
    ## TODO: Doxygen
    def HasExtension(self, path):
        if u'.' in path:
            if path.split(u'.')[-1] != u'':
                return True
        
        return False
    
    
    ## TODO: Doxygen
    def OnAccept(self, event=None):
        if self.Extension:
            if not self.Filename.endswith(self.Extension):
                # Adds extensions if not specified
                self.SetFilename(self.Filename)
        
        if self.Path:
            if os.path.isfile(self.Path):
                overwrite = OverwriteDialog(self, self.Path)
                
                if not ShowDialog(overwrite):
                    return
                
                try:
                    os.remove(self.Path)
                
                except OSError:
                    # File was removed before confirmation
                    Logger.Debug(__name__, u'Item was removed before confirmation: {}'.format(self.Path))
                    #print(u'DEBUG: [{}] Items was removed before confirmation: {}'.format(__name__, self.Path))
                    #print(u'FIXME: Cannot import logger')
            
            # Because we are not using default FileDialog methods, we must set
            # directory manually.
            self.SetDirectory(os.path.dirname(self.Path))
            
            # File & directory dialogs should call this function
            ChangeWorkingDirectory(self.GetDirectory())
            
            self.EndModal(self.AffirmativeId)
    
    
    ## Updates the Filename & Path attributes
    #  
    #  Differences from inherited method:
    #  - If the filename does not already have an extension, the default
    #    extension will be appended.
    #  \param filename
    #    New \b \e string filename
    def SetFilename(self, filename):
        if filename:
            if filename.endswith(u'.'):
                # Strip trailing periods
                filename = filename.rstrip(u'.')
            
            # Allow users to manually set filename extension
            if not u'.' in filename:
                if self.Extension:
                    ext = self.Extension
                    if not ext.startswith(u'.'):
                        ext = u'.{}'.format(ext)
                    
                    if not filename.endswith(ext):
                        filename = u'{}{}'.format(filename, ext)
        
        return wx.FileDialog.SetFilename(self, filename)


# FIXME: Unneeded?
class StandardFileSaveDialog(StandardFileDialog):
    def __init__(self, parent, title, defaultExt=wx.EmptyString,
            wildcard=wx.FileSelectorDefaultWildcardStr):
        
        # Initialize parent class
        StandardFileDialog.__init__(self, parent, title, defaultExt=defaultExt,
                wildcard=wildcard, style=wx.FD_SAVE)


# FIXME: Unneded?
class StandardFileOpenDialog(StandardFileDialog):
    def __init__(self, parent, title, defaultExt=wx.EmptyString,
            wildcard=wx.FileSelectorDefaultWildcardStr):
        
        # Initialize parent class
        StandardFileDialog.__init__(self, parent, title, defaultExt=defaultExt,
                wildcard=wildcard, style=wx.FD_OPEN)
    
    
    ## TODO: Doxygen
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
    def __init__(self, parent, title=GT(u'Message'), icon=ICON_INFORMATION, text=wx.EmptyString,
            details=wx.EmptyString, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
            buttons=(wx.ID_OK,), linewrap=0):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=style)
        
        # Allow using strings for 'icon' argument
        if isinstance(icon, (unicode, str)):
            icon = wx.Bitmap(icon)
        
        icon = wx.StaticBitmap(self, wx.ID_ANY, icon)
        
        txt_message = wx.StaticText(self, label=text)
        if linewrap:
            txt_message.Wrap(linewrap)
        
        # self.details needs to be empty for constructor
        self.details = wx.EmptyString
        details = details
        
        # *** Layout *** #
        
        self.lyt_urls = BoxSizer(wx.VERTICAL)
        
        # Only set if buttons are added to dialog
        self.lyt_buttons = None
        
        lyt_main = wx.GridBagSizer(5, 5)
        lyt_main.SetCols(3)
        lyt_main.AddGrowableRow(3)
        lyt_main.AddGrowableCol(2)
        lyt_main.Add(icon, (0, 0), (5, 1), wx.ALIGN_TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM, 20)
        lyt_main.Add(txt_message, (0, 1), (1, 2), wx.RIGHT|wx.TOP, 20)
        lyt_main.Add(self.lyt_urls, (1, 1), (1, 2), wx.RIGHT, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        
        self.AddButtons(buttons)
        
        if not TextIsEmpty(details):
            # self.details will be set here
            self.CreateDetailedView(details)
        
        else:
            self.Layout()
            
            self.Fit()
            self.SetMinSize(self.GetSize())
        
        self.CenterOnParent()
    
    
    ## Add custom buttons to dialog
    #  
    #  NOTE: Do not call before self.SetSizer
    #  
    #  FIXME: Rename to SetButtons???
    #  FIXME: Should delete any previous buttons
    def AddButtons(self, button_ids):
        self.lyt_buttons = AddCustomButtons(self, button_ids)
        
        self.Sizer.Add(self.lyt_buttons, (4, 2),
                flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.RIGHT|wx.TOP|wx.BOTTOM, border=5)
    
    
    ## Adds a clickable link to the dialog
    def AddURL(self, url):
        if not isinstance(url, Hyperlink):
            url = Hyperlink(self, wx.ID_ANY, label=url, url=url)
        
        self.lyt_urls.Add(url, 0, wx.ALIGN_CENTER_VERTICAL)
        
        self.Layout()
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.CenterOnParent()
    
    
    ## Shows dialog modal & returns 'confirmed' value
    #  
    #  \return
    #    \b \e bool : True if ShowModal return value one of wx.ID_OK, wx.OK, wx.ID_YES, wx.YES
    def Confirmed(self):
        return self.ShowModal() in (wx.ID_OK, wx.OK, wx.ID_YES, wx.YES)
    
    
    ## Adds buttons & details text to dialog
    #  
    #  \param details
    #        \b \e unicode|str : Detailed text to show in dialog
    def CreateDetailedView(self, details):
        # Controls have not been constructed yet
        if TextIsEmpty(self.details):
            self.btn_details = wx.ToggleButton(self, label=GT(u'Details'))
            #btn_copy = wx.Button(self, label=GT(u'Copy details'))
            
            self.dsp_details = TextAreaPanel(self, value=details,
                    style=wx.TE_READONLY)
            
            # *** Event handlers *** #
            
            self.btn_details.Bind(wx.EVT_TOGGLEBUTTON, self.ToggleDetails)
            #btn_copy.Bind(wx.EVT_BUTTON, self.OnCopyDetails)
            
            layout = self.GetSizer()
            layout.Add(self.btn_details, (2, 1))
            #layout.Add(btn_copy, (2, 2), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
            layout.Add(self.dsp_details, (3, 1), (1, 2), wx.EXPAND|wx.RIGHT, 5)
            
            self.ToggleDetails()
        
        if not TextIsEmpty(details):
            for C in self.GetChildren():
                if isinstance(C, TextAreaPanel):
                    self.details = details
                    C.SetValue(self.details)
                    
                    return True
        
        return False
    
    
    ## Attempts to retrieve button instance matching btn_id
    #  
    #  FIXME: This will fail if there are standard buttons in the dialog
    #  FIXME: Retrieving by label doesn't work
    #  \param btn_id
    #    ID of the button instance to retrieve
    #  \return
    #    \b \e wx.Button instance or None
    def GetButton(self, btn_id):
        # Allow search by label
        use_label = not isinstance(btn_id, int)
        
        if self.lyt_buttons:
            for sizer in self.lyt_buttons.GetChildren():
                sizer = sizer.GetSizer()
                
                btn_layout = sizer.GetChildren()
                
                if btn_layout:
                    BTN = btn_layout[0].GetWindow()
                    LBL = None
                    
                    if len(btn_layout) < 2 and isinstance(BTN, wx.Button):
                        LBL = BTN.GetLabel()
                    
                    else:
                        LBL = btn_layout[1]
                        if isinstance(LBL, wx.StaticText):
                            LBL = LBL.GetLabel()
                    
                    if not use_label:
                        if BTN.GetId() == btn_id:
                            return BTN
                    
                    else:
                        if LBL == btn_id:
                            return BTN
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Layout initially wrong
    #  TODO: Allow copying details to clipboard
    def OnCopyDetails(self, event=None):
        print(u'DEBUG: Copying details to clipboard ...')
        
        DetailedMessageDialog(self, u'FIXME', ICON_EXCLAMATION,
                u'Copying details to clipboard not functional').ShowModal()
        return
        
        cb_set = False
        
        clipboard = wx.Clipboard()
        if clipboard.Open():
            print(u'DEBUG: Clipboard opened')
            
            details = wx.TextDataObject(self.dsp_details.GetValue())
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
        
        wx.MessageBox(u'FIXME: Details not copied to clipboard', GT(u'Debug'))
    
    
    ## Override inherited method to center on parent window first
    def ShowModal(self, *args, **kwargs):
        if self.Parent:
            self.CenterOnParent()
        
        return wx.Dialog.ShowModal(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def SetDetails(self, details):
        return self.CreateDetailedView(details)
    
    
    ## TODO: Doxygen
    def ToggleDetails(self, event=None):
        try:
            if self.btn_details.GetValue():
                self.dsp_details.Show()
            
            else:
                self.dsp_details.Hide()
            
            self.Layout()
            self.Fit()
            self.SetMinSize(self.GetSize())
            
            return True
        
        except AttributeError:
            # Disable toggling details
            self.btn_details.Hide()
            
            self.Layout()
            self.Fit()
            self.SetMinSize(self.GetSize())
            
            return False


## Dialog that gives the option to confirm or cancel
class ConfirmationDialog(DetailedMessageDialog):
    def __init__(self, parent, title=GT(u'Warning'), text=wx.EmptyString,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, buttons=(wx.ID_OK, wx.ID_CANCEL,)):
        
        DetailedMessageDialog.__init__(self, parent, title, icon=ICON_QUESTION,
                text=text, style=style, buttons=buttons)


## Dialog for the main window when a modified project is being closed
class ConfirmSaveDialog(DetailedMessageDialog):
    def __init__(self, parent, title=GT(u'Warning'), text=wx.EmptyString,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
            buttons=(wx.ID_OK, wx.ID_CANCEL, wx.ID_SAVE,)):
        
        DetailedMessageDialog.__init__(self, parent, title, icon=ICON_QUESTION,
                text=text, style=style, buttons=buttons)
        
        btn_save = self.GetButton(wx.ID_SAVE)
        
        # *** Event Handling *** #
        
        if btn_save:
            btn_save.Bind(wx.EVT_BUTTON, self.OnButtonSave)
    
    
    def OnButtonSave(self, event=None):
        self.EndModal(wx.ID_SAVE)


## TODO: Doxygen
class OverwriteDialog(ConfirmationDialog):
    def __init__(self, parent, filename):
        text = u'{}\n\n{}'.format(GT(u'Overwrite file?'), filename)
        
        ConfirmationDialog.__init__(self, parent, GT(u'File Exists'), text)


## Message dialog that shows an error & details
class ErrorDialog(DetailedMessageDialog):
    def __init__(self, parent, title=GT(u'Error'), text=GT(u'An error has occurred'),
            details=wx.EmptyString, linewrap=0):
        DetailedMessageDialog.__init__(self, parent, title, ICON_ERROR, text, details,
                linewrap=linewrap)


## TODO: Doxygen
class SuperUserDialog(wx.Dialog):
    def __init__(self, ID=wx.ID_ANY):
        wx.Dialog.__init__(self, GetMainWindow(), ID)
        
        # User selector
        self.users = ComboBox(self)


## TODO: Doxygen
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


## TODO: Doxygen
def GetDirDialog(parent, title):
    if parent == None:
        parent = GetMainWindow()
        
    dir_open = StandardDirDialog(parent, title)
    
    return dir_open


## TODO: Doxygen
def GetFileOpenDialog(parent, title, ext_filters, defaultExt=None):
    if parent == None:
        parent = GetMainWindow()
    
    if isinstance(ext_filters, (list, tuple)):
        ext_filters = u'|'.join(ext_filters)
    
    file_open = StandardFileOpenDialog(parent, title, wildcard=ext_filters)
    
    return file_open


## Retrieves a dialog for display
#  
#  If 'Use custom dialogs' is selected from
#    the main window, the a custom defined
#    dialog is returned. Otherwise the systems
#    default dialog is used.
#    FIXME: Perhaps should be moved to ui.output
#  \param main_window
#        Debreate's main window class
#  \param title
#        Text to be shown in the dialogs's title bar
#  \param wildcard
#        Wildcard to be used to filter filenames
#  \param defaultExt
#        The default filename extension to use when opening or closing a file
#          Only applies to custom dialogs
#  \return
#        The dialog window to be shown
def GetFileSaveDialog(parent, title, wildcard=wx.FileSelectorDefaultWildcardStr, extension=None,
        confirm_overwrite=True):
    if parent == None:
        parent = GetMainWindow()
    
    if isinstance(wildcard, (list, tuple)):
        wildcard = u'|'.join(wildcard)
    
    '''
    # FIXME: Broken
    file_save = StandardFileSaveDialog(parent, title, defaultExt=extension,
            wildcard=ext_filters)
    '''
    
    FD_STYLE = wx.FD_SAVE|wx.FD_CHANGE_DIR
    if confirm_overwrite:
        FD_STYLE = FD_STYLE|wx.FD_OVERWRITE_PROMPT
    
    file_save = wx.FileDialog(parent, title, os.getcwd(), wildcard=wildcard, style=FD_STYLE)
    file_save.CenterOnParent()
    
    return file_save


## Used to display a dialog window
#  
#  For custom dialogs, the method 'DisplayModal()' is used
#    to display the dialog. For stock dialogs, 'ShowModal()'
#    is used. The dialog that will be shown is determined
#    from 'GetFileSaveDialog'.
#    FIXME: Perhaps should be moved to ui.output
#  \param dialog
#    The dialog window to be shown
#  \param center
#    Positioning relative to parent window
#  \return
#    'True' if the dialog's return value is 'wx..ID_OK', 'False'
#      otherwise
#  
#  \b Alias: \e dbr.ShowDialog
def ShowDialog(dialog, center=wx.BOTH):
    dialog.CenterOnParent(center)
    
    return dialog.ShowModal() in (wx.OK, wx.ID_OK, wx.YES, wx.ID_YES, wx.OPEN, wx.ID_OPEN,)


## Displays an instance of ErrorDialog class
#  
#  Dialog is orphaned if parent is None so it can be displayed
#  without main window in cases of initialization errors.
#  \param text
#        \b \e str|unicode: Explanation of error
#  \param details
#        \b \e str|unicode: Extended details of error
#  \param parent
#    \b \e Parent window of new dialog
#    If False, parent is set to main window
#    If None, dialog is orphaned
#  \param module
#        \b \e str|unicode: Module where error was caught (used for Logger output)
#  \param warn
#        \b \e bool: Show log message as warning instead of error
def ShowErrorDialog(text, details=None, parent=False, warn=False, title=GT(u'Error'),
            linewrap=0):
    # Instantiate Logger message type so it can be optionally changed
    PrintLogMessage = Logger.Error
    if warn:
        PrintLogMessage = Logger.Warn
    
    logger_text = text
    
    if isinstance(text, (tuple, list)):
        logger_text = u'; '.join(text)
        text = u'\n'.join(text)
    
    if details:
        logger_text = u'{}:\n{}'.format(logger_text, details)
    
    if parent == False:
        parent = GetMainWindow()
    
    if not parent:
        module_name = __name__
    
    elif isinstance(parent, ModuleAccessCtrl):
        module_name = parent.GetModuleName()
    
    else:
        module_name = parent.GetName()
    
    PrintLogMessage(module_name, logger_text)
    
    error_dialog = ErrorDialog(parent, title, text, linewrap=linewrap)
    if details:
        error_dialog.SetDetails(details)
    
    error_dialog.ShowModal()


## A function that displays a modal message dialog on the main window
def ShowMessageDialog(text, title=GT(u'Message'), details=None, module=None, parent=None,
            linewrap=0):
    if not parent:
        parent = GetMainWindow()
    
    if not module and isinstance(parent, ModuleAccessCtrl):
        module = parent.GetModuleName()
    
    logger_text = text
    if isinstance(text, (tuple, list)):
        logger_text = u'; '.join(text)
        text = u'\n'.join(text)
    
    if details:
        logger_text = u'{}:\n{}'.format(logger_text, details)
    
    message_dialog = DetailedMessageDialog(parent, title, ICON_INFORMATION, text, linewrap=linewrap)
    if details:
        message_dialog.SetDetails(details)
    
    Logger.Debug(module, logger_text)
    
    message_dialog.ShowModal()
