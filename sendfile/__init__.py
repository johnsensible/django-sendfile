import os.path
from mimetypes import guess_type
import unicodedata

VERSION = (0, 3, 11)
__version__ = '.'.join(map(str, VERSION))

_guess = object()


def _lazy_load(fn):
    _cached = []

    def _decorated():
        if not _cached:
            _cached.append(fn())
        return _cached[0]

    def clear():
        while _cached:
            _cached.pop()
    _decorated.clear = clear
    return _decorated


@_lazy_load
def _get_sendfile():
    try:
        from importlib import import_module
    except ImportError:  # Django < 1.9
        from django.utils.importlib import import_module
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    backend = getattr(settings, 'SENDFILE_BACKEND', None)
    if not backend:
        raise ImproperlyConfigured('You must specify a value for SENDFILE_BACKEND')
    module = import_module(backend)
    return module.sendfile


def sendfile(request, filename, check_exist=False, attachment=False, attachment_filename=None,
             encoding=_guess, filesize=_guess, mimetype=_guess):
    """
    Create a response to send file using backend configured in SENDFILE_BACKEND.

    If attachment is True the content-disposition header will be set.
    This will typically prompt the user to download the file, rather
    than view it.  The content-disposition filename depends on the
    value of attachment_filename:

        None (default): Same as filename
        False: No content-disposition filename
        String: Value used as filename

    Any of encoding, filesize and mimetype left to _guess will be
    guessed via the filename (using the standard python mimetypes
    and os.path modules).

    Any of encoding, filesize and mimetype set to None will not
    be set into the response headers.
    """
    _sendfile = _get_sendfile()

    if check_exist and not os.path.exists(filename):
        from django.http import Http404
        raise Http404('"%s" does not exist' % filename)

    if filesize is _guess:
        filesize = os.path.getsize(filename)
    if mimetype is _guess or encoding is _guess:
        guessed_mimetype, guessed_encoding = guess_type(filename)
        if mimetype is _guess:
            mimetype = guessed_mimetype or 'application/octet-stream'
        if encoding is _guess:
            encoding = guessed_encoding

    response = _sendfile(request, filename, mimetype=mimetype)
    if attachment:
        if attachment_filename is None:
            attachment_filename = os.path.basename(filename)
        parts = ['attachment']
        if attachment_filename:
            try:
                from django.utils.encoding import force_text
            except ImportError:
                # Django 1.3
                from django.utils.encoding import force_unicode as force_text
            attachment_filename = force_text(attachment_filename)
            ascii_filename = unicodedata.normalize('NFKD', attachment_filename).encode('ascii','ignore') 
            parts.append('filename="%s"' % ascii_filename)
            if ascii_filename != attachment_filename:
                from django.utils.http import urlquote
                quoted_filename = urlquote(attachment_filename)
                parts.append('filename*=UTF-8\'\'%s' % quoted_filename)
        response['Content-Disposition'] = '; '.join(parts)

    if encoding is not None:
        response['Content-Encoding'] = encoding
    if filesize is not None:
        response['Content-Length'] = filesize
    if mimetype is not None:
        response['Content-Type'] = mimetype

    return response
