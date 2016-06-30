import os.path

from django.conf import settings
from django.utils.encoding import force_text, force_bytes

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


def _convert_file_to_url(filename):
    relpath = os.path.relpath(filename, settings.SENDFILE_ROOT)

    url = [settings.SENDFILE_URL]

    while relpath:
        relpath, head = os.path.split(relpath)
        url.insert(1, head)

    # Python3 urllib.parse.quote accepts both unicode and bytes, while Python2 urllib.quote only accepts bytes.
    # So force bytes for quoting and then go back to unicode.
    url = [force_bytes(url_component) for url_component in url]
    return force_text(quote(b'/'.join(url)))
