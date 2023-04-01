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
from libdbr        import tasks
from libdbr.logger import getLogger


dir_root = os.path.normpath(os.path.dirname(__file__))

logger = getLogger()


# --- misc. functions --- #

printUsage: types.FunctionType


# --- configuration & command line options --- #

def parseCommandLine(task_list):
  task_help = []
  for t in task_list:
    task_help.append(t + ": " + task_list[t])
  args_parser = argparse.ArgumentParser(
      prog=os.path.basename(sys.argv[0]),
      description="Debreate installer script",
      add_help=False)
  args_parser.version = package_version
  args_parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
  args_parser.add_argument("-v", "--version", action="version", help="Show Debreate version and exit.")
  args_parser.add_argument("-q", "--quiet", action="store_true", help="Don't print detailed information.")
  # ~ args_parser.add_argument("-t", "--task", choices=("install", "uninstall", "dist", "binary", "clean-deb"),
  args_parser.add_argument("-t", "--task", choices=tuple(task_list),
      default="install", help="\n".join(task_help))
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


# --- build tasks --- #

def stageApp(prefix):
  print()
  logger.info("staging app files ...")

  dirs_app = config.getValue("dirs_app").split(";")
  files_app = config.getValue("files_app").split(";")

  dir_target = paths.join(prefix, package_name)
  for _dir in dirs_app:
    checkError((fileio.copyDir(paths.join(dir_root, _dir), dir_target, _dir, _filter="\.py$", exclude="__pycache__", verbose=True)))
  for _file in files_app:
    checkError((fileio.copyFile(paths.join(dir_root, _file), dir_target, _file, verbose=True)))
  exe = config.getValue("executable")
  checkError((fileio.copyExecutable(paths.join(dir_root, exe), dir_target, exe, verbose=True)))

  # add desktop menu file
  file_menu = "{}.desktop".format(package_name)
  checkError((fileio.copyFile(paths.join(dir_root, "data", file_menu), paths.join(prefix, "applications", file_menu), verbose=True)))

def stageData(prefix):
  print()
  logger.info("staging data files ...")

  dirs_data = config.getValue("dirs_data").split(";")

  dir_target = paths.join(prefix, package_name)
  for _dir in dirs_data:
    checkError((fileio.copyDir(os.path.join(dir_root, _dir), dir_target, _dir, verbose=True)))
  # copy icon to pixmaps directory
  checkError((fileio.copyFile(paths.join(dir_target, "bitmaps/icon/64/logo.png"), paths.join(prefix, "pixmaps", package_name + ".png"), verbose=True)))

def stageDoc(prefix):
  print()
  logger.info("staging doc files ...")

  files_doc = config.getValue("files_doc").split(";")

  dir_target = paths.join(prefix, "doc/{}".format(package_name))
  for _file in files_doc:
    fileio.copyFile(paths.join(dir_root, _file), dir_target, _file, verbose=True)

  files_man = config.getValue("files_man").split(";")
  for _file in files_man:
    basename = os.path.basename(_file)
    dir_man = paths.join(prefix, "man/{}".format(os.path.basename(os.path.dirname(_file))))
    compressFile(paths.join(dir_root, _file), paths.join(dir_man, basename + ".gz"))

def stageLocale(prefix):
  print()
  logger.info("staging locale files ...")
  # TODO:

def stageMimeInfo(prefix):
  print()
  logger.info("staging mime type files ...")

  dir_conf = paths.join(prefix, "mime/packages")
  # FIXME: need system independent directory
  dir_icons = paths.join(prefix, "icons/gnome/scalable/mimetype")

  mime_prefix = config.getValue("dbp_mime_prefix")
  mime_type = config.getValue("dbp_mime")
  mime_conf = paths.join(dir_root, "data/mime/{}.xml".format(package_name))
  mime_icon = paths.join(dir_root, "data/svg", mime_prefix + "-" + mime_type + ".svg")
  conf_target = paths.join(dir_conf, "{}.xml".format(package_name))
  icon_target = paths.join(dir_icons, "application-x-dbp.svg")
  checkError((fileio.copyFile(mime_conf, conf_target, verbose=True)))
  checkError((fileio.copyFile(mime_icon, icon_target, verbose=True)))

def taskInstall():
  if options.prefix == None:
    exitWithError("'prefix' option is required for 'install' task.", errno.EINVAL, True)

  print()
  logger.info("installing ...")

  tasks.run("stage")
  dir_stage = paths.join(dir_root, "build/stage")
  dir_install = paths.join(options.dir, options.prefix)

  for obj in os.listdir(dir_stage):
    abspath = paths.join(dir_stage, obj)
    if not os.path.isdir(abspath):
      checkError((fileio.moveFile(abspath, dir_install, obj, verbose=True)))
    else:
      checkError((fileio.moveDir(abspath, dir_install, obj, verbose=True)))
  checkError((fileio.deleteDir(dir_stage, verbose=True)))

  dir_data = paths.join(dir_install, "share", package_name)
  dir_bin = paths.join(dir_install, "bin")

  # set executable
  os.chmod(paths.join(dir_data, "init.py"), 0o775)

  createFileLink(paths.join(options.prefix, "share", package_name, config.getValue("executable")), paths.join(dir_bin, package_name))
  fileio.writeFile(paths.join(dir_data, "INSTALLED"), "prefix={}".format(options.prefix), verbose=True)

def taskStage():
  tasks.run("clean-stage")
  dir_stage = paths.join(dir_root, "build/stage")
  dir_data = paths.join(dir_stage, "share")
  stageApp(dir_data)
  stageData(dir_data)
  stageDoc(dir_data)
  stageLocale(dir_data)
  stageMimeInfo(dir_data)

# FIXME: include --dir parameter in uninstall
def taskUninstall():
  if options.prefix == None:
    logger.error("'prefix' option is required for 'uninstall' task.")
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

  checkError((fileio.deleteFile(paths.join(options.prefix, "share/icons/gnome/scalable/mimetype/application-x-dbp.svg"), True)))
  checkError((fileio.deleteFile(paths.join(options.prefix, "share/mime/packages/{}.xml".format(package_name)), True)))
  checkError((fileio.deleteFile(paths.join(options.prefix, "share/applications", package_name + ".desktop"), True)))
  checkError((fileio.deleteFile(paths.join(options.prefix, "share/pixmaps", package_name + ".png"), True)))

def taskClean():
  dir_build = paths.join(dir_root, "build")
  fileio.deleteDir(dir_build, verbose=True)

def taskCleanStage():
  dir_stage = paths.join(dir_root, "build/stage")
  fileio.deleteDir(dir_stage, verbose=True)

def taskCleanDeb():
  for _dir in ("debian/debreate", "debian/.debhelper"):
    fileio.deleteDir(os.path.join(dir_root, os.path.normpath(_dir)), True)
  for _file in ("debian/debhelper-build-stamp", "debian/debreate.debhelper.log", "debian/debreate.substvars", "debian/files"):
    fileio.deleteFile(os.path.join(dir_root, os.path.normpath(_file)), True)

def taskDist():
  # TODO:
  pass

def taskDebBinary():
  taskCleanDeb()
  subprocess.run(("debuild", "-b", "-uc", "-us"))

  dir_parent = os.path.dirname(dir_root)
  dir_dist = paths.join(dir_root, "build/dist")
  fileio.makeDir(dir_dist)
  # FIXME: determine .deb package name
  for obj in os.listdir(dir_parent):
    if not obj.endswith(".deb"):
      continue
    abspath = paths.join(dir_parent, obj)
    if os.path.isfile(abspath):
      fileio.moveFile(abspath, dir_dist, obj, verbose=True)

def taskPortable():
  tasks.run("stage")
  dir_build = paths.join(dir_root, "build")
  dir_data = paths.join(dir_build, "stage/share/debreate")
  dir_dist = paths.join(dir_build, "dist")
  file_dist = paths.join(dir_dist, "{}_{}_portable.zip".format(package_name, package_version))
  # FIXME: packDir should create parent directory
  fileio.makeDir(dir_dist, verbose=True)
  fileio.packDir(dir_data, file_dist, verbose=True)

def addTask(task_list, name, action, desc):
  tasks.add(name, action)
  task_list[name] = desc

def initTasks(task_list):
  addTask(task_list, "install", taskInstall, "Install application files.")
  addTask(task_list, "uninstall", taskUninstall, "Uninstall application files.")
  addTask(task_list, "stage", taskStage, "Stage files for distribution (same as `-t install -p (root_dir)/build/stage`)")
  addTask(task_list, "dist", taskDist, "Create a source distribution package (TODO).")
  addTask(task_list, "deb-bin", taskDebBinary, "Build binary Debian package for installation.")
  addTask(task_list, "portable", taskPortable, "Create portable distribution package.")
  addTask(task_list, "clean", taskClean, "Remove files from build directory.")
  addTask(task_list, "clean-stage", taskCleanStage, "Remove files from stage directory.")
  addTask(task_list, "clean-deb", taskCleanDeb, "Clean up temporary files from .deb package builds.")
  return task_list

# --- execution insertion point --- #

def main():
  global options, printUsage, package_name, package_version

  config.setFile(os.path.join(dir_root, "build.conf")).load()

  package_name = config.getValue("package")
  package_version = config.getValue("version")

  args_parser = parseCommandLine(initTasks({}))
  printUsage = args_parser.print_help
  options = args_parser.parse_args()
  if not options.dir:
    options.dir = paths.getSystemRoot()

  task = tasks.get(options.task)
  if not task:
    logger.error("unknown task ({})".format(options.task))
    sys.exit(1)
  task()

if __name__ == "__main__":
  main()
