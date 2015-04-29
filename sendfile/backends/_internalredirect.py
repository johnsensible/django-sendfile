import os
from urlparse import urlparse
from django.conf import settings
from django.utils.http import urlquote


def _convert_file_to_url(filename):
    url = [settings.SENDFILE_URL]

    parseresult = urlparse(filename)

    if parseresult.scheme:
        urlpath = parseresult.netloc + parseresult.path
        # if parseresult.params:
        #     urlpath += ';' + parseresult.params
        if parseresult.query:
            urlpath += '?' + parseresult.query
        # if parseresult.fragment:
        #     urlpath += '#' + parseresult.fragment
        url.insert(1, urlpath)

    else:
        relpath = os.path.relpath(filename, settings.SENDFILE_ROOT)
        while relpath:
            relpath, head = os.path.split(relpath)
            url.insert(1, head)

    return urlquote(u'/'.join(url))
