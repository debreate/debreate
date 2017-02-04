# -*- coding: utf-8 -*-

## \package dbr.templates

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.language       import GT
from dbr.log            import Logger
from globals.constants  import system_licenses_path
from globals.paths      import ConcatPaths
from globals.paths      import PATH_app
from globals.paths      import PATH_local
from globals.strings    import GS


## Application templates
#  
#  Path to application templates stored in the system Debreate directory.
#  <PATH_app>/templates
#  FIXME: Should be stored elsewhere? /etc? /lib?
application_templates_path = u'{}/templates'.format(PATH_app)

## Application licenses
#  
#  Path to license templates stored in the Debreate data directory
#  FIXME: Rename to 'global_licenses_path'
#  <PATH_app>/templates/li
application_licenses_path = u'{}/licenses'.format(application_templates_path)

## Local templates directory
#  
#  <PATH_local>/templates
local_templates_path = u'{}/templates'.format(PATH_local)

## License templates directory
#  
#  <templates_path>/licenses
local_licenses_path = u'{}/licenses'.format(local_templates_path)


## Retrieves a list of licenses installed on the system
#  
#  Common system license files are located in /usr/share/common-licenses.
def GetSysLicenses():
    license_list = []
    
    for PATH, DIRS, FILES in os.walk(system_licenses_path):
        for F in FILES:
            if os.path.isfile(u'{}/{}'.format(system_licenses_path, F)):
                license_list.append(F)
    
    return sorted(license_list)


## Initializes/Refreshes the app licenses list
def GetAppLicenseTemplates():
    # Clear old values
    licenses_app = []
    
    for PATH, DIRS, FILES in os.walk(application_licenses_path):
        for F in FILES:
            if os.path.isfile(u'{}/{}'.format(PATH, F)):
                licenses_app.append(F)
                
                Logger.Debug(__name__, u'Loaded global license: {}'.format(F))
    
    return sorted(licenses_app, key=GS.lower)


## Initializes/Refreshes the local licenses list
def GetLocalLicenseTemplates():
    # Clear old values
    licenses_local = []
    
    for PATH, DIRS, FILES in os.walk(local_licenses_path):
        for F in FILES:
            if os.path.isfile(u'{}/{}'.format(PATH, F)):
                licenses_local.append(F)
                
                Logger.Debug(__name__, u'Loaded local license: {}'.format(F))
    
    return sorted(licenses_local, key=GS.lower)


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
    if l_name in GetLocalLicenseTemplates():
        template_path = ConcatPaths((local_licenses_path, l_name))
    
    elif l_name in GetAppLicenseTemplates():
        template_path = ConcatPaths((application_licenses_path, l_name))
    
    if not template_path or not os.path.isfile(template_path):
        Logger.Warn(__name__, GT(u'License template not found: {}'.format(template_path)))
        
        return
    
    Logger.Info(__name__, GT(u'Loading license template: {}'.format(template_path)))
    
    return template_path


## Function to retrieve available license templates
#  
#  Licenses are retrieved first from <HOME>/.local/share/debreate/templates/licenses.
#  Then retrieved from <PATH_app>/templates/licenses. Only files that
#  don't already exist in local path are added.
def GetLicenseTemplatesList():
    # Use local templates first if available
    templates_list = GetLocalLicenseTemplates()
    
    # Retrieve licenses that are not available from local path
    for LIC in GetAppLicenseTemplates():
        if LIC not in templates_list:
            templates_list.append(LIC)
    
    # Return an alphabetically sorted list
    return sorted(templates_list, key=GS.lower)
