

from django.contrib import admin
admin.autodiscover()

import django
if django.VERSION >= (1,9,0):
    from django.conf.urls import *
    urlpatterns = [
        url(r'^', include('protected_downloads.download.urls')),
        url(r'^admin/', include(admin.site.urls)),
        ]

else:
    from django.conf.urls.defaults import *
    urlpatterns = patterns(
        '',
        (r'^', include('protected_downloads.download.urls')),
        (r'^admin/', include(admin.site.urls)),
        )
