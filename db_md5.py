# Writing the md5sums file
# -*- coding: utf-8 -*-

import os, stat, commands

class MD5():
    def __init__(self):
        #self.rootdir = rootdir # Set the working folder, same folder where deb is built
        pass
    
    def IsExecutable(self, file):
        # Find out if the file is an executable
#        executable = commands.getoutput("if [ -x %s ]\nthen echo true\nfi" % file)  #bash version
#        if executable == "true":
#        executable = stat.S_IXUSR & os.stat(file)[stat.ST_MODE]  #python version
        executable = os.access(file, os.X_OK) #another python version
        if executable:
            return True
        else:
            return False
    
    def WriteMd5(self, builddir, tempdir):
        tempdir = tempdir.encode('utf-8')
        os.chdir(builddir)

        temp_list = []
        md5_list = [] # Final list used to write the md5sum file
        for root, dirs, files in os.walk(tempdir):
            for file in files:
                file = "%s/%s" % (root, file)
#                if self.IsExecutable(file):
#                    md5 = commands.getoutput("md5sum -b \"%s\"" % file)
#                elif not self.IsExecutable(file):
                md5 = commands.getoutput(("md5sum -t \"%s\"" % file))
                temp_list.append(md5)
            
        for item in temp_list:
            # Remove [tempdir] from the path name in the md5sum so that it has a
            # true unix path
            # e.g., instead of "/myfolder_temp/usr/local/bin", "/usr/local/bin"
            sum_split = item.split("%s/" % tempdir)
            sum_join = "".join(sum_split)
            md5_list.append(sum_join)
        
        file = open("%s/DEBIAN/md5sums" % tempdir, "w")  # Create the md5sums file in the "DEBIAN" directory
        file.write("%s\n" % "\n".join(md5_list))  # Write the final list to the file
        file.close() # Save the file