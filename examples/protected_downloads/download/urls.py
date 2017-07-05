from .views import download, download_list

import django

if django.VERSION >= (1,9,0):
    from django.conf.urls import *
    urlpatterns = [
        url(r'^$', download_list),
        url(r'(?P<download_id>\d+)/$', download, name='download'),
        ]
else:
    from django.conf.urls.defaults import *

    urlpatterns = patterns(
        '',
        url(r'^$', download_list),
        url(r'(?P<download_id>\d+)/$', download, name='download'),
        )
