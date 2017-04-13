import os.path

from django.conf import settings
from django.utils.encoding import smart_text, smart_bytes

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


def _decision(fn):
    _cached_decision = []
    def _decorated():
        if not _cached_decision:
            _cached_decision.append(fn())
        return _cached_decision[0]
    return _decorated

@_decision
def should_be_quoted():
    backend = getattr(settings, 'SENDFILE_BACKEND', None)
    if backend == 'sendfile.backends.nginx':
        nginx_version = getattr(settings, 'NGINX_VERSION', None)
        if nginx_version:
            nginx_version = map(int, nginx_version.split('.'))
            # Since Starting with Nginx 1.5.9, quoted url's are expected to be
            # sent with X-Accel-Redirect headers, we will not quote url's for
            # versions of Nginx before 1.5.9
            if nginx_version < [1, 5, 9]:
                return False
    return True

def _convert_file_to_url(filename):
    relpath = os.path.relpath(filename, settings.SENDFILE_ROOT)

    url = [settings.SENDFILE_URL]

    while relpath:
        relpath, head = os.path.split(relpath)
        url.insert(1, head)

    # Python3 urllib.parse.quote accepts both unicode and bytes, while Python2 urllib.quote only accepts bytes.
    # So use bytes for quoting and then go back to unicode.
    url = [smart_bytes(url_component) for url_component in url]
    if should_be_quoted():
        return smart_text(quote(b'/'.join(url)))
    else:
        return smart_text(b'/'.join(url))
