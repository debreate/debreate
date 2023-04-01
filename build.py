#!/usr/bin/env python3

# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import argparse
import codecs
import errno
import gzip
import os
import subprocess
import sys
import types

if sys.platform == "win32":
  import ctypes

# include libdbr in module search path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))

from libdbr        import config
from libdbr        import fileio
from libdbr        import paths
from libdbr.logger import getLogger


dir_root = os.path.normpath(os.path.dirname(__file__))

logger = getLogger()


# --- misc. functions --- #

printUsage: types.FunctionType


# --- configuration & command line options --- #

def parseCommandLine():
  args_parser = argparse.ArgumentParser(
      prog=os.path.basename(sys.argv[0]),
      description="Debreate installer script",
      add_help=False)
  args_parser.version = str(package_version)
  args_parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
  args_parser.add_argument("-v", "--version", action="version", help="Show Debreate version and exit.")
  args_parser.add_argument("-q", "--quiet", action="store_true", help="Don't print detailed information.")
  args_parser.add_argument("-t", "--target", choices=("install", "uninstall", "dist", "binary", "deb-clean"),
      default="install", help="Build type." \
          + " 'install' (default): Install the application." \
          + " 'dist': Create a source distribution package." \
          + " 'binary': Create a portable package.")
  args_parser.add_argument("-d", "--dir", default=paths.getSystemRoot(), help="Installation target root directory.")
  args_parser.add_argument("-p", "--prefix", help="Installation prefix.")
  return args_parser

# --- helper functions --- #

def exitWithError(msg, code=1, usage=False):
  logger.error(msg)
  if usage:
    printUsage()
  sys.exit(code)

def checkError(res):
  if res[0] != 0:
    exitWithError(res[1], res[0])

def checkAdmin():
  if sys.platform == "win32":
    return ctypes.windll.shell32.IsUserAnAdmin() != 0
  else:
    return os.getuid() == 0

def getInstallPath(subpath=None, stripped=False):
  path = options.prefix
  if not stripped:
    path = os.path.join(options.dir, path.strip(os.sep))
  if subpath:
    path = os.path.join(path, subpath)
  return os.path.normpath(path)

def getBinDir(stripped=False):
  return getInstallPath("bin", stripped)

def getDataDir(stripped=False):
  return getInstallPath("share/{}".format(package_name), stripped)

def getDocDir(stripped=False):
  return getInstallPath("share/doc/{}".format(package_name), stripped)

def getManDir(prefix, stripped=False):
  return getInstallPath("share/man/{}".format(prefix), stripped)

def getIconsDir(stripped=False):
  return getInstallPath("share/icons/gnome", stripped)

def checkWriteTree(_dir):
  if os.path.isfile(_dir):
    exitWithError("cannot write to directory, file exists: {}".format(dir_target), errno.EEXIST)
  while _dir.strip() and not os.path.isdir(_dir):
    _dir = os.path.dirname(_dir)
  if not os.access(_dir, os.W_OK):
    exitWithError("cannot write to directory, insufficient permissions: {}".format(_dir), errno.EACCES)

def checkWriteFile(_file):
  checkWriteTree(os.path.dirname(_file))
  if os.path.isfile(_file) and not os.access(_file, os.W_OK):
    exitWithError("cannot overwrite file, insufficient permissions: {}".format(_file), errno.EACCES)

def checkReadFile(_file):
  if not os.path.isfile(_file):
    exitWithError("cannot read file, does not exist: {}".format(_file), errno.ENOENT)
  if not os.access(_file, os.R_OK):
    exitWithError("cannot read file, insufficient permissions: {}".format(_file), errno.EPERM)

def createFileLink(file_source, link_target):
  file_source = os.path.normpath(file_source)
  link_target = os.path.normpath(link_target)
  checkWriteFile(link_target)
  if os.path.lexists(link_target):
    os.unlink(link_target)
  else:
    fileio.makeDir(os.path.dirname(link_target))

  if sys.platform == "win32" and not checkAdmin():
    logger.error("administrator privileges required on Windows platform to create symbolic links")
    sys.exit(1)
  os.symlink(file_source, link_target)
  if not os.path.islink(link_target):
    logger.error("an unknown error occurred while trying to create symbolic link: {}".format(link_target))
    sys.exit(errno.ENOENT)
  logger.info("new link -> '{}' ({})".format(link_target, file_source))

def compressFile(file_source, file_target):
  file_source = os.path.normpath(file_source)
  checkReadFile(file_source)

  fropen = codecs.open(file_source, "rb")
  file_data = fropen.read()
  fropen.read()

  fileio.writeFile(file_target, gzip.compress(file_data), binary=True, verbose=True)


# --- install targets --- #

def targetInstallApp():
  print()
  logger.info("installing app files ...")

  dirs_main = config.getValue("dirs_main").split(";")
  files_main = config.getValue("files_main").split(";")

  dir_target = getDataDir()
  for _dir in dirs_main:
    checkError((fileio.copyDir(paths.join(dir_root, _dir), dir_target, _dir, _filter="\.py$", verbose=True)))
  for _file in files_main:
    checkError((fileio.copyFile(paths.join(dir_root, _file), dir_target, _file, verbose=True)))
  exe = config.getValue("executable")
  checkError((fileio.copyExecutable(paths.join(dir_root, exe), dir_target, exe, verbose=True)))
  createFileLink(os.path.join(getDataDir(stripped=True), config.getValue("executable")), os.path.join(getBinDir(), package_name))

def targetInstallData():
  print()
  logger.info("installing data files ...")

  dirs_data = config.getValue("dirs_data").split(";")
  dir_target = getDataDir()
  for _dir in dirs_data:
    checkError((fileio.copyDir(os.path.join(dir_root, _dir), dir_target, _dir, verbose=True)))
  fileio.writeFile(os.path.join(dir_target, "INSTALLED"), "prefix={}".format(options.prefix), verbose=True)

def targetInstallDoc():
  print()
  logger.info("installing doc files ...")

  files_doc = config.getValue("files_doc").split(";")
  dir_target = getDocDir()
  for _file in files_doc:
    fileio.copyFile(paths.join(dir_root, _file), dir_target, _file, verbose=True)

  files_man = config.getValue("files_man").split(";")
  for _file in files_man:
    file_man = os.path.basename(_file)
    dir_man = getManDir(os.path.basename(os.path.dirname(_file)))
    compressFile(paths.join(dir_root, _file), paths.join(dir_man, file_man + ".gz"))

def targetInstallLocale():
  print()
  logger.info("installing locale files ...")
  # TODO:

def targetInstallMimeInfo(install=True):
  print()
  msg = "installing mime type files ..."
  if not install:
    msg = "un" + msg
  logger.info(msg)

  mime_prefix = config.getValue("dbp_mime_prefix")
  mime_type = config.getValue("dbp_mime")
  dir_conf = paths.join(getInstallPath(), "share/mime/packages")
  dir_icons = paths.join(getIconsDir(), "scalable/mimetype")
  mime_conf = paths.join(dir_root, "data/mime/{}.xml".format(package_name))
  mime_icon = paths.join(dir_root, "data/svg", mime_prefix + "-" + mime_type + ".svg")
  conf_target = paths.join(dir_conf, mime_conf[len(dir_root)+1:])
  icon_target = paths.join(dir_icons, mime_icon[len(dir_root)+1:])
  if install:
    checkError((fileio.copyFile(mime_conf, conf_target, verbose=True)))
    checkError((fileio.copyFile(mime_icon, icon_target, verbose=True)))
  else:
    checkError((fileio.deleteFile(conf_target, True)))
    checkError((fileio.deleteFile(icon_target, True)))

def targetInstall():
  if options.prefix == None:
    exitWithError("'prefix' option is required for 'install' target.", errno.EINVAL, True)

  print()
  logger.info("installing ...")

  targetInstallApp()
  targetInstallData()
  targetInstallDoc()
  targetInstallLocale()
  targetInstallMimeInfo()

def targetUninstall():
  if options.prefix == None:
    logger.error("'prefix' option is required for 'uninstall' target.")
    print()
    printUsage()
    sys.exit(errno.EINVAL)

  print()
  logger.info("uninstalling ...")

  checkError((fileio.deleteFile(os.path.join(getBinDir(), package_name), True)))
  checkError((fileio.deleteDir(getDataDir(), True)))
  checkError((fileio.deleteDir(getDocDir(), True)))
  files_man = config.getValue("files_man").split(";")
  for _file in files_man:
    file_man = os.path.basename(_file) + ".gz"
    dir_man = getManDir(os.path.basename(os.path.dirname(_file)))
    checkError((fileio.deleteFile(os.path.join(dir_man, file_man), True)))

  # TODO: uninstall locale files

  targetInstallMimeInfo(False)

def targetDebClean():
  for _dir in ("debian/debreate", "debian/.debhelper"):
    fileio.deleteDir(os.path.join(dir_root, os.path.normpath(_dir)), True)
  for _file in ("debian/debhelper-build-stamp", "debian/debreate.debhelper.log", "debian/debreate.substvars", "debian/files"):
    fileio.deleteFile(os.path.join(dir_root, os.path.normpath(_file)), True)

def targetDist():
  # TODO:
  pass

def targetBinary():
  targetDebClean()
  subprocess.run(("debuild", "-b", "-uc", "-us"))

targets = {
  "install": targetInstall,
  "uninstall": targetUninstall,
  "dist": targetDist,
  "binary": targetBinary,
  "deb-clean": targetDebClean
}


# --- execution insertion point --- #

def main():
  global options, printUsage, package_name, package_version

  config.setFile(os.path.join(dir_root, "build.conf")).load()

  package_name = config.getValue("package_name")
  package_version = float(config.getValue("package_version"))

  args_parser = parseCommandLine()
  printUsage = args_parser.print_help
  options = args_parser.parse_args()
  if not options.dir:
    options.dir = paths.getSystemRoot()

  if options.target not in targets:
    logger.error("unknown target: \"{}\"".format(options.target))
    sys.exit(1)

  targets[options.target]()

if __name__ == "__main__":
  main()
