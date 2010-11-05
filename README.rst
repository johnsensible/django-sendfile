This is a wrapper around web-server specific methods for sending files to web clients.  This is useful when Django needs to check permissions associated files, but does not want to serve the actual bytes of the file itself.  i.e. as serving large files is not what Django is made for.


Note this should not be used for regular file serving (e.g. css etc), only for cases where you need Django to do some work before serving the actual file.


