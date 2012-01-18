from django.http import HttpResponse

from _internalredirect import _convert_file_to_url

def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    response['X-Accel-Redirect'] = _convert_file_to_url(filename)

    return response
