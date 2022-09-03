## \package globals.cmdcheck

# MIT licensing
# See: docs/LICENSE.txt


import subprocess


## Check if a command is available on the system
#
#  The system's 'whereis' command is used to
#    find locations for the target command.
#    If one of those locations is found to
#    be an executable file, a tuple containing
#    a True value & the location to the executable
#    is returned.
#  \param cmd
#        \b \e str : Command to check for
#  \return
#        \b \e str|None : A string path to executable or None if not found
def CommandExists(cmd):
    res = subprocess.run(["which", cmd], capture_output=True)

    if res.returncode == 0:
        return res.stdout.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")[0]

    return None
