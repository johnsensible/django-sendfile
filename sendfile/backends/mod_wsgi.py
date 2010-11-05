from django.http import HttpResponse

def sendfile(request, filename):
    response = HttpResponse('')
    print filename
    response['Location'] = filename
    return response

