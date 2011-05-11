from django.conf import settings
from django.test import TestCase
from django.http import HttpResponse, Http404, HttpRequest
import os.path
from sendfile import sendfile as real_sendfile

def sendfile(request, filename, **kwargs):
    # just a simple response with the filename
    # as content - so we can test without a backend active
    return HttpResponse(filename)


def _get_readme():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.rst')

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
        response = real_sendfile(HttpRequest(), _get_readme())
        self.assertTrue(response is not None)
        self.assertEqual('application/octet-stream', response['Content-Type'])
        self.assertEqual(_get_readme(), response.content)

    def test_set_mimetype(self):
        response = real_sendfile(HttpRequest(), _get_readme(), mimetype='text/plain')
        self.assertTrue(response is not None)
        self.assertEqual('text/plain', response['Content-Type'])

    def test_set_encoding(self):
        response = real_sendfile(HttpRequest(), _get_readme(), encoding='utf8')
        self.assertTrue(response is not None)
        self.assertEqual('utf8', response['Content-Encoding'])

    def test_attachment(self):
        response = real_sendfile(HttpRequest(), _get_readme(), attachment=True)
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename=README.rst', response['Content-Disposition'])

    def test_attachment_filename(self):
        response = real_sendfile(HttpRequest(), _get_readme(), attachment=True, attachment_filename='tests.txt')
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename=tests.txt', response['Content-Disposition'])

