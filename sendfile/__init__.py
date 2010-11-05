VERSION = (0, 0, 1)
__version__ = '.'.join(map(str, VERSION))


def _lazy_load(fn):
    _cached = []
    def _decorated():
        if not _cached:
            _cached.append(fn())
        return _cached[0]
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



def sendfile(filename, attachment_name=None):
    _sendfile = _get_sendfile()
    response = _sendfile(filename)
    if attachment_name is not None:
        pass
        # TODO set attachment disposition etc
    return response
