# -*- coding: utf-8 -*-

## \package globals.threads
#  
#  WARNING: Standard Python module 'threads' cannot be imported here

# MIT licensing
# See: docs/LICENSE.txt


import threading

from dbr.log import Logger


thr = threading


## Standard thread class with renamed methods
class Thread(thr.Thread):
    def __init__(self, function, *args):
        thr.Thread.__init__(self, target=function, args=args)
        
        self.Active = False
        # TODO: Retrieve target exit value
        self.ExitVal = None
    
    
    def __del__(self):
        Logger.Debug(__name__, u'Destroying Thread instance; Thread is active: {}'.format(self.IsActive()))
    
    
    ## Exits the thread & sets inactive
    #
    #  Alias of globals.threads.Thread.Join
    def Exit(self):
        return self.Join()
    
    
    ## Retrieves the thread identifier
    def GetId(self):
        return self.ident
    
    ## Tests if thread is active
    def IsActive(self):
        return self.Active
    
    
    ## Exits the thread & sets inactive
    def join(self):
        if self.IsActive():
            Logger.Debug(__name__, u'Joining thread ...')
            
            thr.Thread.join(self)
            self.Active = False
    
    
    ## Exits the thread & sets inactive
    #
    #  Alias of globals.threads.Thread.join
    def Join(self):
        return self.join()
    
    
    ## Executes target under new thread
    def start(self):
        try:
            thr.Thread.start(self)
            self.Active = True
        
        # Do not try to restart thread if already started
        except RuntimeError:
            Logger.Debug(__name__, u'ThreadStart: Thread is active, cannot restart')
            
            # In case active state has been changed
            self.Active = True
            
            pass
        
        return self.IsActive()
    
    
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
