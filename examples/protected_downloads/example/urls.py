from django.conf.urls import url, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^', include('download.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
