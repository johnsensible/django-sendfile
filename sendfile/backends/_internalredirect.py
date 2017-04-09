import os.path

from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.utils.six.moves.urllib.parse import quote


def _convert_file_to_url(filename):
    relpath = os.path.relpath(filename, settings.SENDFILE_ROOT)

    url = [settings.SENDFILE_URL]

    while relpath:
        relpath, head = os.path.split(relpath)
        url.insert(1, head)

    # Python3 urllib.parse.quote accepts both unicode and bytes, while Python2 urllib.quote only accepts bytes.
    # So use bytes for quoting and then go back to unicode.
    url = [force_bytes(url_component) for url_component in url]
    return force_text(quote(b'/'.join(url)))
