# -*- coding: utf-8 -*-

## \package dbr.compression


# system modules
import wx, os, tarfile, zipfile, commands

# local modules
from dbr.constants          import custom_errno


# *** Compression Format IDs *** #
ID_COMPRESSION = wx.NewId() # FIXME: Unused?
ID_ZIP_NONE = wx.NewId()
ID_ZIP_GZ = wx.NewId()
ID_ZIP_BZ2 = wx.NewId()
ID_ZIP_XZ = wx.NewId()
ID_ZIP_ZIP = wx.NewId()

DEFAULT_COMPRESSION_ID = ID_ZIP_BZ2

compression_formats = {
    ID_ZIP_NONE: u'tar',
    ID_ZIP_GZ: u'gz',
    ID_ZIP_BZ2: u'bz2',
    ID_ZIP_XZ: u'xz',
    ID_ZIP_ZIP: u'zip',
}

compression_mimetypes = {
    u'application/x-tar': ID_ZIP_NONE,
    u'application/gzip': ID_ZIP_GZ,
    u'application/x-bzip2': ID_ZIP_BZ2,
    u'application/x-xz': ID_ZIP_XZ,
    u'application/zip': ID_ZIP_ZIP,
}


def GetCompressionId(z_value):
    for z_id in compression_formats:
        if z_value == compression_formats[z_id]:
            return z_id
    
    # FIXME: Can't import Logger
    #Logger.Debug(__name__, GT(u'Compression ID not found for "{}" value'.format(z_value)))
    
    return None


class CompressionHandler:
    def __init__(self, compression_id):
        
        self.compression_id = compression_id
        
        self.tarfile_handlers = (
            ID_ZIP_NONE,
            ID_ZIP_GZ,
            ID_ZIP_BZ2,
        )
        
        self.zipfile_handlers = (
            ID_ZIP_ZIP,
        )
        
        self.system_handlers = {
            ID_ZIP_XZ: u'J',
        }
    
    
    def Compress(self, source_path, target_name):
        if os.path.isdir(source_path):
            compressto = u'w'
            
            if self.compression_id in self.tarfile_handlers:
                if self.compression_id != ID_ZIP_NONE:
                    compressto = u'{}:{}'.format(compressto, compression_formats[self.compression_id])
                
                archive = tarfile.open(target_name, compressto)
                
                for PATH, DIRS, FILES in os.walk(source_path):
                    for F in FILES:
                        archive.add(u'{}/{}'.format(PATH, F), arcname=F)
                
                archive.close()
                return 0
            
            elif self.compression_id in self.zipfile_handlers:
                archive = zipfile.ZipFile(target_name, compressto)
                
                for PATH, DIRS, FILES in os.walk(source_path):
                    for F in FILES:
                        archive.write(u'{}/{}'.format(PATH, F), arcname=F)
                
                archive.close()
                return 0
            
            elif self.compression_id in self.system_handlers:
                compresswith = self.system_handlers[self.compression_id]
                
                work_dir = os.getcwd()
                os.chdir(source_path)
                
                tar_output = commands.getstatusoutput(u'tar -c{}f "{}" *'.format(compresswith, target_name))
                
                os.chdir(work_dir)
                
                return tar_output[0]
            
            else:
                return custom_errno.ENOEXEC
        
        return custom_errno.ENOENT
    
    
    def GetCompressionFormat(self):
        return compression_formats[self.compression_id]
    
    
    def GetCompressionMimetype(self):
        for MIME in compression_mimetypes:
            if compression_mimetypes[MIME] == self.compression_id:
                return MIME
    
    
    def Uncompress(self, source_file, target_dir):
        if not os.path.isfile(source_file):
            return custom_errno.ENOENT
        
        if not os.access(target_dir, os.W_OK):
            return custom_errno.EACCES
        
        z_format = u'r'
        
        if self.compression_id in self.tarfile_handlers:
            if self.compression_id != ID_ZIP_NONE:
                z_format = u'{}:{}'.format(z_format, compression_formats[self.compression_id])
            
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
            
            tar_output = commands.getstatusoutput(u'tar -xJf "{}"'.format(source_file, target_dir))
            
            os.chdir(prev_dir)
            
            return tar_output
        
        return custom_errno.ENOEXEC
