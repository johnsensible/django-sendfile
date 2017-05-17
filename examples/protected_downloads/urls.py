from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^', include('protected_downloads.download.urls')),
    url(r'^admin/', admin.site.urls),
]
