# -*- coding: utf-8 -*-

## \package dbr.functions
#  
#  Global functions used throughout Debreate

# MIT licensing
# See: docs/LICENSE.txt


import commands, os, re, traceback, subprocess, wx
from datetime   import date
from datetime   import datetime
from urllib2    import URLError
from urllib2    import urlopen

from dbr.language           import GT
from globals.application    import APP_project_gh
from globals.application    import VERSION_dev
from globals.constants      import system_licenses_path
from globals.dateinfo       import GetYear
from globals.errorcodes     import dbrerrno
from globals.execute        import GetExecutable
from globals.strings        import GS
from globals.strings        import IsString
from globals.strings        import StringIsNumeric
from globals.strings        import TextIsEmpty
from globals.system         import PY_VER_STRING


## Get the current version of the application
#  
#  \param remote
#    Website URL to parse for update
#  \return
#        Application's version tuple
def GetCurrentVersion(remote=APP_project_gh):
    try:
        version = os.path.basename(urlopen(u'{}/releases/latest'.format(remote)).geturl())
        
        if u'-' in version:
            version = version.split(u'-')[0]
        version = version.split(u'.')
        
        cutoff_index = 0
        for C in version[0]:
            if not C.isdigit():
                cutoff_index += 1
                continue
            
            break
        
        version[0] = version[0][cutoff_index:]
        for V in version:
            if not V.isdigit():
                return u'Cannot parse release: {}'.format(tuple(version))
            
            version[version.index(V)] = int(V)
        
        return tuple(version)
    
    except URLError, err:
        return err


## TODO: Doxygen
def GetContainerItemCount(container):
    if wx.MAJOR_VERSION > 2:
        return container.GetItemCount()
    
    return len(container.GetChildren())


## TODO: Doxygen
def GetLongestLine(lines):
    if isinstance(lines, (unicode, str)):
        lines = lines.split(u'\n')
    
    longest = 0
    
    for LI in lines:
        l_length = len(LI)
        if l_length > longest:
            longest = l_length
    
    return longest


## Checks if the system is using a specific version of Python
#  
#  FIXME: This function is currently not used anywhere in the code
#  \param version
#        The minimal version that should be required
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


## TODO: Doxygen
#  
#  FIXME: time.strftime can be used for all date & time functions
def prepend_zero(number):
    if number < 10:
        return GS(u'0{}'.format(number))
    
    return GS(number)


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
    
    return sorted(license_list)


## Checks if a string contains any alphabetic characters
#  
#  \param
#        \b \e unicode|str : String to check
#  \return
#        \b \e bool : Alphabet characters found
def HasAlpha(value):
    return (re.search(u'[a-zA-Z]', GS(value)) != None)


## Finds integer value from a string, float, tuple, or list
#  
#  \param value
#        Value to be checked for integer equivalent
#  \return
#        \b \e int|None
def GetInteger(value):
    if isinstance(value, (int, float,)):
        return int(value)
    
    # Will always use there very first value, even for nested items
    elif isinstance(value,(tuple, list,)):
        # Recursive check lists & tuples
        return GetInteger(value[0])
    
    elif value and IsString(value):
        # Convert because of unsupported methods in str class
        value = GS(value)
        
        if HasAlpha(value):
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
        
        elif StringIsNumeric(value):
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
    if isinstance(value, (tuple, list,)):
        if len(value) > 1:
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
            
            return tuple(value)
    
    elif IsString(value):
        # Remove whitespace & braces
        value = value.strip(u' ()')
        value = u''.join(value.split(u' '))
        
        value = value.split(u',')
        
        if len(value) > 1:
            for S in value:
                v_index = value.index(S)
                
                S = GetInteger(S)
                
                if S == None:
                    return None
                
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


## Checks if file is binary & needs stripped
#  
#  FIXME: Handle missing 'file' command
def FileUnstripped(file_name):
    CMD_file = GetExecutable(u'file')
    
    if CMD_file:
        output = commands.getoutput(u'{} "{}"'.format(CMD_file, file_name))
        
        if u': ' in output:
            output = output.split(u': ')[1]
        
        output = output.split(u', ')
        
        if u'not stripped' in output:
            return True
        
        return False
    
    print(u'ERROR: "file" command does not exist on system')
    
    return False


def BuildBinaryPackageFromTree(root_dir, filename):
    if not os.path.isdir(root_dir):
        return dbrerrno.ENOENT
    
    # DEBUG
    cmd = u'fakeroot dpkg-deb -v -b "{}" "{}"'.format(root_dir, filename)
    print(u'DEBUG: Issuing command: {}'.format(cmd))
    
    #output = commands.getstatusoutput(cmd)
    
    return 0


def RemovePreWhitespace(text):
    text_lines = text.split(u'\n')
    
    remove_lines = 0
    
    for L in text_lines:
        if not TextIsEmpty(L):
            break
        
        remove_lines += 1
    
    return u'\n'.join(text_lines[remove_lines:])


def UsingDevelopmentVersion():
    return VERSION_dev != 0


def BuildDebPackage(stage_dir, target_file):
    packager = GetExecutable(u'dpkg-deb')
    fakeroot = GetExecutable(u'fakeroot')
    
    if not fakeroot or not packager:
        return (dbrerrno.ENOENT, GT(u'Cannot run "fakeroot dpkg"'))
    
    packager = os.path.basename(packager)
    
    try:
        output = subprocess.check_output([fakeroot, packager, u'-b', stage_dir, target_file], stderr=subprocess.STDOUT)
    
    except:
        return (dbrerrno.EAGAIN, traceback.format_exc())
    
    return (dbrerrno.SUCCESS, output)


## Check if mouse is within the rectangle area of a window
def MouseInsideWindow(window):
    # Only need to find size because ScreenToClient method gets mouse pos
    # relative to window.
    win_size = window.GetSizeTuple()
    mouse_pos = window.ScreenToClient(wx.GetMousePosition())
    
    # Subtracting from width & height compensates for visual boundaries
    inside_x = 0 <= mouse_pos[0] <= win_size[0]-4
    inside_y = 0 <= mouse_pos[1] <= win_size[1]-3
    
    return inside_x and inside_y
