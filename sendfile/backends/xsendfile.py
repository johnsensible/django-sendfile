from django.http import HttpResponse
from django.utils.encoding import force_str


def sendfile(request, filename, **kwargs):
    response = HttpResponse()
    response['X-Sendfile'] = force_str(filename)

    return response
