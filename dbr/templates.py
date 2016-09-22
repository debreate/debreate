# -*- coding: utf-8 -*-


# System imports
import os

# Debreate imports
from dbr import Logger
from dbr.constants import local_path, application_path
from dbr.language import GT


## Application templates
#  
#  Path to application templates stored in the system Debreate directory.
#  <application_path>/templates
#  FIXME: Should be stored elsewhere? /etc? /lib?
application_templates_path = u'{}.templates'.format(application_path)

## Application licenses
#  
#  Path to license templates stored in the Debreate data directory
#  <application_path>/templates/li
application_licenses_path = u'{}/licenses'.format(application_templates_path)

## Local templates directory
#  
#  <local_path>/templates
local_templates_path = u'{}/templates'.format(local_path)

## License templates directory
#  
#  <templates_path>/licenses
local_licenses_path = u'{}/licenses'.format(local_templates_path)


application_licenses_templates = []
for PATH, DIRS, FILES in os.walk(application_licenses_path):
    for F in FILES:
        if os.path.isfile(u'{}/{}'.format(PATH, F)):
            application_licenses_templates.append(F)

local_licenses_templates = []
for PATH, DIRS, FILES in os.walk(local_licenses_path):
    for F in FILES:
        if os.path.isfile(u'{}/{}'.format(PATH, F)):
            local_licenses_templates.append(F)


## Retrieves the absolute path of a license template
#  
#  Templates are checked for first in local directory
#    (<HOME>/.local/share/debreate/templates/licenses)
#    then in the application's directory
#    (<application_path>/templates/licenses).
#  \param l_name
#        The filename of the template
#  \return
#        Absolute path of template file
def GetLicenseTemplateFile(l_name):
    l_template = None
    
    # Check local templates first
    if l_name in local_licenses_templates:
        l_template = u'{}/{}'.format(local_licenses_path, l_name)
    
    elif l_name in application_licenses_templates:
        l_template = u'{}/{}'.format(application_licenses_path, l_name)
    
    
    if os.path.isfile(l_template):
        Logger.Debug(__name__, GT(u'Loading license: {}'.format(l_template)))
    else:
        Logger.Warning(__name__, GT(u'License file not found: {}'.format(l_template)))
        
    return l_template


## Function to retrieve available license templates
#  
#  Licenses are retrieved first from <HOME>/.local/share/debreate/templates/licenses.
#  Then retrieved from <application_path>/templates/licenses. Only files that
#  don't already exist in local path are added.
def GetLicenseTemplatesList():
    # Use local templates first if available
    templates_list = local_licenses_templates
    
    # Retrieve licenses that are not available from local path
    for LIC in application_licenses_templates:
        if LIC not in templates_list:
            templates_list.append(LIC)
    
    # Return an alphabetically sorted list
    return sorted(templates_list, key=unicode.lower)
