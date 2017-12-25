import os.path
from mimetypes import guess_type

VERSION = (0, 3, 4)
__version__ = '.'.join(map(str, VERSION))


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
    from django.utils.importlib import import_module
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    backend = getattr(settings, 'SENDFILE_BACKEND', None)
    if not backend:
        raise ImproperlyConfigured('You must specify a valued for SENDFILE_BACKEND')
    module = import_module(backend)
    return module.sendfile


def sendfile(request, filename, check_exist=False, attachment=False, attachment_filename=None,
             mimetype=None, encoding=None):
    """
    Create a response to send file using backend configured in SENDFILE_BACKEND.

    If attachment is True the content-disposition header will be set.
    This will typically prompt the user to download the file, rather
    than view it.  The content-disposition filename depends on the
    value of attachment_filename:

        None (default): Same as filename
        False: No content-disposition filename
        String: Value used as filename

    If mimetype is set to None then it will be automatically guessed
    via the filename (using the standard python mimetypes module).

    The same apply for encoding.
    """
    _sendfile = _get_sendfile()

    if check_exist and not os.path.exists(filename):
        from django.http import Http404
        raise Http404('"%s" does not exist' % filename)

    if mimetype is None or encoding is None:
        guessed_mimetype, guessed_encoding = guess_type(filename)
        if mimetype is None:
            mimetype = guessed_mimetype or 'application/octet-stream'
        if encoding is None:
            encoding = guessed_encoding

    response = _sendfile(request, filename, mimetype=mimetype)
    if attachment:
        if attachment_filename is None:
            attachment_filename = os.path.basename(filename)
        parts = ['attachment']
        if attachment_filename:
            from unidecode import unidecode
            try:
                from django.utils.encoding import force_text
            except ImportError:
                # Django 1.3
                from django.utils.encoding import force_unicode as force_text
            attachment_filename = force_text(attachment_filename)
            ascii_filename = unidecode(attachment_filename)
            parts.append('filename="%s"' % ascii_filename)
            if ascii_filename != attachment_filename:
                from django.utils.http import urlquote
                quoted_filename = urlquote(attachment_filename)
                parts.append('filename*=UTF-8\'\'%s' % quoted_filename)
        response['Content-Disposition'] = '; '.join(parts)

    response['Content-length'] = os.path.getsize(filename)
    response['Content-Type'] = mimetype
    if encoding:
        response['Content-Encoding'] = encoding

    return response
