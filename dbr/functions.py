# -*- coding: utf-8 -*-

## \package dbr.functions
#  Global functions used throughout Debreate


# System imports
from os import popen
from datetime import datetime, date
import os, subprocess
from urllib2 import urlopen, URLError

# wx imports
from wx import \
    SafeYield as wxSafeYield, \
    FileDialog as wxFileDialog
from wx import \
    MAJOR_VERSION as wxMAJOR_VERSION, \
    FD_SAVE as wxFD_SAVE, \
    FD_CHANGE_DIR as wxFD_CHANGE_DIR, \
    FD_OVERWRITE_PROMPT as wxFD_OVERWRITE_PROMPT, \
    ID_OK as wxID_OK

# Debreate imports
from dbr.constants import \
    HOMEPAGE, PY_VER_STRING
from dbr.custom import SaveFile
from dbr.constants import DEBUG, system_licenses_path


## Get the current version of the application
#  
#  The alias \p \e \b dbr.GetCurrentVersion can be used.
#  \return
#        Application's version tuple
#  
#  \b Alias: \e dbr.GetCurrentVersion
def GetCurrentVersion():
    try:
        request = urlopen(u'{}/current.txt'.format(HOMEPAGE))
        version = request.readlines()[0]
        version = version.split(u'.')
        
        if (u'\n' in version[-1]):
            # Remove newline character
            version[-1] = version[-1][:-1]
        
        # Convert to integer
        for v in range(0, len(version)):
            version[v] = int(version[v])
        
        # Change container to tuple and return it
        version = (version[0], version[1], version[2])
        return version
    
    except URLError, err:
        #err = unicode(err)
        return err


## Checks if a field (or widget) is enabled
#  
#  This is used for compatibility between wx 2.8 & 3.0.
#    3.0 uses the method 'IsThisEnabled()' rather than
#    'IsEnabled()' to get the 'intrinsic' status of the
#    widget.
#  \param field
#        The widget (wxWindow) to be checked
#  
#  \b Alias: \e dbr.FieldEnabled
def FieldEnabled(field):
    # wx 3.0 must use 'IsThisEnabled' to get 'intrinsic' status in case parent is disabled
    if wxMAJOR_VERSION > 2:
        return field.IsThisEnabled()
    else:
        return field.IsEnabled()


## Execute a command with sudo (super user) privileges
#  
#  \param password
#        Password of the current user's login session
#  \param command
#        The command to be run with elevated/super user privileges
#  
#  \b Alias: \e dbr.RunSudo
def RunSudo(password, command):
    command = u'echo {} | sudo -S {} ; echo $?'.format(password, command)
    wxSafeYield()
    output = popen(command).read()
    err = int(output.split(u'\n')[-2])
    if (err):
        return False
    return True

## Checks if a specified executable can be executed on the system
#  
#  FIXME: This function is currently not used anywhere in the code
#  \param command:
#        The command to be checked
#  \rtype bool
#  
#  \b Alias: \e dbr.CommandExists
def CommandExists(command):
    try:
        subprocess.Popen(command.split(u' ')[0].split(u' '))
        exists = True
        print u'First subprocess: {}'.format(exists)
    except OSError:
        exists = os.path.isfile(command)
        print u'os.path: {}'.format(exists)
        if exists:
            subprocess.Popen((command))
            print u'Second subprocess: {}'.format(exists)
    return exists

## Checks if the system is using a specific version of Python
#  
#  FIXME: This function is currently not used anywhere in the code
#  \param version
#        The minimal version that should be required
#  
#  \b Alias: \e dbr.RequirePython
def RequirePython(version):
    error = u'Incompatible python version'
    t = type(version)
    if t == type(u''):
        if version == PY_VER_STRING[0:3]:
            return
        raise ValueError(error)
    elif t == type([]) or t == type(()):
        if PY_VER_STRING[0:3] in version:
            return
        raise ValueError(error)
    raise ValueError(u'Wrong type for argument 1 of RequirePython(version)')

## Checks if a text string is empty
#  
#  \param text
#        The string to be checked
#  
#  \b Alias: \e dbr.TextIsEmpty
def TextIsEmpty(text):
    text = u''.join(u''.join(text.split(u' ')).split(u'\n'))
    return (text == u'')



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
def GetFileSaveDialog(main_window, title, ext_filter, default_extension=None):
    if DEBUG:
        print(u'DEBUG: Getting file save dialog')
    
    if main_window.cust_dias.IsChecked():
        file_save = SaveFile(main_window, title, default_extension)
        file_save.SetFilter(ext_filter)
    else:
        file_save = wxFileDialog(main_window, title, os.getcwd(), u'', ext_filter,
                wxFD_SAVE|wxFD_CHANGE_DIR|wxFD_OVERWRITE_PROMPT)
    
    return file_save


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
#    'True' if the dialog's return value is 'wx.ID_OK', 'False'
#      otherwise
#  
#  \b Alias: \e dbr.ShowDialog
def ShowDialog(main_window, dialog):
    if DEBUG:
        print(u'DEBUG: Showing dialog')
    
    if main_window.cust_dias.IsChecked():
        return dialog.DisplayModal()
    else:
        return dialog.ShowModal() == wxID_OK


def prepend_zero(number):
    if number < 10:
        return str(u'0{}'.format(number))
    
    return str(number)


## Retrieves the current year
#  
#  \return
#        String value of the current year
def GetYear():
    return date.today().year

def GetDate():
    yr = str(GetYear())
    mo = prepend_zero(date.today().month)
    da = prepend_zero(date.today().day)
    
    return u'{}-{}-{}'.format(yr, mo, da)


def GetTime(formatted=False):
    c_time = datetime.now().time()
    hr = prepend_zero(c_time.hour)
    mn = prepend_zero(c_time.minute)
    se = prepend_zero(c_time.second)
    ms = c_time.microsecond
    
    # FIXME: Want to show only microseconds (ms[2:])
    ms = str(ms)
    
    s_time = u'{}:{}:{}:{}'.format(hr, mn, se, ms)
    
    if formatted:
        s_time = s_time.replace(u':', u'.')
    
    return s_time


## Formats the time for outputting to filename
#  
#  \param s_time
#        \b \e str : String representation of the time
def FormatTime(s_time):
    return s_time.replace(u':', u'.')


## Retrieves a list of licenses installed on the system
#  
#  Common system license files are located in /usr/share/common-licenses.
def GetSystemLicensesList():
    license_list = []
    
    for PATH, DIRS, FILES in os.walk(system_licenses_path):
        for F in FILES:
            if os.path.isfile(u'{}/{}'.format(system_licenses_path, F)):
                license_list.append(F)
    
    return license_list
