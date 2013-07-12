import os
import stat
import re
from email.Utils import parsedate_tz, mktime_tz

from django.core.files.base import File
from django.http import HttpResponse, HttpResponseNotModified
from django.utils.http import http_date

try:
    # New in Django 1.5
    from django.http import StreamingHttpResponse
except ImportError:
    StreamingHttpResponse = None


def sendfile(request, filename, **kwargs):
    # Respect the If-Modified-Since header.
    statobj = os.stat(filename)

    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()

    if StreamingHttpResponse is None:
        # Django < 1.5
        response = HttpResponse(File(open(filename, 'rb')))
        response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
        return response

    fileiter = _FileStreamer(filename)

    response = StreamingHttpResponse(fileiter)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])

    # Parse range request, if any
    start = None
    stop = None

    range_request = request.META.get('HTTP_RANGE', '').strip()
    m = re.match(r'^bytes=(?P<start>\d+)?-(?P<stop>\d+)?$', range_request)
    if m and kwargs.get('accept_ranges', False):
        start, stop = m.groups()
        try:
            if start is not None:
                start = int(start)
            if stop is not None:
                stop = int(stop)
                if start is not None and stop < start:
                    raise ValueError()
            if start is None and stop is None:
                raise ValueError()

            if start is None:
                start = 0
            if stop is None:
                stop = fileiter.file_size - 1
        except ValueError:
            # invalid header --- MUST be ignored
            start = None
            stop = None

    # Prepare serving ranges
    if start is not None:
        try:
            fileiter.set_range(start, stop)
            response.status_code = 206
            response['Content-Range'] = 'bytes %d-%d/%d' % (start, stop,
                                                            fileiter.file_size)
            response['Content-Length'] = stop + 1 - start
        except ValueError:
            # Out of bounds
            response = HttpResponse(status=416)
            response['Content-Range'] = 'bytes */%d' % (fileiter.file_size,)
            return response

    return response


def was_modified_since(header=None, mtime=0, size=0):
    """
    Was something modified since the user last downloaded it?

    header
      This is the value of the If-Modified-Since header.  If this is None,
      I'll just return True.

    mtime
      This is the modification time of the item we're talking about.

    size
      This is the size of the item we're talking about.
    """
    try:
        if header is None:
            raise ValueError
        matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header,
                           re.IGNORECASE)
        header_date = parsedate_tz(matches.group(1))
        if header_date is None:
            raise ValueError
        header_mtime = mktime_tz(header_date)
        header_len = matches.group(3)
        if header_len and int(header_len) != size:
            raise ValueError
        if mtime > header_mtime:
            raise ValueError
    except (AttributeError, ValueError, OverflowError):
        return True
    return False


class _FileStreamer(object):
    """
    Streaming file iterator for Django's StreamingHttpResponse.
    Also supports streaming only a part of the file.
    """

    BLOCK_SIZE = 131072

    def __init__(self, filename):
        self.fp = open(filename, 'rb')
        self.file_size = os.path.getsize(filename)
        self.start = None
        self.stop = None   # inclusive!
        self.pos = 0

    def set_range(self, start, stop):
        if not ((0 <= start < self.file_size) and (0 <= stop < self.file_size)):
            raise ValueError("Start or stop out of bounds")

        self.fp.seek(start)
        self.pos = start
        self.start = start
        self.stop = stop

    def close(self):
        if self.fp is not None:
            self.fp.close()
            self.stop = -1
            self.fp = None

    def __iter__(self):
        return self

    def next(self):
        if self.stop is not None:
            block_size = min(_FileStreamer.BLOCK_SIZE, self.stop + 1 - self.pos)
            if block_size <= 0:
                self.close()
                raise StopIteration()
        else:
            block_size = _FileStreamer.BLOCK_SIZE

        block = self.fp.read(block_size)
        self.pos += len(block)

        if not block:
            self.close()
            raise StopIteration()

        return block

    __next__ = next
