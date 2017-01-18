# -*- coding: utf-8 -*-

## \package globals.containers

# MIT licensing
# See: docs/LICENSE.txt


## Tests if a container contains any of a list of items
def Contains(cont, items):
    if not isinstance(items, (tuple, list, dict)):
        return items in cont
    
    for ITEM in items:
        if ITEM in cont:
            return True
    
    return False
