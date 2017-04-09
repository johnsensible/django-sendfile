# coding=utf-8
import os.path
import shutil
from tempfile import mkdtemp
from unittest import TestCase

from django.http import Http404, HttpRequest, HttpResponse
from django.test.utils import override_settings
from django.utils.six.moves.urllib.parse import unquote

from sendfile import sendfile as real_sendfile
from sendfile import _get_sendfile


def sendfile(request, filename, **kwargs):
    # just a simple response with the filename
    # as content - so we can test without a backend active
    return HttpResponse(filename)


class TempFileTestCase(TestCase):

    def setUp(self):
        super(TempFileTestCase, self).setUp()
        self.TEMP_FILE_ROOT = mkdtemp()
        self.addCleanup(shutil.rmtree, self.TEMP_FILE_ROOT)

    def ensure_file(self, filename):
        path = os.path.join(self.TEMP_FILE_ROOT, filename)
        if not os.path.exists(path):
            open(path, 'w').close()
        return path


class TestSendfile(TempFileTestCase):

    def setUp(self):
        super(TestSendfile, self).setUp()
        # set ourselves to be the sendfile backend
        cm = override_settings(SENDFILE_BACKEND='tests.tests')
        cm.enable()
        self.addCleanup(cm.disable)
        _get_sendfile.clear()

    def _get_readme(self):
        return self.ensure_file('testfile.txt')

    def test_404(self):
        with self.assertRaises(Http404):
            real_sendfile(HttpRequest(), 'fhdsjfhjk.txt')

    def test_sendfile(self):
        response = real_sendfile(HttpRequest(), self._get_readme())
        self.assertIsNotNone(response)
        self.assertEqual('text/plain', response['Content-Type'])
        self.assertEqual(self._get_readme(), response.content.decode(response.charset))

    def test_set_mimetype(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), mimetype='text/plain')
        self.assertIsNotNone(response)
        self.assertEqual('text/plain', response['Content-Type'])

    def test_set_encoding(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), encoding='utf8')
        self.assertIsNotNone(response)
        self.assertEqual('utf8', response['Content-Encoding'])

    def test_attachment(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True)
        self.assertIsNotNone(response)
        self.assertEqual('attachment; filename="testfile.txt"', response['Content-Disposition'])

    def test_attachment_filename_false(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True, attachment_filename=False)
        self.assertIsNotNone(response)
        self.assertEqual('attachment', response['Content-Disposition'])

    def test_attachment_filename(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True, attachment_filename='tests.txt')
        self.assertIsNotNone(response)
        self.assertEqual('attachment; filename="tests.txt"', response['Content-Disposition'])

    def test_attachment_filename_unicode(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True, attachment_filename='test’s.txt')
        self.assertIsNotNone(response)
        self.assertEqual('attachment; filename="tests.txt"; filename*=UTF-8\'\'test%E2%80%99s.txt', response['Content-Disposition'])


class TestXSendfileBackend(TempFileTestCase):

    def setUp(self):
        super(TestXSendfileBackend, self).setUp()
        cm = override_settings(SENDFILE_BACKEND='sendfile.backends.xsendfile')
        cm.enable()
        self.addCleanup(cm.disable)
        _get_sendfile.clear()

    def test_correct_file_in_xsendfile_header(self):
        filepath = self.ensure_file('readme.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertIsNotNone(response)
        self.assertEqual(filepath, response['X-Sendfile'])

    def test_xsendfile_header_containing_unicode(self):
        filepath = self.ensure_file('péter_là_gueule.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertIsNotNone(response)
        self.assertEqual(filepath, response['X-Sendfile'])


class TestNginxBackend(TempFileTestCase):

    def setUp(self):
        super(TestNginxBackend, self).setUp()
        cm = override_settings(
            SENDFILE_BACKEND='sendfile.backends.nginx',
            SENDFILE_ROOT=self.TEMP_FILE_ROOT,
            SENDFILE_URL='/private')
        cm.enable()
        self.addCleanup(cm.disable)
        _get_sendfile.clear()

    def test_correct_url_in_xaccelredirect_header(self):
        filepath = self.ensure_file('readme.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertIsNotNone(response)
        self.assertEqual('/private/readme.txt', response['X-Accel-Redirect'])

    def test_xaccelredirect_header_containing_unicode(self):
        filepath = self.ensure_file('péter_là_gueule.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertIsNotNone(response)
        self.assertEqual('/private/péter_là_gueule.txt', unquote(response['X-Accel-Redirect']))


class TestModWsgiBackend(TempFileTestCase):

    def setUp(self):
        super(TestModWsgiBackend, self).setUp()
        cm = override_settings(
            SENDFILE_BACKEND='sendfile.backends.mod_wsgi',
            SENDFILE_ROOT=self.TEMP_FILE_ROOT,
            SENDFILE_URL='/private')
        cm.enable()
        self.addCleanup(cm.disable)
        _get_sendfile.clear()

    def test_correct_url_in_location_header(self):
        filepath = self.ensure_file('readme.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertIsNotNone(response)
        self.assertEqual('/private/readme.txt', response['Location'])

    def test_location_header_containing_unicode(self):
        filepath = self.ensure_file('péter_là_gueule.txt')
        response = real_sendfile(HttpRequest(), filepath)
        self.assertIsNotNone(response)
        self.assertEqual('/private/péter_là_gueule.txt', unquote(response['Location']))
