#!/usr/bin/env python3

# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

if __name__ != "__main__":
  print("ERROR: this build script cannot be imported as a module")
  exit(1)

import argparse
import errno
import os
import re
import subprocess
import sys
import types

# include libdbr in module search path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))

from libdbr         import config
from libdbr         import fileio
from libdbr         import misc
from libdbr         import paths
from libdbr         import tasks
from libdbr         import userinfo
from libdbr.logger  import LogLevel
from libdbr.logger  import Logger
from libdbr.strings import sgr


script_name = os.path.basename(sys.argv[0])
logger = Logger(script_name)

# --- misc. functions --- #

printUsage: types.FunctionType


# --- helper functions --- #

def exitWithError(msg, code=1, usage=False):
  logger.error(msg)
  if usage:
    printUsage()
  sys.exit(code)

def checkError(res):
  if res[0] != 0:
    exitWithError(res[1], res[0])

def checkWriteTree(_dir):
  if os.path.isfile(_dir):
    exitWithError("cannot write to directory, file exists: {}".format(_dir), errno.EEXIST)
  while _dir.strip() and not os.path.isdir(_dir):
    _dir = os.path.dirname(_dir)
  if not os.access(_dir, os.W_OK):
    exitWithError("cannot write to directory, insufficient permissions: {}".format(_dir), errno.EACCES)

def checkWriteFile(_file):
  checkWriteTree(os.path.dirname(_file))
  if os.path.isfile(_file) and not os.access(_file, os.W_OK):
    exitWithError("cannot overwrite file, insufficient permissions: {}".format(_file), errno.EACCES)

def createFileLink(file_source, link_target):
  file_source = os.path.normpath(file_source)
  link_target = os.path.normpath(link_target)
  checkWriteFile(link_target)
  if os.path.lexists(link_target):
    os.unlink(link_target)
  else:
    fileio.makeDir(os.path.dirname(link_target))

  if sys.platform == "win32" and not userinfo.isAdmin():
    exitWithError("administrator privileges required on Windows platform to create symbolic links")
  os.symlink(file_source, link_target)
  if not os.path.islink(link_target):
    exitWithError("an unknown error occurred while trying to create symbolic link: {}".format(link_target))
  if options.verbose:
    logger.info("new link -> '{}' ({})".format(link_target, file_source))


# --- file staging functions --- #

def stageApp(prefix):
  print()
  logger.info("staging app files ...")

  dirs_app = cfg.getValue("dirs_app").split(";")

  dir_target = paths.join(prefix, package_name)
  for _dir in dirs_app:
    checkError((fileio.copyDir(paths.join(dir_app, _dir), dir_target, _dir, _filter="\.py$", exclude="__pycache__", verbose=options.verbose)))
  exe = cfg.getValue("executable")
  checkError((fileio.copyExecutable(paths.join(dir_app, exe), dir_target, exe, verbose=options.verbose)))

  # add desktop menu file
  file_menu = "{}.desktop".format(package_name)
  checkError((fileio.copyFile(paths.join(dir_app, "data", file_menu), paths.join(prefix, "applications", file_menu), verbose=options.verbose)))

def stageData(prefix):
  print()
  logger.info("staging data files ...")

  dirs_data = cfg.getValue("dirs_data").split(";")

  dir_target = paths.join(prefix, package_name)
  for _dir in dirs_data:
    checkError((fileio.copyDir(paths.join(dir_app, _dir), dir_target, _dir, verbose=options.verbose)))
  # copy icon to pixmaps directory
  checkError((fileio.copyFile(paths.join(dir_target, "bitmaps/icon/64/logo.png"), paths.join(prefix, "pixmaps", package_name + ".png"), verbose=options.verbose)))

def stageDoc(prefix):
  print()
  logger.info("staging doc files ...")

  files_doc = cfg.getValue("files_doc").split(";")

  dir_target = paths.join(prefix, "doc/{}".format(package_name))
  for _file in files_doc:
    fileio.copyFile(paths.join(dir_app, _file), dir_target, os.path.basename(_file), verbose=options.verbose)

  files_man = cfg.getValue("files_man").split(";")
  for _file in files_man:
    basename = os.path.basename(_file)
    dir_man = paths.join(prefix, "man/{}".format(os.path.basename(os.path.dirname(_file))))
    checkError((fileio.compressFile(paths.join(dir_app, _file),
        paths.join(dir_man, basename + ".gz"), verbose=options.verbose)))

def stageLocale(prefix):
  print()
  logger.info("staging locale files ...")

  dir_source = paths.join(dir_app, "locale")
  dir_target = paths.join(prefix, "locale")

  for ROOT, DIRS, FILES in os.walk(dir_source):
    for basename in FILES:
      if not basename.endswith(".po"):
        continue
      filepath = paths.join(ROOT, basename)
      loc_code = os.path.basename(os.path.split(filepath)[0])
      loc_dir = paths.join(dir_target, loc_code, "LC_MESSAGES")
      fileio.makeDir(loc_dir)
      mo_target = paths.join(loc_dir, basename[0:-2] + "mo")
      # FIXME: Python library for compiling translations?
      cmd_args = ["msgfmt", "-o", mo_target, filepath]
      if options.verbose:
        cmd_args.insert(1, "-v")
      subprocess.run(cmd_args, check=True)
      if options.verbose:
        print("compile locale '{}'".format(mo_target))

def stageMimeInfo(prefix):
  print()
  logger.info("staging mime type files ...")

  dir_conf = paths.join(prefix, "mime/packages")
  # FIXME: need system independent directory
  dir_icons = paths.join(prefix, "icons/hicolor/scalable/mimetypes")

  mime_prefix = cfg.getValue("dbp_mime_prefix")
  mime_type = cfg.getValue("dbp_mime")
  mime_conf = paths.join(dir_app, "data/mime/{}.xml".format(package_name))
  mime_icon = paths.join(dir_app, "data/svg", mime_prefix + "-" + mime_type + ".svg")
  conf_target = paths.join(dir_conf, "{}.xml".format(package_name))
  icon_target = paths.join(dir_icons, "application-x-dbp.svg")
  checkError((fileio.copyFile(mime_conf, conf_target, verbose=options.verbose)))
  checkError((fileio.copyFile(mime_icon, icon_target, verbose=options.verbose)))

## Formats changes for Debianized changelog
def getChangesDeb():
  changelog = paths.join(paths.getAppDir(), "docs/changelog.txt")
  if not os.path.isfile(changelog):
    return
  changes = misc.getLatestChanges(changelog)
  deb_info = cfg.getKeyedValue("deb_info", sep=";")
  deb_info["package"] = package_name
  deb_info["version"] = package_version
  if package_version_dev > 0:
    deb_info["version"] = "{}-dev{}".format(deb_info["version"], package_version_dev)
  return misc.formatDebianChanges(changes, deb_info)


# --- build tasks --- #

def taskStage():
  tasks.run("update-version")
  tasks.run("clean-stage")
  dir_stage = paths.join(dir_app, "build/stage")
  dir_data = paths.join(dir_stage, "share")
  stageApp(dir_data)
  stageData(dir_data)
  stageDoc(dir_data)
  stageLocale(dir_data)
  stageMimeInfo(dir_data)

def taskStageSource():
  tasks.run("clean-stage")

  print()
  logger.info("staging source distribution files ...")

  root_stage = paths.join(dir_app, "build/stage")

  for _dir in cfg.getValue("dirs_dist_py").split(";"):
    abspath = paths.join(dir_app, _dir)
    checkError((fileio.copyDir(abspath, paths.join(root_stage, _dir), exclude=r"^(.*\.pyc|__pycache__)$", verbose=options.verbose)))
  for _dir in cfg.getValue("dirs_dist_data").split(";"):
    abspath = paths.join(dir_app, _dir)
    checkError((fileio.copyDir(abspath, paths.join(root_stage, _dir), verbose=options.verbose)))
  for _file in cfg.getValue("files_dist_data").split(";"):
    abspath = paths.join(dir_app, _file)
    checkError((fileio.copyFile(abspath, paths.join(root_stage, _file), verbose=options.verbose)))
  for _file in cfg.getValue("files_dist_exe").split(";"):
    abspath = paths.join(dir_app, _file)
    checkError((fileio.copyExecutable(abspath, paths.join(root_stage, _file), verbose=options.verbose)))

def taskInstall():
  if options.prefix == None:
    exitWithError("'prefix' option is required for 'install' task.", errno.EINVAL, True)

  print()
  logger.info("installing ...")

  tasks.run("stage")
  dir_stage = paths.join(dir_app, "build/stage")
  dir_install = paths.join(options.dir, options.prefix)

  for obj in os.listdir(dir_stage):
    abspath = paths.join(dir_stage, obj)
    if not os.path.isdir(abspath):
      checkError((fileio.moveFile(abspath, dir_install, obj, verbose=options.verbose)))
    else:
      checkError((fileio.moveDir(abspath, dir_install, obj, verbose=options.verbose)))
  checkError((fileio.deleteDir(dir_stage, verbose=options.verbose)))

  dir_data = paths.join(dir_install, "share", package_name)
  dir_bin = paths.join(dir_install, "bin")

  # set executable
  os.chmod(paths.join(dir_data, "init.py"), 0o775)

  createFileLink(paths.join(options.prefix, "share", package_name, cfg.getValue("executable")), paths.join(dir_bin, package_name))
  fileio.writeFile(paths.join(dir_data, "INSTALLED"), "prefix={}".format(options.prefix), verbose=options.verbose)

def taskUninstall():
  if options.prefix == None:
    exitWithError("'prefix' option is required for 'uninstall' task.", errno.EINVAL, True)

  print()
  logger.info("uninstalling ...")

  root_install = paths.join(options.dir, options.prefix)
  root_bin = paths.join(root_install, "bin")
  root_data = paths.join(root_install, "share")
  root_menu = paths.join(root_data, "applications")
  root_doc = paths.join(root_data, "doc")
  root_man = paths.join(root_data, "man")
  root_mime = paths.join(root_data, "mime/packages")
  root_locale = paths.join(root_data, "locale")
  root_pixmaps = paths.join(root_data, "pixmaps")
  root_icons = paths.join(root_data, "icons/hicolor")

  logger.info("uninstalling app files ...")

  remove_files = (
    paths.join(root_bin, package_name),
    paths.join(root_menu, package_name + ".desktop"),
    paths.join(root_mime, package_name + ".xml"),
    paths.join(root_pixmaps, package_name + ".png"),
    paths.join(root_icons, "scalable/mimetypes/{}-{}.svg"
        .format(cfg.getValue("dbp_mime_prefix"), cfg.getValue("dbp_mime")))
  )

  for rm_f in remove_files:
    checkError((fileio.deleteFile(rm_f, verbose=options.verbose)))

  remove_files_man = cfg.getValue("files_man").split(";")
  for _file in remove_files_man:
    file_man = os.path.basename(_file) + ".gz"
    dir_man = paths.join(root_man, os.path.basename(os.path.dirname(_file)))
    checkError((fileio.deleteFile(paths.join(dir_man, file_man), verbose=options.verbose)))

  source_loc = paths.join(dir_app, "locale")
  if os.path.isdir(source_loc):
    tags_loc = []
    for obj in os.listdir(source_loc):
      if os.path.isdir(paths.join(source_loc, obj)):
        tags_loc.append(obj)

    for tag in tags_loc:
      file_mo = paths.join(root_locale, tag, "LC_MESSAGES/{}.mo".format(package_name))
      checkError((fileio.deleteFile(file_mo, verbose=options.verbose)))

  logger.info("uninstalling app directories ...")

  remove_dirs = (
    paths.join(root_data, package_name),
    paths.join(root_doc, package_name)
  )

  for rm_d in remove_dirs:
    checkError((fileio.deleteDir(rm_d, verbose=options.verbose)))

def taskUpdateVersion():
  ver_string = package_version
  ver = ver_string.split(".")
  ver_dev = int(cfg.getValue("version_dev", 0))
  ver_string_full = ver_string
  if ver_dev > 0:
    ver_string_full += "-dev{}".format(ver_dev)

  print()
  print("package:     {}".format(package_name))
  print("version:     {}".format(package_version))
  print("dev version: {}".format(ver_dev))

  print()
  logger.info("updating version information ...")

  repl = [
    ("^__version = .*$", "__version = ({})".format(", ".join(ver))),
    ("^__version_dev = .*$", "__version_dev = {}".format(ver_dev))
  ]
  fileio.replace(paths.join(dir_app, "lib/libdebreate/appinfo.py"), repl, count=1,
      verbose=options.verbose)

  repl = [
    (r"^VERSION_maj = .*$", "VERSION_maj = {}".format(ver[0])),
    (r"^VERSION_min = .*$", "VERSION_min = {}".format(ver[1]))
  ]
  if len(ver) > 2:
    repl.append((r"^VERSION_rev = .*$", "VERSION_rev = {}".format(ver[2])))
  repl.append((r"^VERSION_dev = .*$", "VERSION_dev = {}".format(ver_dev)))
  fileio.replace(paths.join(dir_app, "docs/Doxyfile"), r"^PROJECT_NUMBER         = .*",
      "PROJECT_NUMBER         = {}".format(ver_string_full), count=1, verbose=options.verbose)
  fileio.replace(paths.join(dir_app, "locale/debreate.pot"),
      r'"Project-Id-Version: Debreate .*\\n"$',
      '"Project-Id-Version: Debreate {}\\\\n"'.format(ver_string_full), count=1,
      verbose=options.verbose)
  fileio.replace(paths.join(dir_app, "Makefile"), r"^VERSION = .*$",
      "VERSION = {}".format(ver_string_full), count=1, verbose=options.verbose)
  if ver_dev == 0:
    fileio.replace(paths.join(dir_app, "docs/changelog.txt"), r"^next$", ver_string_full, count=1,
        fl=True, verbose=options.verbose)
  # ~ fileio.replace(paths.join(dir_app, "docs/changelog.txt"), r"^(?!\s*$).+", ver_string_full, count=1,
      # ~ fl=True, verbose=options.verbose)

def __cleanByteCode(_dir):
  if os.path.basename(_dir) == "__pycache__":
    checkError((fileio.deleteDir(_dir, verbose=options.verbose)))
    return
  for obj in os.listdir(_dir):
    abspath = paths.join(_dir, obj)
    if os.path.isdir(abspath):
      __cleanByteCode(abspath)
    elif obj.endswith(".pyc") and os.path.lexists(abspath):
      checkError((fileio.deleteFile(abspath, verbose=options.verbose)))

def taskBuildDocs():
  tasks.run("update-version")

  print()
  logger.info("building Doxygen documentation ...")

  dir_docs = paths.join(dir_app, "build/docs")
  fileio.makeDir(dir_docs, verbose=options.verbose)
  subprocess.run(["doxygen", paths.join(dir_app, "docs/Doxyfile")])
  logger.info("cleaning up ...")
  for ROOT, DIRS, FILES in os.walk(paths.join(dir_docs, "html")):
    for _file in FILES:
      if not _file.endswith(".html"):
        continue
      abspath = paths.join(ROOT, _file)
      fileio.replace(abspath, r"^<!DOCTYPE html.*>$", "<!DOCTYPE html>", count=1, flags=re.M)

def taskClean():
  tasks.run(("clean-deb", "clean-stage", "clean-dist"))

  print()
  logger.info("removing build directory ...")

  dir_build = paths.join(dir_app, "build")
  checkError((fileio.deleteDir(dir_build, verbose=options.verbose)))

  excludes = cfg.getValue("exclude_clean_dirs").split(";")
  for ROOT, DIRS, FILES in os.walk(dir_app):
    for _dir in DIRS:
      abspath = paths.join(ROOT, _dir)
      relpath = abspath[len(dir_app)+1:]
      if re.match(r"^({})".format("|".join(excludes)), relpath, flags=re.M):
        continue
      __cleanByteCode(abspath)

def taskCleanStage():
  print()
  logger.info("removing temporary staged build files ...")

  dir_stage = paths.join(dir_app, "build/stage")
  checkError((fileio.deleteDir(dir_stage, verbose=options.verbose)))

def taskCleanDeb():
  print()
  logger.info("removing temporary Debian build files ...")

  # TODO: configure files & directories in build.conf
  for _dir in ("debian/debreate", "debian/.debhelper"):
    checkError((fileio.deleteDir(paths.join(dir_app, _dir), verbose=options.verbose)))
  for _file in (
      "debian/debhelper-build-stamp", "debian/debreate.debhelper.log",
      "debian/debreate.substvars", "debian/files", "debian/changelog"):
    checkError((fileio.deleteFile(paths.join(dir_app, _file), verbose=options.verbose)))

def taskCleanDist():
  print()
  logger.info("removing built distribution packages ...")

  dir_dist = paths.join(dir_app, "build/dist")
  checkError((fileio.deleteDir(dir_dist, verbose=options.verbose)))

def taskDistSource():
  tasks.run("stage-source")

  print()
  logger.info("building source distribution package ...")

  root_stage = paths.join(dir_app, "build/stage")
  root_dist = paths.join(dir_app, "build/dist")

  pkg_dist = paths.join(root_dist, package_name + "_" + package_version_full + ".tar.xz")

  # FIXME: parent directory should be created automatically
  if not os.path.isdir(root_dist):
    fileio.makeDir(root_dist, verbose=options.verbose)

  checkError((fileio.packDir(root_stage, pkg_dist, form="xz", verbose=options.verbose)))

  if os.path.isfile(pkg_dist):
    logger.info("built package '{}'".format(pkg_dist))
  else:
    exitWithError("failed to build source package", errno.ENOENT)

def taskDistBin():
  tasks.run("stage")

  print()
  logger.info("building portable binary distribution package ...")

  dir_build = paths.join(dir_app, "build")
  root_data = paths.join(dir_build, "stage/share")
  dir_data = paths.join(root_data, package_name)
  dir_dist = paths.join(dir_build, "dist")
  pkg_dist = paths.join(dir_dist, "{}_{}_portable.zip".format(package_name, package_version_full))
  # FIXME: packDir should create parent directory
  fileio.makeDir(dir_dist, verbose=options.verbose)
  checkError((fileio.packDir(dir_data, pkg_dist, verbose=options.verbose)))

  for _dir in cfg.getValue("dirs_bdist_data").split(";"):
    checkError((fileio.packDir(_dir, pkg_dist, incroot=True, amend=True, verbose=options.verbose)))
  for _file in cfg.getValue("files_bdist_data").split(";"):
    checkError((fileio.packFile(_file, pkg_dist, amend=True, verbose=options.verbose)))

  dir_locale = paths.join(root_data, "locale")
  os.chdir(root_data)
  checkError((fileio.packDir(dir_locale, pkg_dist, incroot=True, amend=True, verbose=options.verbose)))
  os.chdir(dir_app)

  if os.path.isfile(pkg_dist):
    logger.info("built package '{}'".format(pkg_dist))
  else:
    exitWithError("failed to build portable binary package", errno.ENOENT)

def __buildDebChangelog():
  root_debian = paths.join(dir_app, "debian")
  file_changelog = paths.join(root_debian, "changelog")

  # create changelog for release
  fileio.writeFile(file_changelog, getChangesDeb(), verbose=options.verbose)
  if not os.path.isfile(file_changelog):
    exitWithError("failed to create Debian changelog", errno.ENOENT)

def taskDistDeb():
  tasks.run("clean-deb")

  print()
  logger.info("building Debian binary distribution package ...")

  __buildDebChangelog()
  subprocess.run(("debuild", "-b", "-uc", "-us"))

  dir_parent = os.path.dirname(dir_app)
  dir_dist = paths.join(dir_app, "build/dist")
  fileio.makeDir(dir_dist)
  deb_prefix = package_name + "_" + package_version \
      + ("" if package_version_dev == 0 else "-dev{}".format(package_version_dev)) + "_"
  deb_name = deb_prefix + "all.deb"
  deb_target = paths.join(dir_dist, deb_name)
  if os.path.isfile(deb_target):
    checkError((fileio.deleteFile(deb_target, verbose=options.verbose)))
  checkError((fileio.moveFile(paths.join(dir_parent, deb_name), dir_dist, deb_name,
      verbose=options.verbose)))

  # clean up files created by helper scripts
  for obj in os.listdir(dir_parent):
    abspath = paths.join(dir_parent, obj)
    if not os.path.isfile(abspath):
      continue
    if obj.startswith(deb_prefix) and obj.split(".")[-1] in ("build", "buildinfo", "changes"):
      checkError((fileio.deleteFile(abspath, verbose=options.verbose)))

def taskDebSource():
  tasks.run("clean-deb")
  __buildDebChangelog()
  tasks.run("stage-source")

  print()
  logger.info("building Debian source package ...")

  root_build = paths.join(dir_app, "build")
  root_stage = paths.join(root_build, "stage")
  root_dist = paths.join(root_build, "dist")

  # rename stage directory for use with debuild scripts
  root_target = paths.join(root_build, package_name)
  if os.path.isdir(root_target):
    checkError((fileio.deleteDir(root_target, verbose=options.verbose)))
  checkError((fileio.moveDir(root_stage, root_target, verbose=options.verbose)))

  # move into target directory to run debuild scripts
  os.chdir(root_target)
  if options.verbose:
    logger.info("executing debuild from '{}'".format(os.getcwd()))
  subprocess.run(("debuild", "-S", "-sa"), check=True)

  pre = package_name + "_" + package_version_full
  fileio.makeDir(root_dist)
  for suf in (".dsc", ".tar.xz", "_source.build", "_source.buildinfo", "_source.changes"):
    # move built files to dist directory
    basename = pre + suf
    source_filename = paths.join(root_build, basename)
    target_filename = paths.join(root_dist, basename)
    if os.path.isfile(target_filename):
      checkError((fileio.deleteFile(target_filename, verbose=options.verbose)))
    checkError((fileio.moveFile(source_filename, target_filename, verbose=options.verbose)))
  os.chdir(dir_app)

def taskCheckCode():
  print()
  for action in ("pylint", "mypy"):
    logger.info("checking code with {} ...".format(action))
    params = [action, dir_app]
    if options.verbose:
      params.insert(1, "-v")
    res = subprocess.run(params)
    if res.returncode != 0:
      return res.returncode

def taskPrintChanges():
  changelog = paths.join(paths.getAppDir(), "docs/changelog.txt")
  if not os.path.isfile(changelog):
    return
  print(misc.getLatestChanges(changelog))

def taskPrintChangesDeb():
  print(getChangesDeb())

def taskRunTests():
  from libdbr.unittest import runTest

  # enable debugging for tests
  Logger.setLevel(LogLevel.DEBUG)

  dir_tests = paths.join(dir_app, "tests")
  if not os.path.isdir(dir_tests):
    return

  # add tests directory to module search path
  sys.path.insert(0, dir_tests)
  introspect_tests = {}
  standard_tests = {}

  for ROOT, DIRS, FILES in os.walk(dir_tests):
    for basename in FILES:
      if not basename.endswith(".py") or not basename.startswith("test"):
        continue
      test_file = paths.join(ROOT, basename)
      if os.path.isdir(test_file):
        continue
      test_name = test_file[len(dir_tests)+1:-3].replace(os.sep, ".")
      if test_name.startswith("introspect."):
        introspect_tests[test_name] = test_file
      else:
        standard_tests[test_name] = test_file

  print()
  logger.info("running introspection tests (failure is ok) ...")
  for test_name in introspect_tests:
    # for debugging, it is ok if these tests fail
    res, err = runTest(test_name, introspect_tests[test_name], verbose=options.verbose)
    logger.info("result: {}, message: {}".format(res, err))
  print()
  logger.info("running standard tests ...")
  for test_name in standard_tests:
    res, err = runTest(test_name, standard_tests[test_name], verbose=options.verbose)
    if res != 0:
      exitWithError("{}: failed".format(test_name), res)
    else:
      logger.info("{}: OK".format(test_name))

def addTask(name, action, desc):
  tasks.add(name, action)
  task_list[name] = desc

def initTasks():
  addTask("stage", taskStage, "Prepare files for installation or distribution.")
  addTask("stage-source", taskStageSource, "Prepare source files for distribution.")
  addTask("install", taskInstall, "Install files to directory specified by `--prefix`" \
      + " argument.")
  addTask("uninstall", taskUninstall, "Uninstall files from directory specified by" \
      + " `--prefix` argument.")
  addTask("dist-source", taskDistSource, "Build a source distribution package.")
  addTask("dist-bin", taskDistBin, "Build a portable binary .zip distribution package.")
  addTask("dist-deb", taskDistDeb, sgr("Build a binary Debian distribution package." \
      + " Requires <bold>debuild</bold> (<em>apt install devscripts</em>)."))
  addTask("deb-source", taskDebSource,
      "Build a signed Debian source package for uploading to repo or PPA.")
  addTask("docs", taskBuildDocs, sgr("Build documentation using <bold>Doxygen</bold>."))
  addTask("clean", taskClean, "Remove all temporary build files.")
  addTask("clean-stage", taskCleanStage, "Remove temporary build files from" \
      + " 'build/stage' directory.")
  addTask("clean-deb", taskCleanDeb, "Remove temporary build files from 'debian'" \
      + " directory.")
  addTask("clean-dist", taskCleanDist, "Remove built packages from 'build/dist'" \
      + " directory.")
  addTask("update-version", taskUpdateVersion, "Update relevant files with version" \
      + " information from 'build.conf'.")
  addTask("run-tests", taskRunTests, "Run configured unit tests from 'tests' directory.")
  addTask("test", taskRunTests, sgr("Alias of <bold>run-tests</bold>."))
  addTask("check-code", taskCheckCode, "Check code with pylint & mypy.")
  addTask("check", taskCheckCode, sgr("Alias of <bold>check-code</bold>."))
  addTask("changes", taskPrintChanges, "Print most recent changes from 'doc/changelog'" \
      + " to stdout.")
  addTask("changes-deb", taskPrintChangesDeb, "Print most recent changes from"
      + "'doc/changelog' in Debianized format to stdout.")

# --- configuration & command line options --- #

def initOptions(aparser):
  task_help = []
  for t in task_list:
    task_help.append(sgr("<bold>{}</bold>: {}".format(t, task_list[t])))

  log_levels = []
  for level in LogLevel.getLevels():
    log_levels.append(sgr("<bold>{}) {}</bold>").format(level, LogLevel.toString(level).lower()))

  aparser.add_argument("-h", "--help", action="help",
      help="Show help information.")
  aparser.add_argument("-v", "--version", action="store_true",
      help="Show Debreate version.")
  aparser.add_argument("-V", "--verbose", action="store_true",
      help="Include detailed task information when printing to stdout.")
  aparser.add_argument("-l", "--log-level", metavar="<level>",
      default=LogLevel.toString(LogLevel.getDefault()).lower(),
      help="Logging output verbosity.\n  " + "\n  ".join(log_levels))
  aparser.add_argument("-t", "--task", metavar="<task1>[,<task2>...]",
      help="\n".join(task_help))
  aparser.add_argument("-p", "--prefix", metavar="<dir>", default=paths.getSystemRoot() + "usr",
      help="Path prefix to directory where files are to be installed.")
  aparser.add_argument("-d", "--dir", metavar="<dir>", default=paths.getSystemRoot(),
      help="Target directory (defaults to system root). This is useful for directing the script" \
          + " to place the files in a temporary directory, rather than the intended installation" \
          + " path.")


# --- execution insertion point --- #

def main():
  global dir_app
  dir_app = paths.getAppDir()

  # ensure current working directory is app location
  os.chdir(dir_app)

  # handle command line input
  aparser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="Debreate installer script",
      add_help=False)

  global options, printUsage, task_list
  task_list = {}
  initTasks()
  initOptions(aparser)
  printUsage = aparser.print_help
  options = aparser.parse_args()

  err = LogLevel.check(options.log_level)
  if isinstance(err, Exception):
    sys.stderr.write(sgr("<red>ERROR: {}</fg>\n".format(err)))
    print()
    aparser.print_help()
    exit(1)

  # set logger level before calling config functions
  logger.setLevel(options.log_level)

  global cfg
  cfg = config.add("build", paths.join(dir_app, "build.conf"))

  global package_name, package_version, package_version_dev, package_version_full
  package_name = cfg.getValue("package")
  package_version = cfg.getValue("version")
  package_version_dev = 0
  tmp = cfg.getValue("version_dev")
  if tmp:
    package_version_dev = int(tmp)
  package_version_full = package_version
  if package_version_dev > 0:
    package_version_full = "{}-dev{}".format(package_version_full, package_version_dev)
  aparser.version = package_version_full

  if options.version:
    print(aparser.version)
    exit(0)

  if not options.task:
    exitWithError("task argument not supplied", usage=True)
  t_ids = options.task.split(",")
  # check all request task IDs
  for _id in t_ids:
    if not _id in task_list:
      exitWithError("unknown task ({})".format(options.task), usage=True)
  # run tasks
  for _id in t_ids:
    err = tasks.run(_id)
    if err != 0:
      sys.exit(err)

if __name__ == "__main__":
  main()
