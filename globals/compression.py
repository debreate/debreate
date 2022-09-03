## \package globals.compression


import os, subprocess, tarfile, zipfile

from dbr.language       import GT
from dbr.log            import Logger
from globals            import ident as ID
from globals.errorcodes import errno


DEFAULT_COMPRESSION_ID = ID.ZIP_BZ2

compression_formats = {
  ID.ZIP_NONE: "tar",
  ID.ZIP_GZ: "gz",
  ID.ZIP_BZ2: "bz2",
  ID.ZIP_XZ: "xz",
  ID.ZIP_ZIP: "zip",
}

compression_mimetypes = {
  "application/x-tar": ID.ZIP_NONE,
  "application/gzip": ID.ZIP_GZ,
  "application/x-bzip2": ID.ZIP_BZ2,
  "application/x-xz": ID.ZIP_XZ,
  "application/zip": ID.ZIP_ZIP,
}


def GetCompressionId(z_value):
  for z_id in compression_formats:
    if z_value == compression_formats[z_id]:
      return z_id

  Logger.Debug(__name__, GT("Compression ID not found for \"{}\" value".format(z_value)))

  return None


class CompressionHandler:
  def __init__(self, compression_id):

    self.compression_id = compression_id

    self.tarfile_handlers = (
      ID.ZIP_NONE,
      ID.ZIP_GZ,
      ID.ZIP_BZ2,
    )

    self.zipfile_handlers = (
      ID.ZIP_ZIP,
    )

    self.system_handlers = {
      ID.ZIP_XZ: "J",
    }


  def Compress(self, source_path, target_name):
    if os.path.isdir(source_path):
      compressto = "w"

      if self.compression_id in self.tarfile_handlers:
        if self.compression_id != ID.ZIP_NONE:
          compressto = "{}:{}".format(compressto, compression_formats[self.compression_id])

        archive = tarfile.open(target_name, compressto)

        for PATH, DIRS, FILES in os.walk(source_path):
          for F in FILES:
            archive.add("{}/{}".format(PATH, F), arcname=F)

        archive.close()
        return 0

      elif self.compression_id in self.zipfile_handlers:
        archive = zipfile.ZipFile(target_name, compressto)

        for PATH, DIRS, FILES in os.walk(source_path):
          for F in FILES:
            archive.write("{}/{}".format(PATH, F), arcname=F)

        archive.close()
        return 0

      elif self.compression_id in self.system_handlers:
        compresswith = self.system_handlers[self.compression_id]

        work_dir = os.getcwd()
        os.chdir(source_path)

        res = subprocess.run(["tar", "-c{}f".format(compresswith), target_name, "*"], capture_output=True)
        tar_output = (res.returncode, res.stdout.decode("utf-8"))

        os.chdir(work_dir)

        return tar_output[0]

      else:
        return errno.ENOEXEC

    return errno.ENOENT


  def GetCompressionFormat(self):
    return compression_formats[self.compression_id]


  def GetCompressionMimetype(self):
    for MIME in compression_mimetypes:
      if compression_mimetypes[MIME] == self.compression_id:
        return MIME


  def Uncompress(self, source_file, target_dir):
    if not os.path.isfile(source_file):
      return errno.ENOENT

    if not os.access(target_dir, os.W_OK):
      return errno.EACCES

    z_format = "r"

    if self.compression_id in self.tarfile_handlers:
      if self.compression_id != ID.ZIP_NONE:
        z_format = "{}:{}".format(z_format, compression_formats[self.compression_id])

      archive = tarfile.open(source_file, z_format)
      archive.extractall(target_dir)
      archive.close()

      return 0

    elif self.compression_id in self.zipfile_handlers:
      archive = zipfile.ZipFile(source_file, z_format)
      archive.extractall(target_dir)
      archive.close()

      return 0

    elif self.compression_id in self.system_handlers:
      z_format = self.system_handlers[self.compression_id]

      prev_dir = os.getcwd()
      os.chdir(target_dir)

      tar_output = subprocess.run(["tar", "-xJf", source_file], capture_output=True).stdout.decode("utf-8")

      os.chdir(prev_dir)

      return tar_output

    return errno.ENOEXEC
