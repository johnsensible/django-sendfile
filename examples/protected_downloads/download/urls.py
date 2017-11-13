from django.conf.urls import url

from .views import download, download_list

urlpatterns = [
    url(r'^$', download_list),
    url(r'(?P<download_id>\d+)/$', download, name='download'),
]
