## @module dbr.templates

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.language  import GT
from globals.paths import getLocalDir
from libdbr        import fileinfo
from libdbr        import paths
from libdbr.logger import Logger


__logger = Logger(__name__)

## System common licenses
sys_licenses_path = "/usr/share/common-licenses"


## Application templates.
#
#  Path to application templates stored in the system Debreate directory.
#  <app_dir>/templates
#
#  @fixme
#    Should be stored elsewhere? /etc? /lib?
app_templates_path = paths.join(paths.getAppDir(), "templates")

## Application licenses.
#
#  Path to license templates stored in the Debreate data directory.
#  <app_dir>/templates/licenses
#
#  @fixme
#    Rename to 'global_licenses_path'
app_licenses_path = paths.join(app_templates_path, "licenses")

## Local templates directory.
#
#  <data_dir>/templates
local_templates_path = paths.join(getLocalDir(), "templates")

## License templates directory.
#
#  <templates_dir>/licenses
local_licenses_path = paths.join(local_templates_path, "licenses")


## Retrieves a list of licenses installed on the system.
#
#  Common system license files are located in /usr/share/common-licenses.
def GetSysLicenses():
  return fileinfo.getFileList(sys_licenses_path, recursive=False, absolute=False)


## Retrieves a list of licenses located under the ".local" directory of the user's home path.
def GetLocalLicenses():
  return fileinfo.getFileList(local_licenses_path, recursive=False, absolute=False)


## Join the app & local licenses lists.
def GetCustomLicenses():
  # Local licenses take priority
  licenses = GetLocalLicenses()
  for LIC in fileinfo.getFileList(app_licenses_path, recursive=False, absolute=False):
    if LIC not in licenses:
      licenses.append(LIC)
  return sorted(licenses, key=str.lower)


## Retrieves the absolute path of a license template.
#
#  Templates are checked for first in local directory
#  (<HOME>/.local/share/debreate/templates/licenses)
#  then in the application's directory
#  (<app_dir>/templates/licenses).
#
#  @fixme
#    Rename to "GetLicenseTemplatePath".
#  @param l_name
#    The filename of the template.
#  @return
#    Absolute path of template file.
def GetLicenseTemplateFile(l_name):
  template_path = None

  # Check local templates first
  if l_name in GetLocalLicenses():
    template_path = paths.join(local_licenses_path, l_name)
  elif l_name in fileinfo.getFileList(app_licenses_path, recursive=False, absolute=False):
    template_path = paths.join(app_licenses_path, l_name)
  elif l_name in GetSysLicenses():
    template_path = paths.join(sys_licenses_path, l_name)

  if not template_path or not os.path.isfile(template_path):
    __logger.warn(GT("License template not found: {}".format(template_path)))
    return

  __logger.debug(GT("Loading license template: {}".format(template_path)))
  return template_path
