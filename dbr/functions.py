# -*- coding: utf-8 -*-


from urllib2 import urlopen

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

