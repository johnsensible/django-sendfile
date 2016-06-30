# coding=utf-8

from django.conf import settings
from django.test import TestCase
from django.http import HttpResponse, Http404, HttpRequest
from django.utils.encoding import smart_str
import os.path
from tempfile import mkdtemp
import shutil
from sendfile import sendfile as real_sendfile, _get_sendfile

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote


def sendfile(request, filename, **kwargs):
    # just a simple response with the filename
    # as content - so we can test without a backend active
    return HttpResponse(filename)


class TempFileTestCase(TestCase):

    def setUp(self):
        super(TempFileTestCase, self).setUp()
        self.TEMP_FILE_ROOT = mkdtemp()

    def tearDown(self):
        super(TempFileTestCase, self).tearDown()
        if os.path.exists(self.TEMP_FILE_ROOT):
            shutil.rmtree(self.TEMP_FILE_ROOT)

    def ensure_file(self, filename):
        path = os.path.join(self.TEMP_FILE_ROOT, filename)
        if not os.path.exists(path):
            open(path, 'w').close()
        return path


class TestSendfile(TempFileTestCase):

    def setUp(self):
        super(TestSendfile, self).setUp()
        # set ourselves to be the sendfile backend
        settings.SENDFILE_BACKEND = 'sendfile.tests'
        _get_sendfile.clear()

    def _get_readme(self):
        return self.ensure_file('testfile.txt')

    def test_404(self):
        try:
            real_sendfile(HttpRequest(), 'fhdsjfhjk.txt')
        except Http404:
            pass

    def test_sendfile(self):
        response = real_sendfile(HttpRequest(), self._get_readme())
        self.assertTrue(response is not None)
        self.assertEqual('text/plain', response['Content-Type'])
        self.assertEqual(self._get_readme(), smart_str(response.content))

    def test_set_mimetype(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), mimetype='text/plain')
        self.assertTrue(response is not None)
        self.assertEqual('text/plain', response['Content-Type'])

    def test_set_encoding(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), encoding='utf8')
        self.assertTrue(response is not None)
        self.assertEqual('utf8', response['Content-Encoding'])

    def test_attachment(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True)
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename="testfile.txt"', response['Content-Disposition'])

    def test_attachment_filename_false(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True, attachment_filename=False)
        self.assertTrue(response is not None)
        self.assertEqual('attachment', response['Content-Disposition'])

    def test_attachment_filename(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True, attachment_filename='tests.txt')
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename="tests.txt"', response['Content-Disposition'])

    def test_attachment_filename_unicode(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True, attachment_filename='test’s.txt')
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename="tests.txt"; filename*=UTF-8\'\'test%E2%80%99s.txt', response['Content-Disposition'])


class TestXSendfileBackend(TempFileTestCase):

    def setUp(self):
        super(TestXSendfileBackend, self).setUp()
        settings.SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
        _get_sendfile.clear()

    def test_correct_file_in_xsendfile_header(self):
        filepath = self.ensure_file('readme.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertTrue(response is not None)
        self.assertEqual(filepath, response['X-Sendfile'])

    def test_xsendfile_header_containing_unicode(self):
        filepath = self.ensure_file(u'péter_là_gueule.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertTrue(response is not None)
        self.assertEqual(smart_str(filepath), response['X-Sendfile'])


class TestNginxBackend(TempFileTestCase):

    def setUp(self):
        super(TestNginxBackend, self).setUp()
        settings.SENDFILE_BACKEND = 'sendfile.backends.nginx'
        settings.SENDFILE_ROOT = self.TEMP_FILE_ROOT
        settings.SENDFILE_URL = '/private'
        _get_sendfile.clear()

    def test_correct_url_in_xaccelredirect_header(self):
        filepath = self.ensure_file('readme.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertTrue(response is not None)
        self.assertEqual('/private/readme.txt', response['X-Accel-Redirect'])

    def test_xaccelredirect_header_containing_unicode(self):
        filepath = self.ensure_file(u'péter_là_gueule.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertTrue(response is not None)
        self.assertEqual(u'/private/péter_là_gueule.txt'.encode('utf-8'), unquote(response['X-Accel-Redirect']))


class TestModWsgiBackend(TempFileTestCase):

    def setUp(self):
        super(TestModWsgiBackend, self).setUp()
        settings.SENDFILE_BACKEND = 'sendfile.backends.mod_wsgi'
        settings.SENDFILE_ROOT = self.TEMP_FILE_ROOT
        settings.SENDFILE_URL = '/private'
        _get_sendfile.clear()

    def test_correct_url_in_location_header(self):
        filepath = self.ensure_file('readme.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertTrue(response is not None)
        self.assertEqual('/private/readme.txt', response['Location'])

    def test_location_header_containing_unicode(self):
        filepath = self.ensure_file(u'péter_là_gueule.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertTrue(response is not None)
        self.assertEqual(u'/private/péter_là_gueule.txt'.encode('utf-8'), unquote(response['Location']))
