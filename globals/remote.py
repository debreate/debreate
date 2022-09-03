## \package globals.remote

# MIT licensing
# See: docs/LICENSE.txt


from urllib.error   import HTTPError
from urllib.error   import URLError
from urllib.request import urlopen


def GetRemotePageText(remote_url):
    try:
        URL_BUFFER = urlopen(remote_url)
        page_text = URL_BUFFER.read()
        URL_BUFFER.close()

        return page_text

    except HTTPError or URLError:
        return None
