from django.http import HttpResponse
import six


def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    if six.PY2:
        response['X-Sendfile'] = unicode(filename).encode('utf-8')
    else:
        response['X-Sendfile'] = filename # .encode('utf-8')

    return response
