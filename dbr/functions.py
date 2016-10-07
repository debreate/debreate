# -*- coding: utf-8 -*-

## \package dbr.functions
#  Global functions used throughout Debreate


# System modules
import wx, os, subprocess, re
from datetime import datetime, date
from urllib2 import urlopen, URLError

# Local modules
import dbr
from dbr.constants import \
    HOMEPAGE, PY_VER_STRING, system_licenses_path,\
    project_wildcards, supported_suffixes
from dbr.compression import compression_formats


# FIXME: Can't import Logger

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
#  This is used for compatibility between wx. 2.8 & 3.0.
#    3.0 uses the method 'IsThisEnabled()' rather than
#    'IsEnabled()' to get the 'intrinsic' status of the
#    widget.
#  \param field
#        The widget (wx.Window) to be checked
#  
#  \b Alias: \e dbr.FieldEnabled
def FieldEnabled(field):
    # wx. 3.0 must use 'IsThisEnabled' to get 'intrinsic' status in case parent is disabled
    if wx.MAJOR_VERSION > 2:
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
    wx.SafeYield()
    output = os.popen(command).read()
    err = int(output.split(u'\n')[-2])
    if (err):
        return False
    return True

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
def GetFileSaveDialog(main_window, title, ext_filters, default_extension=None):
    ext_filters = u'|'.join(ext_filters)
    if main_window.cust_dias.IsChecked():
        file_save = dbr.SaveFile(main_window, title, default_extension)
        file_save.SetFilter(ext_filters)
    else:
        file_save = wx.FileDialog(main_window, title, defaultDir=os.getcwd(), wildcard=ext_filters,
                style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
    
    return file_save


def GetFileOpenDialog(main_window, title, ext_filters, default_extension=None):
    ext_filters = u'|'.join(ext_filters)
    if main_window.cust_dias.IsChecked():
        file_open = dbr.OpenFile(main_window, title, default_extension)
        file_open.SetFilter(ext_filters)
    
    else:
        file_open = wx.FileDialog(main_window, title, defaultDir=os.getcwd(), wildcard=ext_filters,
                style=wx.FD_OPEN|wx.FD_CHANGE_DIR)
    
    return file_open


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
def ShowDialog(main_window, dialog):
    if main_window.cust_dias.IsChecked():
        return dialog.DisplayModal()
    else:
        return dialog.ShowModal() == wx.ID_OK


# FIXME: time.strftime can be used for all date & time functions

def prepend_zero(number):
    if number < 10:
        return unicode(u'0{}'.format(number))
    
    return unicode(number)


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


## Checks if a string contains any alphabetic characters
#  
#  \param
#        \b \e unicode|str : String to check
#  \return
#        \b \e bool : Alphabet characters found
def HasAlpha(value):
    return (re.search(u'[a-zA-Z]', unicode(value)) != None)
    
## Finds integer value from a string, float, tuple, or list
#  
#  \param value
#        Value to be checked for integer equivalent
#  \return
#        \b \e int|None
def GetInteger(value):
    v_type = type(value)
    
    if v_type in (int, float):
        return int(value)
    
    # Will always use there very first value, even for nested items
    elif v_type in (tuple, list):
        # Recursive check lists & tuples
        return GetInteger(value[0])
    
    elif v_type in (unicode, str):
        # Convert because of unsupported methods in str class
        value = unicode(value)
        
        if HasAlpha(value):
            return None
        
        if value == wx.EmptyString:
            return None
        
        # Check for negative
        if value[0] == u'-':
            if value.count(u'-') <= 1:
                value = GetInteger(value[1:])
                
                if value != None:
                    return -value
        
        # Check for tuple
        elif u'.' in value:
            value = value.split(u'.')[0]
            return GetInteger(value)
        
        elif value.isnumeric() or value.isdigit():
            return int(value)
    
    return None


## Finds a boolean value from a string, integer, float, or boolean
#  
#  \param value
#        Value to be checked for boolean equivalent
#  \return
#        \b \e bool|None
def GetBoolean(value):
    v_type = type(value)
    
    if v_type == bool:
        return value
    
    elif v_type in (int, float):
        return bool(value)
    
    elif v_type in (unicode, str):
        int_value = GetInteger(value)
        if int_value != None:
            return bool(int_value)
        
        if value in (u'True', u'False'):
            return value == u'True'
    
    return None


## Finds a tuple value from a string, tuple, or list
#  
#  \param value
#        Value to be checked for tuple equivalent
#  \return
#        \b \e tuple|None
def GetIntTuple(value):
    v_type = type(value)
    
    if (v_type in (tuple, list)) and (len(value) > 1):
        # Convert to list in case we need to make changes
        value = list(value)
        
        for I in value:
            t_index = value.index(I)
            
            if type(I) in (tuple, list):
                I = GetIntTuple(I)
            
            else:
                I = GetInteger(I)
            
            if I == None:
                return None
            
            value[t_index] = I
            
            '''
            if type(I) not in (int, float):
                return None
            
            # Convert float values to int
            if type(I) == float:
                value[t_index] = int(I)
            '''
        
        return tuple(value)
    
    elif v_type in (unicode, str):
        # Remove whitespace & braces
        for D in u' ', u'(', u')':
            value = u''.join(value.split(D))
        
        value = value.split(u',')
        
        if len(value) >= 2:
            for S in value:
                v_index = value.index(S)
                
                S = GetInteger(S)
                
                if S == None:
                    return None
                '''
                # Check for float values
                if u'.' in S:
                    # Remove trailing values after 2nd period
                    S = S.split(u'.')[:2]
                    
                    for C in S:
                        if (not C.isnumeric() and (not C.isdigit())):
                            return None
                    
                    S = float(u'.'.join(S))
                
                elif (not S.isnumeric()) and (not S.isdigit()):
                    return None
                '''
                value[v_index] = S
                
            # Convert return value from list to tuple
            return tuple(value)
        
    return None


def IsInteger(value):
    return GetInteger(value) != None

def IsBoolean(value):
    return GetBoolean(value) != None

def IsIntTuple(value):
    return GetIntTuple(value) != None

def GetCompressionId(z_value):
    for z_id in compression_formats:
        if z_value == compression_formats[z_id]:
            return z_id
    
    # FIXME: Can't import Logger
    #Logger.Debug(__name__, GT(u'Compression ID not found for "{}" value'.format(z_value)))
    
    return None


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
