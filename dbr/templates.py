# -*- coding: utf-8 -*-

## \package dbr.templates

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.language   import GT
from dbr.log        import Logger
from globals.paths  import PATH_app
from globals.paths  import PATH_local


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

# FIXME: Rename to 'global_licenses_templates'
application_licenses_templates = []
for PATH, DIRS, FILES in os.walk(application_licenses_path):
    for F in FILES:
        if os.path.isfile(u'{}/{}'.format(PATH, F)):
            application_licenses_templates.append(F)
            Logger.Debug(__name__, u'Loaded global license: {}'.format(F))

local_licenses_templates = []
for PATH, DIRS, FILES in os.walk(local_licenses_path):
    for F in FILES:
        if os.path.isfile(u'{}/{}'.format(PATH, F)):
            local_licenses_templates.append(F)
            Logger.Debug(__name__, u'Loaded local license: {}'.format(F))


## Retrieves the absolute path of a license template
#  
#  Templates are checked for first in local directory
#    (<HOME>/.local/share/debreate/templates/licenses)
#    then in the application's directory
#    (<PATH_app>/templates/licenses).
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
        Logger.Info(__name__, GT(u'Loading license template: {}'.format(l_template)))
    else:
        Logger.Warning(__name__, GT(u'License template not found: {}'.format(l_template)))
    
    return l_template


## Function to retrieve available license templates
#  
#  Licenses are retrieved first from <HOME>/.local/share/debreate/templates/licenses.
#  Then retrieved from <PATH_app>/templates/licenses. Only files that
#  don't already exist in local path are added.
def GetLicenseTemplatesList():
    # Use local templates first if available
    templates_list = local_licenses_templates[:]
    
    # Retrieve licenses that are not available from local path
    for LIC in application_licenses_templates:
        if LIC not in templates_list:
            templates_list.append(LIC)
    
    # Return an alphabetically sorted list
    return sorted(templates_list, key=unicode.lower)
