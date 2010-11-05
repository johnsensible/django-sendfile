===============
Django Sendfile
===============

This is a wrapper around web-server specific methods for sending files to web clients.  This is useful when Django needs to check permissions associated files, but does not want to serve the actual bytes of the file itself.  i.e. as serving large files is not what Django is made for.

Note this should not be used for regular file serving (e.g. css etc), only for cases where you need Django to do some work before serving the actual file.

The interface is a single function `sendfile(request, filename, attachment=False, attachment_filename=None)`, which returns a HTTPResponse object.

::

    from sendfile import sendfile
    
    # send myfile.pdf to user
    return sendfile(request, '/home/john/myfile.pdf')

    # send myfile.pdf as an attachment (with name myfile.pdf)
    return sendfile(request, '/home/john/myfile.pdf', attachment=True)
    
    # send myfile.pdf as an attachment with a different name
    return sendfile(request, '/home/john/myfile.pdf', attachment=True, attachment_filename='full-name.pdf')



Backends are specified using the setting `SENDFILE_BACKEND`.  Currenly available backends are:

* `sendfile.backends.development` - for use with django development server only. DO NOT USE IN PRODUCTION
* `sendfile.backends.xsendfile` - sets X-Sendfile header (as used by mod_xsendfile/apache and lighthttpd)

If you want to write your own backend simply create a module with a `sendfile` function matching:

::

   def sendfile(request, filename):
       '''Return HttpResponse object for serving file'''


Then specify the full path to the module in `SENDFILE_BACKEND`.  You only need to implement the sending of the file.  Adding the content-disposition headers etc is done elsewhere.

