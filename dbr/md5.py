# -*- coding: utf-8 -*-

# Writing the md5sums file


import commands, os


## Object for creating MD5 hashes
class MD5Hasher:
    def __init__(self):
        pass
    
    
    def IsExecutable(self, filename):
        # Find out if the file is an executable
        executable = os.access(filename, os.X_OK) #another python version
        
        return bool(executable)
    
    
    def WriteMd5(self, builddir, tempdir):
        tempdir = tempdir.encode(u'utf-8')
        os.chdir(builddir)
        
        temp_list = []
        md5_list = [] # Final list used to write the md5sum file
        for ROOT, DIRS, FILES in os.walk(tempdir):
            for F in FILES:
                F = u'{}/{}'.format(ROOT, F)
                md5 = commands.getoutput((u'md5sum -t "{}"'.format(F)))
                temp_list.append(md5)
        
        for item in temp_list:
            # Remove [tempdir] from the path name in the md5sum so that it has a
            # true unix path
            # e.g., instead of "/myfolder_temp/usr/local/bin", "/usr/local/bin"
            sum_split = item.split(u'{}/'.format(tempdir))
            sum_join = u''.join(sum_split)
            md5_list.append(sum_join)
        
        FILE_BUFFER = open(u'{}/DEBIAN/md5sums'.format(tempdir), u'w')  # Create the md5sums file in the "DEBIAN" directory
        FILE_BUFFER.write(u'{}\n'.format(u'\n'.join(md5_list)))  # Write the final list to the file
        FILE_BUFFER.close() # Save the file
