from __future__ import absolute_import

from django.http import HttpResponse

from ._internalredirect import _convert_file_to_url


def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    response['Location'] = _convert_file_to_url(filename)
    # need to destroy get_host() to stop django
    # rewriting our location to include http, so that
    # mod_wsgi is able to do the internal redirect
    request.get_host = lambda: ''

    return response
