# -*- coding: utf-8 -*-

## \package globals.system

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from globals.containers import Contains
from globals.fileio     import ReadFile
from globals.fileio     import WriteFile
from globals.paths      import ConcatPaths
from globals.paths      import PATH_cache
from globals.remote     import GetRemotePageText
from globals.strings    import RemoveEmptyLines
from globals.strings    import StringIsVersioned


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
FILE_distnames = ConcatPaths((PATH_cache, u'distnames'))

## Retrieves distribution names from remote Debian site
#  
#  NOTE: If site layout changes, function will need updated
#  \param obsolete
#    Include obsolete distributions
#  \param unstable
#    Include testing & unstable distributions
#  \param generic
#    Include generic names 'oldstable', 'stable', 'testing', & 'unstable'
def _get_debian_distnames(unstable=True, obsolete=False, generic=False):
    ref_site = u'https://wiki.debian.org/DebianReleases'
    
    # Names added statically are continually used by Debian project
    dist_names = []
    
    if generic:
        if unstable:
            dist_names.append(u'unstable')
            dist_names.append(u'testing')
        
        dist_names.append(u'stable')
        
        if obsolete:
            dist_names.append(u'oldstable')
    
    # NOTE: 'stretch' & 'sid' names are repeatedly used for testing & unstable,
    #       but this could change in the future.
    if unstable:
        dist_names.append(u'sid')
        dist_names.append(u'stretch')
    
    page_html = GetRemotePageText(ref_site).split(u'\n')
    
    if page_html:
        # Only add up to max_dists to list
        max_dists = 6
        dists_added = 0
        
        for INDEX in range(len(page_html)):
            LINE = page_html[INDEX].lower()
            
            if u'<p class="line862">' in LINE and LINE.strip().endswith(u'</td>'):
                stable_version = LINE.split(u'</td>')[0].split(u'>')[-1].strip()
                
                if StringIsVersioned(stable_version):
                    dist_names.append(page_html[INDEX+1].split(u'</a>')[0].split(u'>')[-1].lower().strip())
                    dists_added += 1
                    
                    if dists_added >= max_dists:
                        break
                    
                    # First name found should be current stable version
                    if not obsolete:
                        break
    
    return dist_names


## Retrieves distribution names from remote Ubuntu site
#  
#  NOTE: If site layout changes, function will need updated
def _get_ubuntu_distnames(unstable=True, obsolete=False):
    ref_site = u'https://wiki.ubuntu.com/Releases'
    page_html = GetRemotePageText(ref_site).split(u'\n')
    
    dist_names = []
    current = []
    
    if unstable:
        future = []
    
    if obsolete:
        eol = []
    
    if page_html:
        for INDEX in range(len(page_html)):
            LINE = page_html[INDEX].lower()
            
            if u'id="current"' in LINE and len(current) < 2:
                current.append(INDEX + 8)
                
                continue
            
            if u'id="future"' in LINE:
                if len(current) < 2:
                    current.append(INDEX)
                
                if unstable and len(future) < 2:
                    future.append(INDEX + 8)
                
                continue
            
            if u'id="end_of_life"' in LINE:
                if unstable and len(future) < 2:
                    future.append(INDEX)
                
                if obsolete and len(eol) < 2:
                    eol.append(INDEX + 8)
                    eol.append(len(page_html) - 1)
                    
                    break
        
        # Lines containing these strings will be ignored
        skip_lines = (
            u'releasenotes',
            u'class="http',
            )
        
        # Add names in order of newest first
        
        if unstable and len(future) > 1:
            future = page_html[future[0]:future[1]]
            
            for LINE in future:
                LINE = LINE.lower()
                
                if u'class="line891"' in LINE and not Contains(LINE, skip_lines):
                    name = LINE.split(u'</a>')[0].split(u'>')[-1].strip().split(u' ')[0]
                    
                    if name and name not in dist_names:
                        dist_names.append(name)
        
        if len(current) > 1:
            current = page_html[current[0]:current[1]]
            
            for LINE in current:
                LINE = LINE.lower()
                
                if u'class="line891"' in LINE and not Contains(LINE, skip_lines):
                    name = LINE.split(u'</a>')[0].split(u'>')[-1].strip().split(u' ')[0]
                    if name and name not in dist_names:
                        dist_names.append(name)
        
        if obsolete and len(eol) > 1:
            eol = page_html[eol[0]:eol[1]]
            
            # Maximum number of obsolete dists that will be added
            eol_max = 6
            eol_added = 0
            
            for LINE in eol:
                LINE = LINE.lower()
                
                if u'class="line891"' in LINE and not Contains(LINE, skip_lines):
                    name = LINE.split(u'</a>')[0].split(u'>')[-1].strip().split(u' ')[0]
                    
                    if name and name not in dist_names:
                        dist_names.append(name)
                        
                        eol_added += 1
                        if eol_added >= eol_max:
                            break
    
    return dist_names


## Retrieves distribution names from remote Linux Mint site
#  
#  NOTE: If site layout changes, function will need updated
def _get_mint_distnames():
    ref_site = u'https://www.linuxmint.com/download_all.php'
    page_html = GetRemotePageText(ref_site).split(u'\n')
    
    dist_names = []
    
    if page_html:
        for INDEX in range(len(page_html)):
            LINE = page_html[INDEX].lower()
            
            if u'href="release.php?id=' in LINE:
                name = LINE.split(u'</a>')[0].split(u'>')[-1].strip()
                
                if name and not StringIsVersioned(name) and name not in dist_names:
                    dist_names.append(name)
    
    return dist_names


## Creates/Updates list of distribution names stored in user's local directory
#  
#  \param deprecated
#    If \b \e True, includes obsolete Ubuntu distributions
#  \return
#    \b \e Boolean value of WriteFile
def UpdateDistNamesCache(unstable=True, obsolete=False, generic=False):
    global FILE_distnames
    
    debian_distnames = _get_debian_distnames(unstable, obsolete, generic)
    ubuntu_distnames = _get_ubuntu_distnames(unstable, obsolete)
    mint_distnames = _get_mint_distnames()
    
    section_debian = u'[DEBIAN]\n{}'.format(u'\n'.join(debian_distnames))
    section_ubuntu = u'[UBUNTU]\n{}'.format(u'\n'.join(ubuntu_distnames))
    section_mint = u'[LINUX MINT]\n{}'.format(u'\n'.join(mint_distnames))
    
    return WriteFile(FILE_distnames, u'\n\n'.join((section_debian, section_ubuntu, section_mint)))


## Retrieves distribution names from cache file
#  
#  \param deprecated
#    If \b \e True, includes obsolete Ubuntu distributions (only works if cache file doesn't already exist)
#  \return
#    ???
def GetCachedDistNames(unstable=True, obsolete=False, generic=False):
    global FILE_distnames
    
    if not os.path.isfile(FILE_distnames):
        if not UpdateDistNamesCache(unstable, obsolete, generic):
            return None
    
    text_temp = ReadFile(FILE_distnames)
    
    dist_names = {}
    
    if text_temp:
        try:
            dist_names[u'debian'] = RemoveEmptyLines(text_temp.split(u'[DEBIAN]')[1].split(u'[UBUNTU]')[0].split(u'\n'))
        
        except IndexError:
            pass
        
        try:
            dist_names[u'ubuntu'] = RemoveEmptyLines(text_temp.split(u'[UBUNTU]')[1].split(u'[LINUX MINT]')[0].split(u'\n'))
        
        except IndexError:
            pass
        
        try:
            dist_names[u'mint'] = RemoveEmptyLines(text_temp.split(u'[LINUX MINT]')[1].split(u'\n'))
        
        except IndexError:
            pass
    
    return (dist_names)


## Get a list of available system release codenames
#  
#  FIXME: unstable, obsolete, & generic names should only be added if specified
def GetOSDistNames():
    global FILE_distnames
    
    dist_names = []
    
    if os.path.isfile(FILE_distnames):
        cached_names = GetCachedDistNames()
        
        if cached_names:
            for OS in (u'debian', u'ubuntu', u'mint',):
                for NAME in cached_names[OS]:
                    dist_names.append(NAME)
    
    # Only check system for dist names if could not be loaded from cache file
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
            
            for NAME in reversed(debian_names):
                if NAME not in dist_names:
                    # Put Debian names first
                    dist_names.insert(0, NAME)
    
    return tuple(dist_names)
