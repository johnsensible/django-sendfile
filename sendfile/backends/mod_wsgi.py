from django.http import HttpResponse

from ._internalredirect import _convert_file_to_url


def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    response['Location'] = _convert_file_to_url(filename)
    # Workaround for Django < 1.9
    # https://docs.djangoproject.com/en/1.9/releases/1.9/#http-redirects-no-longer-forced-to-absolute-uris
    #
    # need to destroy get_host() to stop django
    # rewriting our location to include http, so that
    # mod_wsgi is able to do the internal redirect
    request.get_host = lambda: ''
    request.build_absolute_uri = lambda location: location

    return response
