
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

# library for handling .dbr project files

import codecs
import errno
import os

from libdebreate   import appinfo
from libdbr        import fileio
from libdbr.logger import Logger


standards_defaults = {
  "app": appinfo.getVersion(),
  "config": (0, 9) # assume legacy
}

class DBRFile:
  logger = None

  # buffer for reading files
  chunksize = 512
  # 'app' & 'config' config versions parsed from project file
  standards = {
    "app": None,
    "config": None
  }


  def __init__(self, filepath=None):
    if not DBRFile.logger:
      DBRFile.logger = Logger(DBRFile.__name__)

    self.dirty = False
    self.project_data = {}
    self.setFile(filepath)

    # detectected standard & app versions from project file
    self.dbr_standard = None
    self.app_version = None

  ## Sets location of project file.
  #
  #  @param filepath
  #    Path to file for opened project.
  def setFile(self, filepath):
    self.filepath = filepath

  ## Retrieves project file.
  #
  #  @return
  #    Path to project file if configured.
  def getFile(self):
    return self.filepath

  ## Retrieves the dirty state of the project.
  #
  #  @return
  #    True if changes have been made without saving.
  def isDirty(self):
    return self.dirty

  ## Sets saved state of project.
  def __onChanged(self):
    self.dirty = True

  ## Unsets dirty state when projed is saved.
  def __onSaved(self):
    self.dirty = False

  ## Formats project file data into readable dictionary.
  #
  #  @param data
  #    Raw text data to be parsed.
  def __parseProjectData(self, data):
    pass

  ## Formats project data dictionary into text for file export.
  #
  #  @return
  #    Text representation of entire project.
  def __formatProjectData(self):
    # TODO:
    return ""

  ## Loads project information from file.
  #
  #  @return
  #    Error code & message.
  def load(self):
    if self.filepath == None:
      return 1, "project file not set, use {}.{}".format(__name__, self.setFile.__name__)
    if os.path.isdir(self.filepath):
      return errno.EISDIR, "cannot open project, target is a directory: '{}'".format(self.filepath)
    if not os.path.isfile(self.filepath):
      return errno.ENOENT, "cannot open project, target does not exist: '{}'".format(self.filepath)
    self.__parseProjectData(fileio.readFile(self.filepath))
    return 0, None

  ## Writes project information to file.
  #
  #  @return
  #    Error code & message.
  def save(self):
    if self.filepath == None:
      return 1, "project file not set, use {}.{}".format(__name__, self.setFile.__name__)
    data = self.__formatProjectData()
    err, msg = fileio.writeFile(self.filepath, data)
    # FIXME: libdbr.fileio.writeFile should return an integer
    if type(err) == bool:
      err = 0 if err else 1
    if err != 0:
      return err, msg
    return 0, None

  ## Reads version information from project file.
  #
  #  The first lines in a project file should formatted as:
  #    [APP-version]
  #    [CONFIG-version]
  def __cacheStandards(self):
    if self.filepath == None or not os.path.isfile(self.filepath):
      return
    with codecs.open(self.filepath, "r", "utf-8") as fin:
      data = fin.read(self.chunksize)
      idx_start, idx_end = 0, 0
      for marker in self.standards:
        if self.standards[marker]:
          # don't re-cache
          continue
        try:
          idx_start, idx_end = data.index("[", idx_start), data.index("]", idx_end)
        except ValueError:
          continue
        tmp = data[idx_start+1:idx_end].split("-", 1)
        sname = tmp[0].lower()
        if sname in ("app", "debreate"):
          sname = "app"
        if sname not in self.standards:
          # ignore unknown tags
          continue
        st = []
        if len(tmp) > 1:
          for v in tmp[1].split("."):
            if "-" in v:
              v = v.split("-", 1)[0]
            st.append(int(v))
        self.standards[sname] = tuple(st)
        idx_start = idx_end + 1
        idx_end = idx_start + 1
      fin.close()

    if Logger.debugging():
      self.logger.debug("parsed app standard: {}".format(self.standards["app"]))
      self.logger.debug("parsed config standard: {}".format(self.standards["config"]))

    # defaults if couldn't be parsed from project file
    # ~ global __standards_defaults
    if not self.standards["app"]:
      self.standards["app"] = standards_defaults["app"]
    if not self.standards["config"]:
      self.standards["config"] = standards_defaults["config"]

  ## Retrieves writing app version from project file.
  #
  #  @return
  #    Version number of app that created file.
  def getAppVersion(self):
    if not self.standards["app"]:
      self.__cacheStandards()
    if not self.standards["app"]:
      # fallback to current app standard
      self.standards["app"] = list(appinfo.getVersion())
    if Logger.debugging:
      self.logger.debug("app standard: {}".format(self.standards["app"]))
    return self.standards["app"]

  ## Retrieves standard that project file is written with.
  #
  #  @return
  #    Standard version.
  def getDBRStandard(self):
    if not self.standards["config"]:
      self.__cacheStandards()
    if not self.standards["config"]:
      # fallback to current config standard
      self.standards["config"] = list(appinfo.getDBRStandard())
    if Logger.debugging():
      self.logger.debug("config standard: {}".format(self.standards["config"]))
    return self.standards["config"]

  ## Retrieves a section from project file.
  #
  #  Config sections:
  #  - Section opening tags are marked between double left angle brackes followed by '+' (<<+) &
  #    double right angle brackets (>>).
  #  - Section closing tags are marked between double left angle brackets followed by '-' (<<-) &
  #  double right angle brackets (>>).
  #  - Section tags must start at the beginning of a line. E.g., "<<+foobar>>" is valid,
  #    " <<+foobar>>" is not.
  #
  #  Legacy config sections:
  #  - Legacy section opening tags are marked between double left angle brackets (<<) & double right
  #    angle brackets (>>).
  #  - Legacy section closing tags are marked between double left angle brackets follows by a
  #    forward slash (<</) & double right angle brackets (>>).
  #  - Legacy section tags must start at the beginning of a line. E.G., "<<foobar>>" is valid,
  #    " <<foobar>>" is not.
  #
  #  @param sname
  #    Section name to parse.
  def parseSection(self, sname):
    chunk_offset = 1
    # TODO:
