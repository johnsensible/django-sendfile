import os.path
from django.conf import settings
from rfc3987 import parse

def _convert_file_to_url(filename):
    try:
        url_dictionary = parse(filename, rule='IRI')
        uri_segment = [settings.SENDFILE_PROXY]
        uri_path = filename.replace('%s://' % url_dictionary['scheme'], '')
        uri_segment.insert(1, uri_path)

    except ValueError:
        relpath = os.path.relpath(filename, settings.SENDFILE_ROOT)
        uri_segment = [settings.SENDFILE_URL]
        while relpath:
            relpath, head = os.path.split(relpath)
            uri_segment.insert(1, head)

    url = u'/'.join(uri_segment)

    return url

