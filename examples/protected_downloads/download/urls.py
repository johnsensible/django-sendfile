from django.conf.urls.defaults import *

from .views import download, download_list

urlpatterns = patterns('',
    url(r'^$', download_list),
    url(r'(?P<download_id>\d+)/$', download, name='download'),
)
