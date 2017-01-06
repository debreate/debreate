# -*- coding: utf-8 -*-

## \package globals.system

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from globals.fileio     import ReadFile
from globals.remote     import GetRemotePageText
from globals.strings    import RemoveEmptyLines


# *** Python Info *** #

PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = u'{}.{}.{}'.format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


# *** wxWidgets Info *** #

WX_VER_STRING = u'{}.{}.{}'.format(wx.MAJOR_VERSION, wx.MINOR_VERSION, wx.RELEASE_VERSION)


# *** Operating System Info *** #

def GetOSInfo(key, upstream=False):
    lsb_release = u'/etc/lsb-release'
    
    if upstream:
        lsb_release = u'/etc/upstream-release/lsb-release'
    
    if not os.path.isfile(lsb_release):
        return None
    
    release_data = ReadFile(lsb_release, split=True)
    
    value = None
    
    for L in release_data:
        if L.startswith(key):
            value = L.replace(u'{}='.format(key), u'').replace(u'"', u'')
            break
    
    return value


OS_name = GetOSInfo(u'DISTRIB_ID')
OS_version = GetOSInfo(u'DISTRIB_RELEASE')
OS_codename = GetOSInfo(u'DISTRIB_CODENAME')

OS_upstream_name = GetOSInfo(u'DISTRIB_ID', True)
OS_upstream_version = GetOSInfo(u'DISTRIB_RELEASE', True)
OS_upstream_codename = GetOSInfo(u'DISTRIB_CODENAME', True)


def _get_debian_distname():
    ref_site = u''
    
    code_names = []
    
    return sorted(code_names)


def _get_ubuntu_distname(nonexistent=False):
    ref_site = u'https://wiki.ubuntu.com/Releases'
    
    code_names = []
    
    page_text = GetRemotePageText(ref_site).split(u'\n')
    
    for INDEX in range(len(page_text)):
        if page_text[INDEX] == u'<h3 id="Current">Current</h3>':
            page_text = page_text[INDEX+1:]
            break
    
    for INDEX in range(len(page_text)):
        if page_text[INDEX] == u'<h3 id="End_of_life">End of life</h3>':
            page_text = page_text[:INDEX]
            break
    
    delim = u'<td style="background-color: #f1f1dd"><p class="line891"><a '
    
    for LINE in page_text:
        LINE = LINE.strip()
        
        if LINE.startswith(delim) and u'ReleaseNotes' not in LINE:
            LINE = LINE.replace(delim, u'')
            
            add_line = LINE.startswith(u'href=')
            if nonexistent:
                add_line = add_line or LINE.startswith(u'class="nonexistent"')
            
            if add_line:
                index_start = LINE.index(u'>')
                index_end = LINE.index(u'<')
                
                LINE = LINE[index_start+1:index_end].lower().strip()
                
                if u' ' in LINE:
                    LINE = LINE.split(u' ')[0]
                
                if LINE not in code_names:
                    code_names.append(LINE)
    
    return sorted(code_names)


def _get_mint_distname():
    ref_site = u''
    
    code_names = []
    
    return sorted(code_names)


## Get a list of available system release codenames
def GetOSDistNames():
    code_names = []
    
    if not code_names:
        # Ubuntu & Linux Mint distributions
        global OS_codename, OS_upstream_codename
        
        for CN in (OS_codename, OS_upstream_codename,):
            if CN and CN not in code_names:
                code_names.append(CN)
    
    # Debian distributions
    FILE_debian = u'/etc/debian_version'
    if os.path.isfile(FILE_debian):
        debian_names = RemoveEmptyLines(ReadFile(FILE_debian, split=True))[:1]
        
        # Usable names should all be on first line
        if u'/' in debian_names[0]:
            debian_names = sorted(debian_names[0].split(u'/'))
        
        # Add generic Debian release names
        debian_names = debian_names + [u'stable', u'testing', u'unstable',]
        
        # Put Debian names first
        code_names = debian_names + code_names
    
    return tuple(code_names)
