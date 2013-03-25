from distutils.core import setup

version=__import__('sendfile').__version__


setup(
    name='django-sendfile',
    version=version,
    description='Abstraction to offload file uploads to web-server (e.g. Apache with mod_xsendfile) once Django has checked permissions etc.',
    long_description=open('README.rst').read(),
    author='John Montgomery',
    author_email='john@sensibledevelopment.com',
    url='https://github.com/johnsensible/django-sendfile',
    download_url='https://github.com/johnsensible/django-sendfile/archive/v%s.zip#egg=django-sendfile-%s' % (version, version),
    license='BSD',
    
    requires=['Django (>=1.4.2)'],

    packages=['sendfile', 'sendfile.backends'],
    package_dir={
        'sendfile': 'sendfile',
        'sendfile.backends': 'sendfile/backends',
    },
    package_data = {
        'sendfile': ['testfile.txt'],
    },
    
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
