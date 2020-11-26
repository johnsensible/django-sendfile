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
* `sendfile.backends.simple` - "simple" backend that uses Django file objects to attempt to stream files from disk (note middleware may cause files to be loaded fully into memory)
* `sendfile.backends.xsendfile` - sets X-Sendfile header (as used by mod_xsendfile/apache and lighthttpd)
* `sendfile.backends.mod_wsgi` - sets Location with 200 code to trigger internal redirect (daemon mode mod_wsgi only - see below)
* `sendfile.backends.nginx` - sets X-Accel-Redirect header to trigger internal redirect to file

If you want to write your own backend simply create a module with a `sendfile` function matching:

::

   def sendfile(request, filename):
       '''Return HttpResponse object for serving file'''


Then specify the full path to the module in `SENDFILE_BACKEND`.  You only need to implement the sending of the file.  Adding the content-disposition headers etc is done elsewhere.


Development backend
===================

The Development backend is only meant for use while writing code.  It uses Django's static file serving code to do the job, which is only meant for development.  It reads the whole file into memory and the sends it down the wire - not good for big files, but ok when you are just testing things out.

It will work with the Django dev server and anywhere else you can run Django.

Simple backend
==============

This backend is one step up from the development backend.  It uses Django's `django.core.files.base.File` class to try and stream files from disk.  However some middleware (e.g. GzipMiddleware) that rewrites content will causes the entire file to be loaded into memory.  So only use this backend if you are not using middleware that rewrites content or you only have very small files.


xsendfile backend
=================

Install either mod_xsendfile_ in Apache_ or use Lighthttpd_.  You may need to configure mod_xsendfile_, but that should be as simple as:

::

    XSendFile On

In your virtualhost file/conf file.


mod_wsgi backend
================

The mod_wsgi backend will only work when using mod_wsgi in daemon mode, not in embedded mode.  It requires a bit more work to get it to do the same job as xsendfile though.  However some may find it easier to setup, as they don't need to compile and install mod_xsendfile_.

Firstly there are two more django settings:

* `SENDFILE_ROOT` - this is a directoy where all files that will be used with sendfile must be located
* `SENDFILE_URL` - internal URL prefix for all files served via sendfile

These settings are needed as this backend makes mod_wsgi_ send an internal redirect, so we have to convert a file path into a URL.  This means that the files are visible via Apache_ by default too.  So we need to get Apache_ to hide those files from anything that's not an internal redirect.  To so this we can use some mod_rewrite_ magic along these lines:

::

    RewriteEngine On
    # see if we're on an internal redirect or not
    RewriteCond %{THE_REQUEST} ^[\S]+\ /private/
    RewriteRule ^/private/ - [F]

    Alias /private/ /home/john/Development/myapp/private/
    <Directory /home/john/Development/myapp/private/>
        Order deny,allow
        Allow from all
    </Directory>


In this case I have also set:

::

    SENDFILE_ROOT = '/home/john/Development/myapp/private/'
    SENDFILE_URL = '/private'


All files are stored in a folder called 'private'.  We forbid access to this folder (`RewriteRule ^/private/ - [F]`) if someone tries to access it directly (`RewriteCond %{THE_REQUEST} ^[\S]+\ /private/`) by checking the original request (`THE_REQUEST`).

Alledgedly `IS_SUBREQ` can be used to `perform the same job <http://www.mail-archive.com/django-users@googlegroups.com/msg96718.html>`_, but I was unable to get this working.


Nginx backend
=============

As with the mod_wsgi backend you need to set two extra settings:

* `SENDFILE_ROOT` - this is a directoy where all files that will be used with sendfile must be located
* `SENDFILE_URL` - internal URL prefix for all files served via sendfile

You then need to configure nginx to only allow internal access to the files you wish to serve.  More details on this `are here <https://www.nginx.com/resources/wiki/start/topics/examples/xsendfile/>`_.

For example though, if I use the django settings:

::

    SENDFILE_ROOT = '/home/john/Development/django-sendfile/examples/protected_downloads/protected'
    SENDFILE_URL = '/protected'

Then the matching location block in nginx.conf would be:

::

    location /protected/ {
      internal;
      root   /home/john/Development/django-sendfile/examples/protected_downloads;
    }

You need to pay attention to whether you have trailing slashes or not on the SENDFILE_URL and root values, otherwise you may not get the right URL being sent to NGINX and you may get 404s.  You should be able to see what file NGINX is trying to load in the error.log if this happens.  From there it should be fairly easy to work out what the right settings are.

.. _mod_xsendfile: https://tn123.org/mod_xsendfile/
.. _Apache: http://httpd.apache.org/
.. _Lighthttpd: http://www.lighttpd.net/
.. _mod_wsgi: http://code.google.com/p/modwsgi/

