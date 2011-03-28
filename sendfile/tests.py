from django.conf import settings
from django.test import TestCase
from django.http import HttpResponse, Http404, HttpRequest
import os.path
from sendfile import sendfile as real_sendfile

def sendfile(request, filename, **kwargs):
    # just a simple response with the filename
    # as content - so we can test without a backend active
    return HttpResponse(filename)


class TestSendfile(TestCase):

    def setUp(self):
        # set ourselves to be the sendfile backend
        settings.SENDFILE_BACKEND = 'sendfile.tests'
    
    def test_404(self):
        try:
            real_sendfile(HttpRequest(), 'fhdsjfhjk.txt')
        except Http404:
            pass

    def test_sendfile(self):
        response = real_sendfile(HttpRequest(), __file__)
        self.assertTrue(response is not None)
        self.assertEqual('text/x-python', response['Content-Type'])
        self.assertEqual(__file__, response.content)

    def test_set_mimetype(self):
        response = real_sendfile(HttpRequest(), __file__, mimetype='text/plain')
        self.assertTrue(response is not None)
        self.assertEqual('text/plain', response['Content-Type'])

    def test_set_encoding(self):
        response = real_sendfile(HttpRequest(), __file__, encoding='utf8')
        self.assertTrue(response is not None)
        self.assertEqual('utf8', response['Content-Encoding'])

    def test_attachment(self):
        response = real_sendfile(HttpRequest(), __file__, attachment=True)
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename=tests.py', response['Content-Disposition'])

    def test_attachment_filename(self):
        response = real_sendfile(HttpRequest(), __file__, attachment=True, attachment_filename='tests.txt')
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename=tests.txt', response['Content-Disposition'])

