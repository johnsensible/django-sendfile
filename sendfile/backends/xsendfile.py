from django.http import HttpResponse

from mimetypes import guess_type
import os.path

def sendfile(request, filename):
    response = HttpResponse()
    response['Content-length'] = os.path.getsize(filename)

    content_type = guess_type(filename)[0]
    if content_type is None:
        content_type = "application/octet-stream"
    response['Content-Type'] = content_type
    
    response['X-Sendfile'] = filename

    return response

