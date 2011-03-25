from django.core.files.base import File
from django.http import HttpResponse

def sendfile(request, filename):
    return HttpResponse(File(file(filename, 'rb')))
