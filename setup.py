from setuptools import setup, find_packages
 
setup(
    name='django-sendfile',
    version=__import__('sendfile').__version__,
    description='Abstraction to offload file uploads to web-server (e.g. Apache with mod_xsendfile) once Django has checked permissions etc.',
    long_description=open('README.rst').read(),
    author='John Montgomery',
    author_email='john@sensibledevelopment.com',
    url='http://github.com/johnsensible/django-sendfile',
    download_url='http://github.com/johnsensible/django-sendfile/downloads',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
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
