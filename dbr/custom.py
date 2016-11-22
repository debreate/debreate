# -*- coding: utf-8 -*-

## \package dbr.custom


# System imports
import os, sys, webbrowser
import wx.combo, wx.lib.mixins.listctrl as LC
from wx.lib.docview import PathOnly

from dbr.language   import GT
from dbr.textinput  import MultilineTextCtrlPanel
from globals.ident  import ID_APPEND
from globals.ident  import ID_OVERWRITE
from globals.paths  import PATH_app


# Local imports
db_here = PathOnly(__file__).decode(u'utf-8')

# FIXME: This should be import from dbr.functions
def TextIsEmpty(text):
    text = u''.join(u''.join(text.split(u' ')).split(u'\n'))
    return text == u''


## Dialog shown when Debreate is run for first time
#  
#  If configuration file is not found or corrupted
#    this dialog is shown.
#  TODO: Move to dbr.dialogs
class FirstRun(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, GT(u'Debreate First Run'), size=(450,300))
        
        m2 = GT(u'This message only displays on the first run, or if\nthe configuration file becomes corrupted.')
        m3 = GT(u'The default configuration file will now be created.')
        m4 = GT(u'To delete this file, type the following command in a\nterminal:')
        
        # "OK" button sets to True
        #self.OK = False
        
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


## A generic display area that captures \e stdout & \e stderr
class OutputLog(MultilineTextCtrlPanel):
    ## Constructor
    #  
    #  \param parent
    #        The parent window
    def __init__(self, parent):
        MultilineTextCtrlPanel.__init__(self, parent, style=wx.TE_READONLY)
        self.SetBackgroundColour(u'black')
        self.SetForegroundColour(u'white')
        self.stdout = sys.stdout
        self.stderr = sys.stderr
    
    ## Adds test to the display area
    def write(self, string):
        self.AppendText(string)
    
    def ToggleOutput(self, event=None):
        if sys.stdout == self:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
        else:
            sys.stdout = self
            sys.stdout = self


## Prompt for overwriting a text area
#  
#  TODO: Delete; Deprecated, moved to dbr.dialogs
class OverwriteDialog(wx.Dialog):
    ## Constructor
    #  
    #  \param parent
    #        Parent window
    #  \param id
    #        Window ID (FIXME: Should be set from constant)
    #  \param title
    #        Text to be shown in title bar
    #  \param message
    #        Message to display
    def __init__(self, parent, id=-1, title=GT(u'Overwrite?'), message=u''):
        wx.Dialog.__init__(self, parent, id, title)
        self.message = wx.StaticText(self, -1, message)
        
        ## Button to accept overwrite
        self.button_overwrite = wx.Button(self, ID_OVERWRITE, GT(u'Overwrite'))
        
        self.button_append = wx.Button(self, ID_APPEND, GT(u'Append'))
        
        ## Button to cancel overwrite
        self.button_cancel = wx.Button(self, wx.ID_CANCEL)
        
        # -*- Button events -*- #
        wx.EVT_BUTTON(self.button_overwrite, ID_OVERWRITE, self.OnButton)
        wx.EVT_BUTTON(self.button_append, ID_APPEND, self.OnButton)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.button_overwrite, 0, wx.LEFT|wx.RIGHT, 5)
        hsizer.Add(self.button_append, 0, wx.LEFT|wx.RIGHT, 5)
        hsizer.Add(self.button_cancel, 0, wx.LEFT|wx.RIGHT, 5)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.message, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        vsizer.Add(hsizer, 0, wx.ALIGN_RIGHT|wx.TOP|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizerAndFit(vsizer)
        self.Layout()
    
    ## Defines actions to take when a button is pressed
    #  
    #  Get the event object & close the dialog.
    #  \param event
    #        wx.EVT_BUTTON
    def OnButton(self, event):
        id = event.GetEventObject().GetId()
        self.EndModal(id)
    
    ## Retrieves the message that is displayed in the dialog
    def GetMessage(self, event=None):
        return self.message.GetLabel()


## Object for drag-&-drop text files
class SingleFileTextDropTarget(wx.FileDropTarget):
    ## Constructor
    #  
    #  \param obj
    #        ???
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj
    
    ## Defines actions to take when a file is dropped on object
    #  
    #  \param x
    #        ???
    #  \param y
    #        ???
    #  \param filenames
    #        ???
    def OnDropFiles(self, x, y, filenames):
        if len(filenames) > 1:
            raise ValueError(GT(u'Too many files'))
        text = open(filenames[0]).read()
        try:
            if not TextIsEmpty(self.obj.GetValue()):
                overwrite = OverwriteDialog(self.obj, message = GT(u'The text area is not empty!'))
                id = overwrite.ShowModal()
                if id == ID_OVERWRITE:
                    self.obj.SetValue(text)
                elif id == ID_APPEND:
                    self.obj.SetInsertionPoint(-1)
                    self.obj.WriteText(text)
            else:
                self.obj.SetValue(text)
        except UnicodeDecodeError:
            wx.MessageDialog(None, GT(u'Error decoding file'), GT(u'Error'), wx.OK).ShowModal()


## A customized combo control
#  
#  FIXME: Unused. Was used in page.control
class Combo(wx.combo.ComboCtrl):
    def __init__(self, parent, id=wx.ID_ANY, value=u'', choices=()):
        wx.combo.ComboCtrl.__init__(self, parent, id)
        
        self.Frame = self.GetTopLevelParent()
        
        wx.EVT_LEFT_DOWN(self.Frame, self.HideItems)
        wx.EVT_LEFT_DOWN(parent, self.HideItems)
        
        # Locate textctrl for changing its bg/fg color
        self.bg = self.GetTextCtrl()
        
        wx.EVT_LEFT_DOWN(self.bg, self.HideItems)
        
        # Hide the List if textctrl loses focus
        wx.EVT_KILL_FOCUS(self.bg, self.HideItems)
        
        # Enable scrolling through list with up/down arrows
        wx.EVT_KEY_DOWN(self.bg, self.OnNavigate)
        
        # List to show when button pressed
        self.lb = wx.ListCtrl(parent, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL)
        self.lb.InsertColumn(0, u'')
        for item in choices:
            self.lb.InsertStringItem(0, item)
        self.lb.Hide()
        
        # Select list item hovered by mouse
        wx.EVT_MOTION(self.lb, self.OnMouseOver)
        
        # Set the value of the textctrl when the mouse is clicked
        wx.EVT_LEFT_DOWN(self.lb, self.OnSelect)
        
        # If value argument is not blank, put string in textctrl
        self.SetValue(value)
    
    def PlaceList(self):
        # Lines the list up with the ComboCtrl
        
        # Make the list the same size as the ComboCtrl
        width = self.bg.GetSize()[0]
        self.lb.SetColumnWidth(0, width)
        self.lb.SetSize((width+23, 250)) # Makes the list flush with ComboCtrl
        
        # Place the list under the ComboBox
        cbpos = self.GetPosition()
        cbsize = self.GetSize()
        x = cbpos[0]
        y = cbpos[1] + cbsize[1]
        self.lb.SetPosition((x,y))
    
    def OnButtonClick(self):
        # Make sure that textctrl gets focus when button pressed
        self.bg.SetFocus()
        
        # Hide the list if it is already shown and do nothing else
        if self.lb.IsShown():
            self.lb.Hide()
        
        else:
            # Align list with ComboCtrl
            self.PlaceList()
            
            # Show the list
            self.lb.Show()
    
    def OnMouseOver(self, event):
        # Highlight the item hovered by mouse
        item = self.lb.HitTest(event.GetPosition()) # Returns a tuple so use "item[0]"
        self.lb.Select(item[0])
        event.Skip()
    
    def OnNavigate(self, event):
        # Make sure the list is in the right spot
        self.PlaceList()
        
        # Enable scrolling through list with up/down arrows
        key = event.GetKeyCode()
        cur_item = self.lb.GetFocusedItem()
        if key == 317:
            if self.lb.IsShown() == False:
                self.lb.Show()
            else:
                self.lb.Select(cur_item+1)
        elif key == 315 and cur_item > 0:
            self.lb.Select(cur_item-1)
        
        # Use "Enter" or "Return" keys to set TextCtrl as well
        elif key == wx.WXK_RETURN or key == wx.WXK_NUMPAD_ENTER:
            if self.lb.IsShown():
                self.OnSelect(None)
            else:
                self.lb.Show()
        
        event.Skip()
    
    def OnSelect(self, event):
        # Put the selected text in the txtctrl and hide the list
        self.SetValue(self.lb.GetItemText(self.lb.GetFocusedItem()))
        self.lb.Hide()
        # Give focus back to TextCtrl
        self.bg.SetFocus()
        self.bg.SetInsertionPointEnd()
    
    def HideItems(self, event):
        # Hide the list if it visible
        if self.lb.IsShown():
            self.lb.Hide()
        event.Skip()
    
    def SetValue(self, value):
        # Sets the text in the TextCtrl
        self.bg.SetValue(value)
    
    def SetBackgroundColour(self, color):
        self.bg.SetBackgroundColour(color)
        self.lb.SetBackgroundColour(color)
    
    def GetBackgroundColour(self):
        return self.bg.GetBackgroundColour()
    
    def SetForegroundColour(self, color):
        self.bg.SetForegroundColour(color)
        self.lb.SetForegroundColour(color)
    
    def GetForegroundColour(self):
        return self.bg.GetForegroundColour()
    
    def Clear(self):
        self.bg.Clear()


## A customized report style ListCtrl
#  
#  Columns cannot be resized with context menu to add/delete entries.
#  FIXME: Unused. Was used in page.control.
class LCReport(wx.ListCtrl, LC.TextEditMixin, LC.ListCtrlAutoWidthMixin):
    ## Constructor
    #  
    #  \param parent
    #        Parent window
    #  \param id
    #        Window ID (FIXME: Should be set from constant)
    #  \param style
    #        wx.ListCtrl style to use
    def __init__(self, parent, id=wx.ID_ANY, style=wx.LC_REPORT|wx.SIMPLE_BORDER|wx.LC_SINGLE_SEL):
        wx.ListCtrl.__init__(self, parent, -1,
                style=wx.LC_REPORT|wx.SIMPLE_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        LC.TextEditMixin.__init__(self)
        LC.ListCtrlAutoWidthMixin.__init__(self)
        
        wx.EVT_CONTEXT_MENU(self, self.ShowMenu)
        wx.EVT_LIST_COL_BEGIN_DRAG(self, -1, self.NoResize)
    
    ## ???
    #  
    #  \param event
    #        Menu event?
    def ShowMenu(self, event):
        menu = wx.Menu()
        self.ID_Add = wx.NewId()
        self.ID_Del = wx.NewId()
        
        wx.EVT_MENU(self, self.ID_Add, self.OnAdd)
        wx.EVT_MENU(self, self.ID_Del, self.OnDel)
        
        menu.Append(self.ID_Add, GT(u'Add'))
        menu.Append(self.ID_Del, GT(u'Delete'))
        menu.AppendSeparator()
        menu.Append(wx.ID_COPY)
        menu.Append(wx.ID_CUT)
        menu.Append(wx.ID_PASTE)
        
        self.PopupMenu(menu)
        menu.Destroy()
    
    def OnAdd(self, event):
        self.InsertStringItem(0, u'')
        self.SetItemBackgroundColour(0, (200,255,200))
    
    def OnDel(self, event):
        item = self.GetFocusedItem()
        self.DeleteItem(item)
    
    ## Disallows resizing of columns
    def NoResize(self, event):
        event.Veto()



# *** File/Folder Dialogs *** #

## A base class for custom file & folder dialogs
class DBDialog(wx.Dialog):
    ## Constructor
    #  
    #  \param parent
    #        Parent window
    #  \param title
    #        Text to be displayed in title bar
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE, size=(350,450))
        
#        self.SetTitle("Browse for a Folder")
        
        # IDs for context menu and buttons
        ID_Folder = 100
        ID_Rename = 101
        ID_Delete = 102
        
        
        ## Context menu
        self.menu = wx.Menu()
        self.menu.Append(ID_Folder, GT(u'New Folder'))
        self.menu.Append(ID_Rename, GT(u'Rename'))
        self.menu.AppendSeparator()
        self.menu.Append(ID_Delete, GT(u'Move to Trash'))
        
        wx.EVT_MENU(self, ID_Folder, self.CreateFolder)
        wx.EVT_MENU(self, ID_Rename, self.ShowRename)
        wx.EVT_MENU(self, ID_Delete, self.Delete)
        
#        # Display area
#        self.dir_tree = wx.GenericDirCtrl(self, -1, os.getcwd())
#        
#        # Add a context menu to the dir_tree
#        self.dir_tree.Bind(wx.EVT_CONTEXT_MENU, self.OnContext)
        
        ## New folder button
        self.New = wx.Button(self, ID_Folder, GT(u'New Folder'))
        
        ## Confirm button
        self.Ok = wx.Button(self, wx.OK)
        
        ## Cancel button
        self.Cancel = wx.Button(self, wx.CANCEL, GT(u'Cancel'))
        
        wx.EVT_BUTTON(self.New, -1, self.CreateFolder)
        wx.EVT_BUTTON(self.Ok, -1, self.OnButton)
        wx.EVT_BUTTON(self.Cancel, -1, self.OnButton)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.New, 0, wx.ALL, 5)
        button_sizer.AddSpacer(40)
        button_sizer.Add(self.Ok, 0, wx.ALL, 5)
        button_sizer.Add(self.Cancel, 0, wx.ALL, 5)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
#        self.main_sizer.Add(self.dir_tree, 1, wx.EXPAND|wx.ALL, 20)
        self.main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT, 16)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.main_sizer)
        self.Layout()
        
        
        self.value = False
        
    
    ## Defines type of dialog
    #  
    #  Dialogs can be 'open directory', 'open file', or 'save file'.
    #  \param type
    #        Dialoge type of either 'dir' or 'file'
    #  \param mode
    #        Action mode of either 'save' or 'open'
    def SetType(self, type, mode):
        if type.lower() == u'file':
            try:
                self.dir_tree = wx.GenericDirCtrl(self, -1, os.getcwd(), filter=u'*', style=wx.DIRCTRL_SHOW_FILTERS)
            except OSError:
                self.dir_tree = wx.GenericDirCtrl(self, -1, os.getenv(u'HOME'), filter=u'*', style=wx.DIRCTRL_SHOW_FILTERS)
            if mode.lower() == u'save':
                self.Ok.SetLabel(GT(u'Save'))
            elif mode.lower() == u'open':
                self.Ok.SetLabel(GT(u'Open'))
        elif type.lower() == u'dir':
            self.dir_tree = wx.GenericDirCtrl(self, -1, os.getcwd(),
                    style=wx.DIRCTRL_DIR_ONLY|wx.BORDER_SIMPLE)
            if mode.lower() == u'save':
                self.Ok.SetLabel(GT(u'Save'))
            elif mode.lower() == u'open':
                self.Ok.SetLabel(GT(u'Open'))
        
        # Add a context menu to the dir_tree
        self.dir_tree.Bind(wx.EVT_CONTEXT_MENU, self.OnContext)
        # Add to main sizer
        self.main_sizer.Insert(0, self.dir_tree, 1, wx.EXPAND|wx.ALL, 20)
    
    ## Shows the dialog window
    #  
    #  \return
    #        wx.EVT_BUTTON
    def DisplayModal(self):
        self.ShowModal()
        return self.value
    
    ## Shows a context menu
    #  
    #  \param event
    #        wx.EVT_RIGHT_DOWN???
    def OnContext(self, event):
        # Get folder/file that is highlighted
        selected = self.dir_tree.GetPath()
        
        # Show the context menu
        self.dir_tree.PopupMenu(self.menu)
    
    def GetPath(self):
        return self.dir_tree.GetPath()
        
    def OnButton(self, event):
        id = event.GetEventObject().GetId()
        
        dest_path = self.dir_tree.GetPath()
        
        if id == wx.OK:
            if os.path.isdir(dest_path):
                os.chdir(dest_path)
            else:
                os.chdir(os.path.split(dest_path)[0])
            self.value = True
        self.Close()
    
    def SetFilter(self, filter):
        self.dir_tree.SetFilter(filter)
        self.dir_tree.ReCreateTree()
    
    def CreateFolder(self, event):
        # Creates a new folder in the highlighted path
        destination = self.dir_tree.GetPath()
        
        # If highlighted path is folder, create new folder in path
        n = GT(u'New Folder')
        if os.path.isdir(destination):
            new_folder = u'{}{}'.format(destination, n)
        # If highlighted path is file, create new folder in the same directory
        else:
            parent_dir = os.path.split(destination)[0]
            new_folder = u'{}/{}'.format(parent_dir, n)
        
        folder_number = 0
        unavailable = True
        while unavailable:
            # First check to see if "New Folder" already exists in target path
            # If it does exist, create folders with numerical value "1", "2", etc.
            try:
                if not os.path.exists(new_folder):
                    os.mkdir(new_folder)
                    unavailable = False
                elif os.path.exists(new_folder):
                    folder_number += 1
                    new_folder = u'{}/{} ({})'.format(destination, n, folder_number)
            # If folder can't be created show error dialog
            except OSError:
                unavailable = False
                permission_error = wx.MessageDialog(self, GT(u'Permission Denied'), GT(u'Error'), wx.OK|wx.ICON_EXCLAMATION)
                permission_error.ShowModal()
        
        # Refresh the tree so that the new folders are dislplayed
        self.dir_tree.ReCreateTree()
        # When tree is refreshed return to new folder
        self.dir_tree.SetPath(new_folder)

    
    def Delete(self, event):
        path = self.dir_tree.GetPath()
        
        # Get the parent dir of the file/folder being deleted
        parent_path = os.path.split(path)[0]
        
        # Move file to trash
        os.system((u'gvfs-trash "{}"'.format(path)).encode(u'utf-8'))
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(parent_path)
    
    def ShowRename(self, event):
        # Get the filename to be placed in the textarea
        filename = os.path.split(self.dir_tree.GetPath())[1]
        
        # Create the rename dialog
        dia = wx.Dialog(self, -1, GT(u'Rename'), size=(200,75))
        
        # Create the input area
        input = wx.TextCtrl(dia, -1, filename)
        
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sizer.Add(input, 1)
        
        # Two buttons to confirm/cancel renaming
        button_rename = wx.Button(dia, wx.WXK_RETURN, GT(u'Rename'))
        button_cancel = wx.Button(dia, wx.WXK_ESCAPE, GT(u'Cancel'))
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddMany([(button_rename, 0, wx.ALL, 5), (button_cancel, 0, wx.ALL, 5)])
        
        # If button_rename pressed, rename file, otherwise leave as is, and close dialog
        def Rename(event):
            try:
                id = event.GetKeyCode()
            except:
                id = event.GetId()
            # Get potential name
            name = input.GetValue()
            
            # Get the selected path to folder/file
            path = self.dir_tree.GetPath()
            
            # Set the path and name
            new_name = u'{}/{}'.format(os.path.split(path)[0], name)
            
            if id == wx.WXK_RETURN or id == wx.WXK_NUMPAD_ENTER:
                if os.path.isdir(new_name) or os.path.isfile(new_name):
                    direrr = wx.MessageDialog(dia, GT(u'Name already used in current directory'), GT(u'Error'),
                                wx.OK|wx.ICON_EXCLAMATION)
                    direrr.ShowModal()
                    direrr.Close()
                else:
                    os.rename(path, new_name)
                    
                    # Return to renamed folder/file
                    self.dir_tree.ReCreateTree()
                    self.dir_tree.SetPath(new_name)
                    dia.Close()
            elif id == wx.WXK_ESCAPE:
                dia.Close()
            event.Skip()
        
        
        wx.EVT_BUTTON(button_rename, wx.WXK_RETURN, Rename)
        wx.EVT_BUTTON(button_cancel, -1, Rename)
        wx.EVT_KEY_DOWN(input, Rename)
        
        # Set layout for rename dialog
        naming_sizer = wx.BoxSizer(wx.VERTICAL)
        naming_sizer.Add(input_sizer, 1, wx.EXPAND|wx.ALL, 5)
        naming_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)
        
        dia.SetAutoLayout(True)
        dia.SetSizer(naming_sizer)
        dia.Layout()
        
        # Set focus on text area for quick renaming
        input.SetFocus()
        
        # Show the dialog
        dia.ShowModal()
        dia.Destroy()
        


class OpenDir(DBDialog):
    def __init__(self, parent, title=GT(u'Choose Directory')):
        DBDialog.__init__(self, parent, title)
        
        self.SetTitle(title)
        
        self.SetType(u'dIr', u'OpeN')
        


class OpenFile(DBDialog):
    def __init__(self, parent, title=GT(u'Open File')):
        DBDialog.__init__(self, parent, title)
        
        self.SetTitle(title)
        
        self.SetType(u'FilE', u'oPeN')
        
        # Find the wx.TreeCtrl child so events can be passed to it
        self.tree = self.dir_tree.GetChildren()[0]
        
        # Add an event handler to the tree for opening files on double-click
        wx.EVT_LEFT_DCLICK(self.tree, self.OnDClick)
    
    def OnDClick(self, event):
        path = self.dir_tree.GetPath()
        if os.path.isfile(path):
            self.OnButton(wx.OK)
        event.Skip()
        
    def OnButton(self, event):
        try:
            id = event.GetEventObject().GetId()  # Get the button that was pressed
        except AttributeError:
            id = event  # Use this if a EVT_LEFT_DCLICK is processed
        
        # Get the current selected path and (since is a file) get the parent path to return to after
        # file is selected
        path = self.dir_tree.GetPath()
        parent_path = os.path.split(path)[0]
        
        if id == wx.OK:
            # If the selected path is a file, confirm and close, otherwise try to expand the path
            if os.path.isfile(path):
                os.chdir(parent_path)
                self.value = True
                self.Close()
            elif os.path.isdir(path):
                self.dir_tree.ExpandPath(path)
        # If cancel is pressed, just close the dialog
        else:
            self.Close()


class SaveFile(DBDialog):
    def __init__(self, parent, title=GT(u'Save File'), defaultExtension=None):
        DBDialog.__init__(self, parent, title)
        
        self.defaultExtension = defaultExtension
        
        self.SetTitle(title)
        
        self.SetType(u'FILE', u'savE')
        
        # Find the wx.TreeCtrl child so events can be passed to it
        self.tree = self.dir_tree.GetChildren()[0]
        
        self.TextCtrl = wx.TextCtrl(self, -1)
        wx.EVT_KEY_DOWN(self.TextCtrl, self.OnButton)
        
        # Double-click is the same as "Save"
        wx.EVT_LEFT_DCLICK(self.tree, self.OnButton)
        
        # Put the cursor in the text control when the dialog is shown
        wx.EVT_INIT_DIALOG(self, self.OnSelfShow)
        
        # Invalid characters at beginning of filename
        self.invalid_first_char = (u' ', u'.')
        # Invalid characters in filename
        self.invalid_char = (u'/', u'\\')
        
        self.main_sizer.Insert(1, self.TextCtrl, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 20)
        
        def OnLMouseButton(event):
            path = self.dir_tree.GetPath()
            if os.path.isfile(path):
                self.SetFilename(self.dir_tree.GetPath())
            event.Skip()
        wx.EVT_LEFT_UP(self.dir_tree.GetChildren()[0], OnLMouseButton)
    
    def OnSelfShow(self, event):
        self.TextCtrl.SetFocus()
    
    def SetFilename(self, path):
        filename = os.path.split(path)[1]
        self.TextCtrl.SetValue(filename)
    
    def GetFilename(self):
        return self.TextCtrl.GetValue()
    
    def GetPath(self):
        if os.path.isdir(self.dir_tree.GetPath()):
            return u'{}/{}'.format(self.dir_tree.GetPath(), self.GetFilename())
        else:
            return u'{}/{}'.format(os.path.dirname(self.dir_tree.GetPath()), self.GetFilename())
    
    def OnButton(self, event):
        save_ids = (wx.OK, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, 7000) # 7000 is for left mouse button d-click
        cancel_ids = (wx.CANCEL, wx.WXK_ESCAPE)
        try:
            id = event.GetKeyCode()
        except AttributeError:
            id = event.GetEventObject().GetId()
        
        # Find out if the selected path is a file or directory
        if os.path.isdir(self.dir_tree.GetPath()):
            dest_path = self.dir_tree.GetPath()
        else:
            # If the path is a file, set dest_path to dir where file resides
            dest_path = os.path.split(self.dir_tree.GetPath())[0]
        
        if id in save_ids:
            filename = self.TextCtrl.GetValue()
            bad_filename_dia = wx.MessageDialog(self, GT(u'Bad File Name'), GT(u'Error'), wx.OK|wx.ICON_ERROR)
            # Check to see that the input value isn't empty
#            if self.TextCtrl.GetValue() == wx.EmptyString:
            if filename == wx.EmptyString or filename[0] in self.invalid_first_char or [i for i in list(filename) if i in self.invalid_char]:
                bad_filename_dia.ShowModal()
                #dia.Destroy()
            else:
                # If a default file extension is set add it to the filename
                if self.defaultExtension:
                    if self.TextCtrl.GetValue().split(u'.')[-1] != self.defaultExtension:
                        self.TextCtrl.SetValue(u'{}.{}'.format(self.TextCtrl.GetValue(), self.defaultExtension))
                # Set the Dir and Filename for saving
                savefile = u'{}/{}'.format(dest_path, self.TextCtrl.GetValue())
                
                # If everything checks out OK run this function
                
                save_file = True
                if os.path.exists(savefile):
                    warn = wx.MessageDialog(self, GT(u'Overwrite File?'), GT(u'File Exists'), wx.YES_NO|wx.NO_DEFAULT)
                    if warn.ShowModal() == wx.ID_NO:
                        save_file = False
                    warn.Destroy()
                
                if save_file:
                    if os.path.isdir(dest_path):
                        os.chdir(dest_path)
                    else:
                        os.chdir(os.path.split(dest_path)[0])
                    self.value = True
                    self.Close()
        elif id in cancel_ids:
            self.Close()
        event.Skip()


## Control for opening a webpage with a mouse click
#  
#  wx.HyperlinkCtrl seems to have some issues in wx 3.0,
#    so this class is used instead.
class Hyperlink(wx.Panel):
    def __init__(self, parent, ID, label, url):
        wx.Panel.__init__(self, parent, ID)
        
        self.url = url
        self.text_bg = wx.Panel(self)
        self.text = wx.StaticText(self.text_bg, label=label)
        
        self.clicked = False
        
        self.FONT_DEFAULT = self.text.GetFont()
        self.FONT_HIGHLIGHT = self.text.GetFont()
        self.FONT_HIGHLIGHT.SetUnderlined(True)
        
        wx.EVT_LEFT_DOWN(self.text, self.OnLeftClick)
        wx.EVT_ENTER_WINDOW(self.text_bg, self.OnMouseOver)
        wx.EVT_LEAVE_WINDOW(self.text_bg, self.OnMouseOut)
        
        self.text.SetForegroundColour(wx.Colour(0, 0, 255))
        
        layout_V1 = wx.BoxSizer(wx.VERTICAL)
        layout_V1.AddSpacer(1, wx.EXPAND)
        layout_V1.Add(self.text_bg, 0, wx.ALIGN_CENTER)
        layout_V1.AddSpacer(1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_V1)
        self.Layout()
    
    
    def OnLeftClick(self, event=None):
        webbrowser.open(self.url)
        
        if not self.clicked:
            self.text.SetForegroundColour(u'purple')
            self.clicked = True
        
        if event:
            event.Skip(True)
    
    
    def OnMouseOut(self, event):
        self.SetCursor(wx.NullCursor)
        self.text.SetFont(self.FONT_DEFAULT)
    
    
    def OnMouseOver(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.text.SetFont(self.FONT_HIGHLIGHT)
        
        if event:
            event.Skip(True)
    
    
    def SetDefaultFont(self, font):
        self.FONT_DEFAULT = font
    
    
    def SetHighlightFont(self, font):
        self.FONT_HIGHLIGHT = font
