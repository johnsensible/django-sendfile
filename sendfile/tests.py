# coding=utf-8

from django.conf import settings
from django.test import TestCase
from django.http import HttpResponse, Http404, HttpRequest
import django.http

import os.path
from tempfile import mkdtemp
import shutil
import random
from sendfile import sendfile as real_sendfile, _get_sendfile


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

    def ensure_file(self, filename, length=0):
        path = os.path.join(self.TEMP_FILE_ROOT, filename)
        if not os.path.exists(path):
            f = open(path, 'w')
            if length > 0:
                f.write("".join([chr(random.randint(0, 255)) for _ in range(length)]))
            f.close()
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
        self.assertEqual(self._get_readme(), response.content)

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

    def test_attachment_filename(self):
        response = real_sendfile(HttpRequest(), self._get_readme(), attachment=True, attachment_filename='tests.txt')
        self.assertTrue(response is not None)
        self.assertEqual('attachment; filename="tests.txt"', response['Content-Disposition'])


class TestSimpleBackend(TempFileTestCase):

    def setUp(self):
        super(TestSimpleBackend, self).setUp()
        settings.SENDFILE_BACKEND = 'sendfile.backends.simple'
        _get_sendfile.clear()

        self.filepath = self.ensure_file('readme.txt', length=90)
        f = open(self.filepath, 'rb')
        self.filecontent = f.read()
        f.close()

    def _verify_response_content(self, response, start, stop):
        result = []
        for block in response.streaming_content:
            result.append(block)
        result = "".join(result)

        self.assertEqual(len(result), len(self.filecontent[start:stop]))
        self.assertEqual(result, self.filecontent[start:stop])

    if hasattr(django.http, 'StreamingHttpResponse'):
        # Django >= 1.5

        def test_range_request_header(self):
            request = HttpRequest()
            response = real_sendfile(request, self.filepath, accept_ranges=True)
            self.assertEqual(response['Accept-ranges'], 'bytes')
            self.assertEqual(response['Content-length'], '90')
            self._verify_response_content(response, 0, 90)

            # Request with both bounds
            request = HttpRequest()
            request.META['HTTP_RANGE'] = 'bytes=5-7'
            response = real_sendfile(request, self.filepath, accept_ranges=True)
            self.assertEqual(response.status_code, 206)
            self.assertEqual(response['Content-length'], '3')
            self.assertEqual(response['Content-range'], 'bytes 5-7/90')
            self._verify_response_content(response, 5, 7+1)

            # Request with start bound
            request = HttpRequest()
            request.META['HTTP_RANGE'] = 'bytes=1-'
            response = real_sendfile(request, self.filepath, accept_ranges=True)
            self.assertEqual(response.status_code, 206)
            self.assertEqual(response['Content-length'], '89')
            self.assertEqual(response['Content-range'], 'bytes 1-89/90')
            self._verify_response_content(response, 1, 90)

            # Request with end bound
            request = HttpRequest()
            request.META['HTTP_RANGE'] = 'bytes=-1'
            response = real_sendfile(request, self.filepath, accept_ranges=True)
            self.assertEqual(response.status_code, 206)
            self.assertEqual(response['Content-length'], '2')
            self.assertEqual(response['Content-range'], 'bytes 0-1/90')
            self._verify_response_content(response, 0, 1+1)

            # Out of bounds request
            request = HttpRequest()
            request.META['HTTP_RANGE'] = 'bytes=0-90'
            response = real_sendfile(request, self.filepath, accept_ranges=True)
            self.assertEqual(response['Content-range'], 'bytes */90')
            self.assertEqual(response.status_code, 416)

            # Malformed headers, MUST be ignored according to spec
            for hdr in ['bytes=-', 'bytes=foo', 'bytes=3-2']:
                request = HttpRequest()
                request.META['HTTP_RANGE'] = hdr
                response = real_sendfile(request, self.filepath,
                                         accept_ranges=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-length'], '90')
                self._verify_response_content(response, 0, 90)

            # Without accept-ranges, it should be disabled
            request = HttpRequest()
            request.META['HTTP_RANGE'] = 'bytes=5-7'
            response = real_sendfile(request, self.filepath)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-length'], '90')
            self._verify_response_content(response, 0, 90)


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
        self.assertEqual(filepath, response['X-Sendfile'].decode('utf-8'))


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
        self.assertEqual(u'/private/péter_là_gueule.txt', response['X-Accel-Redirect'].decode('utf-8'))
