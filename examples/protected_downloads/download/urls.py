from django.urls import re_path

from .views import download, download_list

urlpatterns = [
    re_path(r'^$', download_list),
    re_path(r'(?P<download_id>\d+)/$', download, name='download'),
]
