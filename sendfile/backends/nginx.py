from __future__ import absolute_import

from django.http import HttpResponse
from django.utils.encoding import smart_bytes

from ._internalredirect import _convert_file_to_url


def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    url = _convert_file_to_url(filename)
    response['X-Accel-Redirect'] = smart_bytes(url)

    return response
