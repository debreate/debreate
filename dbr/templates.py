# -*- coding: utf-8 -*-

## \package dbr.templates

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.language       import GT
from dbr.log            import Logger
from globals.paths      import ConcatPaths
from globals.paths      import PATH_app
from globals.paths      import PATH_local
from globals.strings    import GS


## System common licenses
sys_licenses_path = u'/usr/share/common-licenses'


## Application templates
#  
#  Path to application templates stored in the system Debreate directory.
#  <PATH_app>/templates
#  FIXME: Should be stored elsewhere? /etc? /lib?
app_templates_path = ConcatPaths((PATH_app, u'templates'))

## Application licenses
#  
#  Path to license templates stored in the Debreate data directory
#  FIXME: Rename to 'global_licenses_path'
#  <PATH_app>/templates/li
app_licenses_path = ConcatPaths((app_templates_path, u'licenses'))

## Local templates directory
#  
#  <PATH_local>/templates
local_templates_path = ConcatPaths((PATH_local, u'templates'))

## License templates directory
#  
#  <templates_path>/licenses
local_licenses_path = ConcatPaths((local_templates_path, u'licenses'))


## Retrieves all files from the given path
#
#  FIXME: Should be renamed to "GetFiles" & moved to a "files" or "general" module
#
#  \param path
#    Directory to search for license templates
def GetLicenses(path):
    licenses = []
    
    for PATH, DIRS, FILES in os.walk(path):
        for F in FILES:
            license_path = ConcatPaths((path, F))
            
            if os.path.isfile(license_path):
                licenses.append(F)
                
                Logger.Debug(__name__, u'Loaded license: {}'.format(license_path))
    
    return sorted(licenses, key=GS.lower)


## Retrieves a list of licenses installed on the system
#  
#  Common system license files are located in /usr/share/common-licenses.
def GetSysLicenses():
    return GetLicenses(sys_licenses_path)


## Retrieves a list of licenses located under the ".local" directory of the user's home path
def GetLocalLicenses():
    return GetLicenses(local_licenses_path)


## Join the app & local licenses lists
def GetCustomLicenses():
    # Local licenses take priority
    licenses = GetLicenses(local_licenses_path)
    
    for LIC in GetLicenses(app_licenses_path):
        if LIC not in licenses:
            licenses.append(LIC)
    
    return sorted(licenses, key=GS.lower)


## Retrieves the absolute path of a license template
#
#  FIXME: Rename to "GetLicenseTemplatePath"
#  Templates are checked for first in local directory
#    (<HOME>/.local/share/debreate/templates/licenses)
#    then in the application's directory
#    (<PATH_app>/templates/licenses).
#
#  \param l_name
#        The filename of the template
#  \return
#        Absolute path of template file
def GetLicenseTemplateFile(l_name):
    template_path = None
    
    # Check local templates first
    if l_name in GetLicenses(local_licenses_path):
        template_path = ConcatPaths((local_licenses_path, l_name))
    
    elif l_name in GetLicenses(app_licenses_path):
        template_path = ConcatPaths((app_licenses_path, l_name))
    
    if not template_path or not os.path.isfile(template_path):
        Logger.Warn(__name__, GT(u'License template not found: {}'.format(template_path)))
        
        return
    
    Logger.Info(__name__, GT(u'Loading license template: {}'.format(template_path)))
    
    return template_path
