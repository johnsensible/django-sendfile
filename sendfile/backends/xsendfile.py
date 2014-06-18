from django.http import HttpResponse
from django.utils.encoding import smart_str


def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    response['X-Sendfile'] = smart_str(unicode(filename))

    return response
