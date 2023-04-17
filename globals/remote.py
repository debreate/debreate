
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.remote

from urllib.error   import HTTPError
from urllib.error   import URLError
from urllib.request import urlopen


## @todo Doxygen.
def GetRemotePageText(remote_url):
  try:
    URL_BUFFER = urlopen(remote_url)
    page_text = URL_BUFFER.read()
    URL_BUFFER.close()

    if type(page_text) == bytes:
        # convert to a string
        page_text = page_text.decode("utf-8")
    return page_text

  except (HTTPError, URLError):
    return None
