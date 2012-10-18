from django.conf import settings
from django.test import TestCase
from django.http import HttpResponse, Http404, HttpRequest
import os.path
from sendfile import sendfile as real_sendfile, _get_sendfile

def sendfile(request, filename, **kwargs):
    # just a simple response with the filename
    # as content - so we can test without a backend active
    return HttpResponse(filename)


def _get_readme():
    return os.path.join(os.path.dirname(__file__), 'testfile.txt')

class TestSendfile(TestCase):

    def setUp(self):
        # set ourselves to be the sendfile backend
        settings.SENDFILE_BACKEND = 'sendfile.tests'
        _get_sendfile.clear()
    
    def test_404(self):
        try:
            real_sendfile(HttpRequest(), 'fhdsjfhjk.txt')
        except Http404:
            pass

    def test_sendfile(self):
        response = real_sendfile(HttpRequest(), _get_readme())
        self.assertTrue(response is not None)
        self.assertEqual('text/plain', response['Content-Type'])
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
        self.assertEqual('attachment; filename="testfile.txt"', response['Content-Disposition'])

    def test_attachment_filename(self):
        response = real_sendfile(HttpRequest(), _get_readme(), attachment=True, attachment_filename='tests.txt')
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename="tests.txt"', response['Content-Disposition'])


class TestXSendfileBackend(TestCase):

    def setUp(self):
        settings.SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
        _get_sendfile.clear()

    def test_correct_file_in_xsendfile_header(self):
        response = real_sendfile(HttpRequest(), _get_readme())
        self.assertTrue(response is not None)
        self.assertEqual(_get_readme(), response['X-Sendfile'])


class TestNginxBackend(TestCase):

    def setUp(self):
        settings.SENDFILE_BACKEND = 'sendfile.backends.nginx'
        settings.SENDFILE_ROOT = os.path.dirname(os.path.dirname(__file__))
        settings.SENDFILE_URL = '/private'
        _get_sendfile.clear()

    def test_correct_url_in_xaccelredirect_header(self):
        response = real_sendfile(HttpRequest(), _get_readme())
        self.assertTrue(response is not None)
        self.assertEqual('/private/sendfile/testfile.txt', response['X-Accel-Redirect'])

