from django.http import HttpResponse


def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    response['X-Sendfile'] = unicode(filename).encode('utf-8')

    return response
