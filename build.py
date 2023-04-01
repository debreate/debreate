#!/usr/bin/env python3

# This file is part of the Debreate Debian Package Builder software.
#
# MIT licensing
# See: docs/LICENSE.txt

import argparse, codecs, errno, gzip, os, re, shutil, subprocess, sys, types

if sys.platform == "win32":
  import ctypes

# update module search path to include local 'lib' directory
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "lib")))

dir_root = os.path.normpath(os.path.dirname(__file__))

package_name = "debreate"
package_version = 0.8


# --- misc. functions --- #

def log(lvl="", msg=None):
  if msg == None:
    msg = lvl
    lvl = "info"
  lvl = lvl.lower()
  if lvl == "error":
    print("ERROR: {}".format(msg))
  elif lvl == "warn":
    print("WARNING: {}".format(msg))
  elif lvl == "info":
    if not options.quiet:
      print(msg)
  else:
    print("ERROR: unknown log level: {}".format(lvl))

print_help: types.FunctionType


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
  args_parser.add_argument("-d", "--dir", default=getSystemRoot(), help="Installation target root directory.")
  args_parser.add_argument("-p", "--prefix", help="Installation prefix.")
  return args_parser

def parseConfig(path):
  if not os.path.exists(path):
    print("ERROR: cannot read config, file does not exist: {}".format(path))
    sys.exit(errno.ENOENT)
  if os.path.isdir(path):
    print("ERROR: cannot read config, target is a directory: {}".format(path))
    sys.exit(errno.EISDIR)

  fopen = codecs.open(path, "r", "utf-8")
  lines = fopen.read().replace("\r\n", "\n").replace("\r", "\n").split("\n")
  fopen.close()

  conf = {}
  for lineidx in range(len(lines)):
    l = lines[lineidx]
    line = l.strip()
    if not line or line.startswith("#"):
      continue
    if not "=" in line:
      print("ERROR: malformed line in configuration ({}:{}): \"{}\"".format(path, lineidx+1, l))
      sys.exit(1)
    tmp = line.split("=", 1)
    key = tmp[0].strip()
    if not key:
      log("error", "malformed line in configuration ({}:{}): \"{}\"".format(path, lineidx+1, l))
      sys.exit(1)
    if key.startswith("dirs_") or key.startswith("files_") or ";" in tmp[1]:
      value = []
      for v in tmp[1].split(";"):
        v = v.strip()
        if v:
          value.append(v)
      value = tuple(value)
    else:
      value = tmp[1].strip()
    if not value:
      log("warn", "configuration key without value ({}:{}): \"{}\"".format(path, lineidx+1, l))
    else:
      conf[key] = value

  return conf

class Config:
  def __init__(self, conf):
    self.conf = conf

  def get(self, key, default=None):
    if key in self.conf:
      return self.conf[key]
    if default != None:
      return default
    log("error", "unknown configuration key: {}".format(key))
    sys.exit(1)

# --- helper functions --- #

def getSystemRoot():
  sys_root = "/"
  if sys.platform == "win32":
    sys_root = os.getenv("SystemDrive") or "C:"
    sys_root += "\\"
  return sys_root

def checkAdmin():
  if sys.platform == "win32":
    return ctypes.windll.shell32.IsUserAnAdmin() != 0
  else:
    return os.getuid() == 0

def joinPath(*paths):
  path = ""
  for p in paths:
    path = os.path.join(path, p)
  return os.path.normpath(path)

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
    log("error", "cannot write to directory, file exists: {}".format(dir_target))
    sys.exit(errno.EEXIST)
  while _dir.strip() and not os.path.isdir(_dir):
    _dir = os.path.dirname(_dir)
  if not os.access(_dir, os.W_OK):
    log("error", "cannot write to directory, insufficient permissions: {}".format(_dir))
    sys.exit(errno.EACCES)

def checkWriteFile(_file):
  checkWriteTree(os.path.dirname(_file))
  if os.path.isfile(_file) and not os.access(_file, os.W_OK):
    log("error", "cannot overwrite file, insufficient permissions: {}".format(_file))
    sys.exit(errno.EACCES)

def checkReadFile(_file):
  if not os.path.isfile(_file):
    log("error", "cannot read file, does not exist: {}".format(_file))
  if not os.access(_file, os.R_OK):
    log("error", "cannot read file, insufficient permissions: {}".format(_file))

def makeDir(_dir):
  if not os.path.exists(_dir):
    os.makedirs(_dir)

def installFile(file_source, dir_target, name=None, perm=0o664):
  file_source = os.path.normpath(file_source)
  dir_target = os.path.normpath(dir_target)
  if os.path.isdir(file_source):
    log("error", "cannot copy file, source is a directory: {}".format(file_source))
    sys.exit(errno.EISDIR)
  name = os.path.basename(file_source) if not name else name
  file_target = os.path.join(dir_target, name)
  checkWriteFile(file_target)
  makeDir(dir_target)
  # delete old file so we can check if new copy succeeded
  if os.path.isfile(file_target):
    os.remove(file_target)
  shutil.copy(file_source, file_target)
  if not os.path.isfile(file_target):
    log("error", "an unknown error occurred while trying to copy file: {}".format(file_target))
    sys.exit(errno.ENOENT)
  os.chmod(file_target, perm)
  log("'{}' -> '{}' (perm={})".format(file_source, file_target, oct(perm).lstrip("0o")))

def installExecutable(file_source, dir_target, name=None):
  installFile(file_source, dir_target, name, 0o775)

def installDir(dir_source, dir_target, name=None, _filter=""):
  dir_source = os.path.normpath(dir_source)
  dir_target = os.path.normpath(dir_target)
  if os.path.isfile(dir_source):
    log("error", "cannot copy directory, source is a file: {}".format(dir_source))
    sys.exit(errno.ENOTDIR)
  if not os.path.isdir(dir_source):
    log("error", "source directory not found: {}".format(dir_source))
    sys.exit(errno.ENOENT)
  name = os.path.basename(dir_source) if not name else name
  path_target = joinPath(dir_target, name)
  for basename in os.listdir(dir_source):
    absname = os.path.join(dir_source, basename)
    if os.path.isfile(absname):
      if re.search(_filter, basename):
        installFile(absname, path_target)
    elif os.path.isdir(absname):
      installDir(absname, path_target, None, _filter)

def uninstallFile(file_target):
  file_target = os.path.normpath(file_target)
  if not os.path.isfile(file_target):
    return
  checkWriteFile(file_target)
  if os.path.isfile(file_target) or os.path.islink(file_target):
    os.remove(file_target)
  if os.path.isfile(file_target):
    log("error", "failed to remove file: {}".format(file_target))
  else:
    log("deleted file -> '{}'".format(file_target))

def uninstallDir(dir_target):
  dir_target = os.path.normpath(dir_target)
  if os.path.isfile(dir_target):
    log("error", "cannot delete directory, target is a file: {}".format(dir_target))
    sys.exit(errno.ENOTDIR)
  if not os.path.isdir(dir_target):
    return

  for basename in os.listdir(dir_target):
    absname = os.path.join(dir_target, basename)
    if os.path.isfile(absname) or os.path.islink(absname):
      uninstallFile(absname)
    elif os.path.isdir(absname):
      uninstallDir(absname)

  try:
    if len(os.listdir(dir_target)) == 0:
      os.rmdir(dir_target)
    if os.path.isdir(dir_target):
      raise OSError
    else:
      log("deleted directory -> '{}'".format(dir_target))
  except:
    log("error", "an unknown error occurred while trying to remove directory: {}".format(dir_target))

def writeFile(file_target, file_data, binary=False, perm=0o664):
  file_target = os.path.normpath(file_target)
  checkWriteFile(file_target)
  if os.path.lexists(file_target):
    os.remove(file_target)
  else:
    makeDir(os.path.dirname(file_target))

  if binary:
    fopen = codecs.open(file_target, "wb")
  else:
    fopen = codecs.open(file_target, "w", "utf-8")
  fopen.write(file_data)
  fopen.close()

  if not os.path.isfile(file_target):
    log("error", "an unknown error occurred while trying to create file: {}".format(file_target))
    sys.exit(errno.ENOENT)
  os.chmod(file_target, perm)
  log("new file -> '{}' (perm={})".format(file_target, oct(perm).lstrip("0o")))

def createFileLink(file_source, link_target):
  file_source = os.path.normpath(file_source)
  link_target = os.path.normpath(link_target)
  checkWriteFile(link_target)
  if os.path.lexists(link_target):
    os.unlink(link_target)
  else:
    makeDir(os.path.dirname(link_target))

  if sys.platform == "win32" and not checkAdmin():
    log("error", "administrator privileges required on Windows platform to create symbolic links")
    sys.exit(1)
  os.symlink(file_source, link_target)
  if not os.path.islink(link_target):
    log("error", "an unknown error occurred while trying to create symbolic link: {}".format(link_target))
    sys.exit(errno.ENOENT)
  log("new link -> '{}' ({})".format(link_target, file_source))

def compressFile(file_source, file_target):
  file_source = os.path.normpath(file_source)
  checkReadFile(file_source)

  fropen = codecs.open(file_source, "rb")
  file_data = fropen.read()
  fropen.read()

  writeFile(file_target, gzip.compress(file_data), binary=True)


# --- install targets --- #

config: Config

def targetInstallApp():
  log()
  log("installing app files ...")

  dirs_main = config.get("dirs_main")
  files_main = config.get("files_main")

  dir_target = getDataDir()
  for _dir in dirs_main:
    installDir(os.path.join(dir_root, _dir), dir_target, _filter="\.py$")
  for _file in files_main:
    installFile(os.path.join(dir_root, _file), dir_target)
  installExecutable(os.path.join(dir_root, config.get("executable")), dir_target)
  createFileLink(os.path.join(getDataDir(stripped=True), config.get("executable")), os.path.join(getBinDir(), package_name))

def targetInstallData():
  log()
  log("installing data files ...")

  dirs_data = config.get("dirs_data")
  dir_target = getDataDir()
  for _dir in dirs_data:
    installDir(os.path.join(dir_root, _dir), dir_target)
  writeFile(os.path.join(dir_target, "INSTALLED"), "prefix={}".format(options.prefix))

def targetInstallDoc():
  log()
  log("installing doc files ...")

  files_doc = config.get("files_doc")
  dir_target = getDocDir()
  for _file in files_doc:
    installFile(os.path.join(dir_root, _file), dir_target)
  # ~ dir_target = os.path.join(getDataDir(), "docs")
  # ~ for _file in ("changelog", "LICENSE.txt"):
    # ~ file_source = os.path.join(getDocDir(stripped=True), _file)
    # ~ link_target = os.path.join(dir_target, _file)
    # ~ createFileLink(file_source, link_target)

  files_man = config.get("files_man")
  for _file in files_man:
    file_man = os.path.basename(_file)
    dir_man = getManDir(os.path.basename(os.path.dirname(_file)))
    compressFile(os.path.join(dir_root, _file), os.path.join(dir_man, file_man + ".gz"))

def targetInstallLocale():
  log()
  log("installing locale files ...")
  # TODO:

def targetInstallMimeInfo(install=True):
  log()
  msg = "installing mime type files ..."
  if not install:
    msg = "un" + msg
  log(msg)

  mime_prefix = config.get("dbp_mime_prefix")
  mime_type = config.get("dbp_mime")
  dir_conf = joinPath(getInstallPath(), "share/mime/packages")
  dir_icons = joinPath(getIconsDir(), "scalable/mimetype")
  mime_conf = joinPath(dir_root, "data/mime/{}.xml".format(package_name))
  mime_icon = joinPath(dir_root, "data/svg", mime_prefix + "-" + mime_type + ".svg")
  if install:
    installFile(mime_conf, dir_conf)
    installFile(mime_icon, dir_icons)
  else:
    uninstallFile(joinPath(dir_conf, package_name + ".xml"))
    uninstallFile(joinPath(dir_icons, mime_prefix + "-" + mime_type + ".svg"))

def targetInstall():
  if options.prefix == None:
    log("error", "'prefix' option is required for 'install' target.")
    log()
    print_help()
    sys.exit(errno.EINVAL)

  log()
  log("installing ...")

  targetInstallApp()
  targetInstallData()
  targetInstallDoc()
  targetInstallLocale()
  targetInstallMimeInfo()

def targetUninstall():
  if options.prefix == None:
    log("error", "'prefix' option is required for 'uninstall' target.")
    log()
    print_help()
    sys.exit(errno.EINVAL)

  log()
  log("uninstalling ...")

  uninstallFile(os.path.join(getBinDir(), package_name))
  uninstallDir(getDataDir())
  uninstallDir(getDocDir())
  files_man = config.get("files_man")
  for _file in files_man:
    file_man = os.path.basename(_file) + ".gz"
    dir_man = getManDir(os.path.basename(os.path.dirname(_file)))
    uninstallFile(os.path.join(dir_man, file_man))

  # TODO: uninstall locale files

  targetInstallMimeInfo(False)

def targetDebClean():
  for _dir in ("debian/debreate", "debian/.debhelper"):
    uninstallDir(os.path.join(dir_root, os.path.normpath(_dir)))
  for _file in ("debian/debhelper-build-stamp", "debian/debreate.debhelper.log", "debian/debreate.substvars", "debian/files"):
    uninstallFile(os.path.join(dir_root, os.path.normpath(_file)))

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
  global options, config, print_help

  args_parser = parseCommandLine()
  print_help = args_parser.print_help
  options = args_parser.parse_args()
  if not options.dir:
    options.dir = getSystemRoot()
  config = Config(parseConfig(os.path.join(dir_root, "build.conf")))

  if options.target not in targets:
    log("error", "unknown target: \"{}\"".format(options.target))
    sys.exit(1)

  targets[options.target]()

if __name__ == "__main__":
  main()
