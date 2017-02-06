# -*- coding: utf-8 -*-

## \package globals.threads
#  
#  WARNING: Standard Python module 'threads' cannot be imported here

# MIT licensing
# See: docs/LICENSE.txt


import threading


thr = threading


## Standard thread class with renamed methods
class Thread(thr.Thread):
    def __init__(self, function, *args):
        thr.Thread.__init__(self, target=function, args=args)
        
        self.Active = False
    
    
    ## Retrieves the thread identifier
    def GetId(self):
        return self.ident
    
    ## Tests if thread is active
    def IsActive(self):
        return self.Active
    
    ## Alias for start method
    def Start(self):
        return self.start()


active_threads = []


## Creates a new thread for processing
#  
#  \return
#    \b \e Integer thread ID if successfully activated
def CreateThread(function, *args):
    global active_threads
    
    new_thread = Thread(function, args)
    thread_id = new_thread.GetId()
    
    if new_thread.IsActive() and thread_id not in active_threads:
        active_threads.append(thread_id)
        
        return thread_id
    
    return None


## Ends an active thread
#  
#  TODO: Define
#  \param thread_id
#    \b \e Integer ID of the thread to kill
#  \return
#    \b \e True if thread was successfully killed
def KillThread(thread_id):
    global active_threads
    
    if thread_id not in active_threads:
        return False
    
    # REMOVEME:
    return False
