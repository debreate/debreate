# -*- coding: utf-8 -*-


import os, subprocess
from os import popen
from urllib2 import urlopen, URLError

from wx import \
    MAJOR_VERSION as wxMAJOR_VERSION, \
    SafeYield as wxSafeYield

from dbr.constants import \
    HOMEPAGE, PY_VER_STRING


def GetCurrentVersion():
    try:
        request = urlopen(u'%s/current.txt' % (HOMEPAGE))
        version = request.readlines()[0]
        version = version.split('.')
        
        if ('\n' in version[-1]):
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


# Compatibility function for wx 3.0
def FieldEnabled(field):
    # wx 3.0 must use 'IsThisEnabled' to get 'intrinsic' status in case parent is disabled
    if wxMAJOR_VERSION > 2:
        return field.IsThisEnabled()
    else:
        return field.IsEnabled()


### -*- Execute commands with sudo privileges -*- ###
def RunSudo(password, command):
    command = u'echo %s | sudo -S %s ; echo $?' % (password, command)
    wxSafeYield()
    output = popen(command).read()
    err = int(output.split(u'\n')[-2])
    if (err):
        return False
    return True

### -*- Function to check for installed executables -*- ###
# FIXME: Unused
def CommandExists(command):
    try:
        subprocess.Popen(command.split(u' ')[0].split(u' '))
        exists = True
        print u'First subprocess: %s' % (exists)
    except OSError:
        exists = os.path.isfile(command)
        print u'os.path: %s' % (exists)
        if exists:
            subprocess.Popen((command))
            print u'Second subprocess: %s' % (exists)
    return exists

# FIXME: Unused
def RequirePython(version):
    error = 'Incompatible python version'
    t = type(version)
    if t == type(''):
        if version == PY_VER_STRING[0:3]:
            return
        raise ValueError(error)
    elif t == type([]) or t == type(()):
        if PY_VER_STRING[0:3] in version:
            return
        raise ValueError(error)
    raise ValueError('Wrong type for argument 1 of RequirePython(version)')
