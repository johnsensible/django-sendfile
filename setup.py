from setuptools import setup


version = __import__('sendfile').__version__


setup(
    name='django-sendfile',
    version=version,
    description='Abstraction to offload file uploads to web-server (e.g. Apache with mod_xsendfile) once Django has checked permissions etc.',
    long_description=open('README.rst').read(),
    author='John Montgomery',
    author_email='john@sensibledevelopment.com',
    url='https://github.com/johnsensible/django-sendfile',
    license='BSD',

    requires=['Django (>=1.8)'],
    install_requires=['Django>=1.8', 'six'],

    packages=['sendfile', 'sendfile.backends'],
    package_dir={
        'sendfile': 'sendfile',
        'sendfile.backends': 'sendfile/backends',
    },
    package_data={
        'sendfile': ['testfile.txt'],
    },

    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
