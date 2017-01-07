# -*- coding: utf-8 -*-

## \package globals.system

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from globals.fileio     import ReadFile
from globals.fileio     import WriteFile
from globals.paths      import ConcatPaths
from globals.paths      import PATH_local
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

## File where distribution code names cache is stored
FILE_distnames = ConcatPaths((PATH_local, u'distnames'))

def _get_debian_stable_distname():
    ref_site = u'https://wiki.debian.org/DebianReleases'
    
    stable_name = u''
    
    return stable_name


def _get_ubuntu_distnames(nonexistent=False):
    ref_site = u'https://wiki.ubuntu.com/Releases'
    
    dist_names = []
    
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
                
                if LINE not in dist_names:
                    dist_names.append(LINE)
    
    return sorted(dist_names)


def _get_mint_distnames():
    ref_site = u'https://www.linuxmint.com/download_all.php'
    
    dist_names = []
    
    return sorted(dist_names)


## Creates/Updates list of distribution names stored in user's local directory
#  
#  \param deprecated
#    If \b \e True, includes obsolete Ubuntu distributions
#  \return
#    \b \e Boolean value of WriteFile
def UpdateDistNamesCache(deprecated=False):
    global FILE_distnames
    
    debian_stable_distname = _get_debian_stable_distname()
    ubuntu_distnames = _get_ubuntu_distnames(deprecated)
    mint_distnames = _get_mint_distnames()
    
    section_debian = u'[DEBIAN]\n{}'.format(debian_stable_distname)
    section_ubuntu = u'[UBUNTU]\n{}'.format(u'\n'.join(ubuntu_distnames))
    section_mint = u'[LINUX MINT]\n{}'.format(u'\n'.join(mint_distnames))
    
    return WriteFile(FILE_distnames, u'\n\n'.join((section_debian, section_ubuntu, section_mint)))


## Get a list of available system release codenames
def GetOSDistNames():
    dist_names = []
    
    if not dist_names:
        # Ubuntu & Linux Mint distributions
        global OS_codename, OS_upstream_codename
        
        for CN in (OS_codename, OS_upstream_codename,):
            if CN and CN not in dist_names:
                dist_names.append(CN)
    
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
        dist_names = debian_names + dist_names
    
    return tuple(dist_names)
