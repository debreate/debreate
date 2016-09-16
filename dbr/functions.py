# -*- coding: utf-8 -*-


from os import popen
from urllib2 import urlopen, URLError

from wx import \
    MAJOR_VERSION as wxMAJOR_VERSION, \
    SafeYield as wxSafeYield

from dbr.constants import HOMEPAGE


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
