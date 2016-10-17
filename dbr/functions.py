# -*- coding: utf-8 -*-

## \package dbr.functions
#  
#  Global functions used throughout Debreate


from datetime   import date
from datetime   import datetime
import os, re, commands, shutil
from urllib2    import URLError
from urllib2    import urlopen
import wx

from dbr.constants          import system_licenses_path
from globals.application    import APP_homepage
from globals.application    import APP_name
from globals.application    import VERSION_string
from globals.errorcodes     import dbrerrno
from globals.system         import PY_VER_STRING


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
        request = urlopen(u'{}/current.txt'.format(APP_homepage))
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
            
            if isinstance(I, (tuple, list)):
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


def GetFileMimeType(file_name):
    output = commands.getstatusoutput(u'file --mime-type "{}"'.format(file_name))
    
    if output[0]:
        return (output[0], output[1])
    
    return output[1].split(u': ')[-1]


def SetToolTip(control, tooltip):
    control.SetToolTip(wx.ToolTip(tooltip))


def SetToolTips(control_list):
    for C in control_list:
        SetToolTip(C[0], C[1])


def BuildBinaryPackageFromTree(root_dir, filename):
    if not os.path.isdir(root_dir):
        return dbrerrno.ENOENT
    
    # DEBUG
    cmd = u'fakeroot dpkg-deb -v -b "{}" "{}"'.format(root_dir, filename)
    print(u'DEBUG: Issuing command: {}'.format(cmd))
    
    #output = commands.getstatusoutput(cmd)
    
    return 0


def CreateTempDirectory():
    temp_dir = u'/tmp'
    
    # Check if we can write to /tmp
    if not os.access(temp_dir, os.W_OK):
        temp_dir = os.getcwd()
    
    temp_dir = u'{}/{}-{}_temp'.format(temp_dir, unicode(APP_name).lower(), VERSION_string)
    
    if os.access(os.path.dirname(temp_dir), os.W_OK):
        # Start with fresh directory
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        
        elif os.path.isfile(temp_dir):
            return dbrerrno.EACCES
        
        os.makedirs(temp_dir)
        return temp_dir
    
    return dbrerrno.EACCES


def RemoveTempDirectory(temp_dir):
    if os.access(temp_dir, os.W_OK):
        shutil.rmtree(temp_dir)


def RemovePreWhitespace(text):
    text_lines = text.split(u'\n')
    
    remove_lines = 0
    
    for L in text_lines:
        if not TextIsEmpty(L):
            break
        
        remove_lines += 1
    
    return u'\n'.join(text_lines[remove_lines:])
